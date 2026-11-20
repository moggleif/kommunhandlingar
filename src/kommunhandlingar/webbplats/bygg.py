"""Krav: K14, K18, K22, K26, K28, K36, K37, K39, K46, K47, K48, K54, K56, K58, K60 och
K62 i docs/02-KRAV.md.
Test: tests/test_webbplats.py, tests/test_projekt.py,
tests/test_webbplats_dokument.py, tests/test_kalender.py, tests/test_mal.py,
tests/test_uppfoljningar.py, tests/test_lokalbehov.py, tests/test_initiativ.py,
tests/test_dokumentindex.py, tests/test_paragrafindex.py,
tests/test_sammantradessida.py, tests/test_sokindex.py.
"""

import shutil
from dataclasses import replace
from datetime import datetime
from functools import partial
from pathlib import Path

from kommunhandlingar import frontmatter, konfiguration
from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats import (
    dokumentindex,
    kalender,
    mal,
    paragrafindex,
    projekt,
    sammantradesbygge,
    sidor,
    sokindex,
    spar,
    uppfoljningar,
)
from kommunhandlingar.webbplats.arspann import arspann, poolens_ar, radernas_ar
from kommunhandlingar.webbplats.dokumentsida import dokumentsida
from kommunhandlingar.webbplats.kalendersida import kalendersida
from kommunhandlingar.webbplats.llms import llms
from kommunhandlingar.webbplats.mall import Mall, sida
from kommunhandlingar.webbplats.malsida import adress as malsidans_adress
from kommunhandlingar.webbplats.malsida import malsida
from kommunhandlingar.webbplats.meny import oversiktsnamn, statusadress
from kommunhandlingar.webbplats.organsida import organsida
from kommunhandlingar.webbplats.oversikt import adresser, oversikt
from kommunhandlingar.webbplats.rakning import okanda, rakna
from kommunhandlingar.webbplats.slagen import SLAGEN
from kommunhandlingar.webbplats.sparkort import Vy
from kommunhandlingar.webbplats.sparsida import adress as sparets_adress
from kommunhandlingar.webbplats.sparsida import sparsida
from kommunhandlingar.webbplats.sparslag import DETALJPLANER


def bygg(rot: Path, ut: Path, repo: str, byggd: datetime) -> Mall:
    kommuner = [konfiguration.las(f) for f in sorted((rot / "kommuner").glob("*.toml"))]
    kalendrar = kommunfiler(rot / "kalender", kommuner)
    malen = las_kommunfiler(rot, "mal", kommuner, mal.las)
    uppfoljda = las_kommunfiler(rot, "uppfoljningar", kommuner, uppfoljningar.las)
    sparen = {
        s.id: las_kommunfiler(rot, s.id, kommuner, partial(spar.las, slag=s))
        for s in SLAGEN
    }
    projekten = las_projekten(rot, kommuner, sparen[DETALJPLANER.id])
    aren = kommunernas_ar(rot, kommuner, byggd, (malen, uppfoljda, sparen))
    mall = Mall(
        kommuner, repo, byggd, kalendrar, malen, uppfoljda, sparen, projekten, aren
    )
    ut.mkdir(parents=True, exist_ok=True)
    if not mall.en_kommun:
        (ut / "index.html").write_text(sidor.startsida(mall), encoding="utf-8")
    (ut / "llms.txt").write_text(llms(mall), encoding="utf-8")
    sokgrupper = []
    for kommun in kommuner:
        sokgrupper.append(bygg_kommun(rot / "data" / kommun.id, ut, mall, kommun))
        bygg_kalender(rot, ut, mall, kommun)
    sokindex.skriv(ut, sokgrupper)
    return mall


# Varje dokuments sida skrivs när det läses, så att poolens text inte hålls
# i minnet. Kommunens grupp i sökindexet lämnas tillbaka.
def bygg_kommun(katalog: Path, ut: Path, mall: Mall, kommun: Kommun) -> dict:
    (ut / kommun.id).mkdir(exist_ok=True)
    dokument, stycken = [], []
    for fil in sorted(katalog.rglob("*.md")):
        falt, text = las_dokument(fil, katalog, kommun)
        html = dokumentsida(mall, kommun, falt, text)
        skriv_dokument(fil, ut / kommun.id / falt["adress"], html)
        dokument.append(falt)
        stycken += paragrafindex.av_dokument(falt, text, katalog)
    dokumentindex.skriv(ut, dokument, katalog)
    paragrafindex.skriv(ut, stycken, katalog)
    underlag = sammantradesbygge.underlag(mall, katalog, kommun, (dokument, stycken))
    sammantradesbygge.bygg(ut, mall, underlag)
    html = sidor.statussida(mall, kommun, dokument)
    (ut / statusadress(kommun.id)).write_text(html, encoding="utf-8")
    bygg_oversikten(ut, mall, kommun, dokument)
    bygg_organen(ut, mall, kommun, dokument)
    return sokindex.grupp(kommun, underlag.paragrafer)


