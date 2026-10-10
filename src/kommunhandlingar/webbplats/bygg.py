"""Krav: K14 och K18 i docs/02-KRAV.md. Test: tests/test_webbplats.py,
tests/test_webbplats_dokument.py.
"""

import shutil
from datetime import datetime
from pathlib import Path

from kommunhandlingar import frontmatter, konfiguration
from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats import sidor
from kommunhandlingar.webbplats.dokumentsida import dokumentsida
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.organsida import organsida
from kommunhandlingar.webbplats.rakning import okanda, rakna


def bygg(rot: Path, ut: Path, repo: str, byggd: datetime) -> None:
    kommuner = [konfiguration.las(f) for f in sorted((rot / "kommuner").glob("*.toml"))]
    mall = Mall(kommuner, repo, byggd)
    ut.mkdir(parents=True, exist_ok=True)
    (ut / "index.html").write_text(sidor.startsida(mall), encoding="utf-8")
    for kommun in kommuner:
        bygg_kommun(rot / "data" / kommun.id, ut, mall, kommun)


# Varje dokuments sida skrivs när det läses, så att poolens text inte hålls
# i minnet.
def bygg_kommun(katalog: Path, ut: Path, mall: Mall, kommun: Kommun) -> None:
    (ut / kommun.id).mkdir(exist_ok=True)
    dokument = []
    for fil in sorted(katalog.rglob("*.md")):
        falt, text = las_dokument(fil, katalog, kommun)
        html = dokumentsida(mall, kommun, falt, text)
        skriv_dokument(fil, ut / kommun.id / falt["adress"], html)
        dokument.append(falt)
    html = sidor.statussida(mall, kommun, dokument)
    (ut / f"{kommun.id}.html").write_text(html, encoding="utf-8")
    for rad in rakna(kommun, dokument, mall.byggd.date()):
        organets = [d for d in dokument if d["organ"] == rad.id]
        html = organsida(mall, kommun, rad, organets)
        (ut / kommun.id / f"{rad.id}.html").write_text(html, encoding="utf-8")


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
