"""Krav: K4, K6, K8 och K9 i docs/02-KRAV.md, ADR-0003 och ADR-0004.
Test: tests/test_hamta.py.

Steg 2 för en kandidat: hoppa över det som redan finns, annars hämta,
konvertera och skriv. Ett misslyckat försök skriver aldrig över en
fullständig `.md`. K8:s regel om äldre ögonblicksbilder väntar på
Wayback-adaptern. Skrivningen avbryts aldrig av tidsgränsen (K11).
"""

import hashlib
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path, PurePosixPath

from kommunhandlingar import frontmatter, skrivning
from kommunhandlingar.fel import Hamtfel
from kommunhandlingar.kandidat import Kandidat
from kommunhandlingar.konvertering.dokument import Resultat, konvertera, versioner
from kommunhandlingar.plats import Plats, ledigt_namn, namn_av
from kommunhandlingar.pool import Pool
from kommunhandlingar.tidsbudget import utan_avbrott


@dataclass(frozen=True)
class Steg2:
    data: Path
    kommun: str
    pool: Pool
    klient: object  # har fil(url, mal), som hamtning.klient.Klient
    nycklar: frozenset[str]
    tid: Callable[[], datetime]
    version: str


@dataclass(frozen=True)
class Dokument:
    kandidat: Kandidat
    sokvag: PurePosixPath
    befintlig: dict[str, str] | None
    namn: str | None = None


def behandla(steg: Steg2, kandidat: Kandidat) -> str:
    if kandidat.kallnyckel in steg.pool.tidigare:
        return "tidigare källnyckel"
    sokvag = steg.pool.efter_nyckel.get(kandidat.kallnyckel)
    if sokvag is None:
        dokument = placera(steg, kandidat)
    else:
        dokument = Dokument(kandidat, sokvag, steg.pool.efter_sokvag[sokvag])
    gammal = dokument.befintlig
    if sokvag and gammal["kalla_url"] == kandidat.url and hel(gammal):
        return "oförändrad"
    with tempfile.TemporaryDirectory() as katalog:
        pdf = Path(katalog) / "original.pdf"
        hamtad = steg.tid()
        try:
            steg.klient.fil(kandidat.url, pdf)
        except Hamtfel as fel:
            return misslyckad(steg, dokument, fel.orsak, hamtad)
        return hamtad_fil(steg, dokument, pdf, hamtad)


def hel(falt: dict[str, str]) -> bool:
    return falt["kvalitet"] != "ej-hamtad"


def placera(steg: Steg2, kandidat: Kandidat) -> Dokument:
    namn = namn_av(kandidat.filnamn.removesuffix(".pdf").removesuffix(".PDF"))
    plats = Plats(kandidat.organ, kandidat.datum, kandidat.typ)
    if kandidat.typ == "bilaga":
        plats = replace(plats, namn=namn or "2")
    sokvag = plats.sokvag(steg.kommun)
    upptagen = steg.pool.efter_sokvag.get(sokvag)
    if upptagen is None:
        return Dokument(kandidat, sokvag, None, plats.namn)
    if upptagen["kallnyckel"] not in steg.nycklar:
        return Dokument(kandidat, sokvag, upptagen)

    def finns(forslag: str) -> bool:
        return (
            replace(plats, namn=forslag).sokvag(steg.kommun) in steg.pool.efter_sokvag
        )

    plats = replace(plats, namn=ledigt_namn(namn, finns))
    return Dokument(kandidat, plats.sokvag(steg.kommun), None, plats.namn)


def misslyckad(steg: Steg2, dokument: Dokument, orsak: str, hamtad: datetime) -> str:
    gammal = dokument.befintlig
    if gammal and hel(gammal):
        return f"ej hämtad ({orsak}), fullständig .md orörd"
    adress = dokument.kandidat.url
    if gammal and (gammal["fel"], gammal["kalla_url"]) == (orsak, adress):
        return f"ej hämtad ({orsak}), oförändrad"
    falt = grundfalt(steg, dokument) | {
        "hamtad": gammal["hamtad"] if gammal else hamtad.isoformat(),
        "pipeline": steg.version,
        "kvalitet": "ej-hamtad",
        "fel": orsak,
    }
    spara(steg, dokument.sokvag, frontmatter.skriv(falt), {})
    return f"ej hämtad ({orsak})"