def bygg_oversikten(ut: Path, mall: Mall, kommun: Kommun, dokument: list[dict]) -> None:
    rader = rakna(kommun, dokument, mall.byggd.date())
    innehall = oversikt(mall, kommun, rader, dokument)
    for adress in adresser(mall, kommun):
        html = sida(mall, adress, oversiktsnamn(mall.kommuner, kommun), innehall)
        (ut / adress).write_text(html, encoding="utf-8")


def bygg_organen(ut: Path, mall: Mall, kommun: Kommun, dokument: list[dict]) -> None:
    for rad in rakna(kommun, dokument, mall.byggd.date()):
        organets = [d for d in dokument if d["organ"] == rad.id]
        html = organsida(mall, kommun, rad, organets)
        (ut / kommun.id / f"{rad.id}.html").write_text(html, encoding="utf-8")
        if malen := [m for m in mall.malen.get(kommun.id, []) if m.organ == rad.id]:
            html = malsida(mall, kommun, malen, organets)
            (ut / malsidans_adress(kommun, rad.id)).write_text(html, encoding="utf-8")
        bygg_sparen(ut, mall, kommun, rad.id)


def bygg_sparen(ut: Path, mall: Mall, kommun: Kommun, organ: str) -> None:
    for slag in SLAGEN:
        alla = mall.spar[slag.id].get(kommun.id, [])
        if stegen := [s for s in alla if s.organ == organ]:
            vy = Vy(slag, kommun, mall.aren[kommun.id])
            if slag == DETALJPLANER:
                vy = replace(vy, projekt=mall.projekt.get(kommun.id, {}))
            html = sparsida(mall, vy, stegen)
            adress = sparets_adress(kommun, organ, slag)
            (ut / adress).write_text(html, encoding="utf-8")


# Målen, uppföljningarna och spåren per kommun, som Mall har dem (K60).
def kommunernas_ar(rot: Path, kommuner: list, byggd: datetime, filer: tuple) -> dict:
    return {
        k.id: arspann(
            [*poolens_ar(rot / "data" / k.id), *radernas_ar(k.id, *filer), byggd.year]
        )
        for k in kommuner
    }


def las_projekten(rot: Path, kommuner: list[Kommun], planerna: dict) -> dict:
    projekten = las_kommunfiler(rot, "projekt", kommuner, projekt.las)
    for kommun, kopplade in projekten.items():
        fil = f"projekt/{kommun}.csv"
        projekt.kontrollera(kopplade, planerna.get(kommun, []), fil)
    return projekten


def kommunfiler(katalog: Path, kommuner: list[Kommun]) -> frozenset[str]:
    filer = frozenset(f.stem for f in katalog.glob("*.csv"))
    if utan_kommun := filer - {k.id for k in kommuner}:
        raise Datafel(f"{katalog.name}/{min(utan_kommun)}.csv har ingen kommunfil")
    return filer


def las_kommunfiler(rot: Path, katalog: str, kommuner: list[Kommun], las) -> dict:
    filer = kommunfiler(rot / katalog, kommuner)
    return {
        k.id: las(rot / katalog / f"{k.id}.csv", k, rot / "data" / k.id)
        for k in kommuner
        if k.id in filer
    }


def bygg_kalender(rot: Path, ut: Path, mall: Mall, kommun: Kommun) -> None:
    if kommun.id in mall.kalendrar:
        fil = rot / "kalender" / f"{kommun.id}.csv"
        sammantraden = kalender.las(fil, kommun, rot / "data" / kommun.id)
        sammantraden = kalender.med_sidor(sammantraden, ut / kommun.id)
        html = kalendersida(mall, kommun, sammantraden)
        (ut / kommun.id / "kalender.html").write_text(html, encoding="utf-8")


def las_dokument(fil: Path, katalog: Path, kommun: Kommun) -> tuple[dict, str]:
    text = fil.read_text(encoding="utf-8")
    falt = frontmatter.las(text)
    if fel := okanda(falt, kommun):
        raise Datafel(f"{fil}: okänt {', '.join(fel)}")
    falt["adress"] = fil.relative_to(katalog).with_suffix(".html").as_posix()
    return falt, text


def skriv_dokument(fil: Path, sidfil: Path, html: str) -> None:
    sidfil.parent.mkdir(parents=True, exist_ok=True)
    sidfil.write_text(html, encoding="utf-8")
    if (tabeller := fil.with_suffix(".tabeller")).is_dir():
        shutil.copytree(tabeller, sidfil.with_suffix(".tabeller"), dirs_exist_ok=True)