def hamtad_fil(steg: Steg2, dokument: Dokument, pdf: Path, hamtad: datetime) -> str:
    with pdf.open("rb") as fil:
        sha256 = hashlib.file_digest(fil, "sha256").hexdigest()
    gammal = dokument.befintlig
    if gammal and (gammal["kallnyckel"], gammal["sha256"]) == (
        dokument.kandidat.kallnyckel,
        sha256,
    ):
        return ny_adress(steg, dokument)
    resultat = konvertera(pdf)
    falt = grundfalt(steg, dokument) | kvalitetsfalt(steg, resultat)
    falt |= {"sha256": sha256, "bytes": pdf.stat().st_size}
    falt |= {"hamtad": hamtad.isoformat(), "konverterad": steg.tid().isoformat()}
    md = steg.data / dokument.sokvag
    text = frontmatter.skriv(falt)
    if resultat.sidor:
        katalog = skrivning.tabellkatalog(md).name
        text += "\n" + skrivning.brodtext(resultat.sidor, katalog)
    spara(steg, dokument.sokvag, text, skrivning.tabellfiler(resultat.sidor or []))
    return "konverterad"


def kvalitetsfalt(steg: Steg2, resultat: Resultat) -> dict:
    return {
        "sidor": len(resultat.sidor) if resultat.sidor else None,
        "pipeline": " / ".join([steg.version, *versioner(resultat)]),
        "kvalitet": resultat.kvalitet,
        "fel": resultat.fel,
        "kvalitet_per_sida": resultat.kvalitet_per_sida,
        "tal_obekraftade": resultat.tal_obekraftade,
        "figurer": resultat.figurer,
        "tolkade": None if resultat.figurer is None else [],
    }


def ny_adress(steg: Steg2, dokument: Dokument) -> str:
    md = steg.data / dokument.sokvag
    _, huvud, kropp = md.read_text(encoding="utf-8").split("---\n", 2)
    falt = frontmatter.las(f"---\n{huvud}---\n") | {"kalla_url": dokument.kandidat.url}
    text = frontmatter.skriv(falt) + kropp
    with utan_avbrott():
        skrivning.skriv_md(md, text)
    steg.pool.satt(dokument.sokvag, frontmatter.las(text))
    return "ny adress, samma innehåll"


def grundfalt(steg: Steg2, dokument: Dokument) -> dict:
    return (
        dict.fromkeys(frontmatter.FALT)
        | platsfalt(dokument)
        | {
            "kommun": steg.kommun,
            "kallnyckel": dokument.kandidat.kallnyckel,
            "tidigare_kallnycklar": tidigare(dokument),
            "kalla_url": dokument.kandidat.url,
        }
    )


def platsfalt(dokument: Dokument) -> dict:
    gammal = dokument.befintlig
    if gammal:
        return {f: gammal[f] for f in ("organ", "datum", "lopnr", "typ", "namn")}
    k = dokument.kandidat
    return {"organ": k.organ, "datum": k.datum, "typ": k.typ, "namn": dokument.namn}


def tidigare(dokument: Dokument) -> list[str]:
    gammal = dokument.befintlig
    if not gammal:
        return []
    nycklar = frontmatter.lista(gammal["tidigare_kallnycklar"])
    if gammal["kallnyckel"] != dokument.kandidat.kallnyckel:
        nycklar.append(gammal["kallnyckel"])
    return nycklar


def spara(steg: Steg2, sokvag: PurePosixPath, text: str, tabeller: dict) -> None:
    with utan_avbrott():
        skrivning.skriv(steg.data / sokvag, text, tabeller)
    steg.pool.satt(sokvag, frontmatter.las(text))
