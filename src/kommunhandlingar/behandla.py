"""Krav: K4, K6, K8 och K9 i docs/02-KRAV.md, ADR-0003 och ADR-0004.
Test: tests/test_hamta.py.

Steg 2 för en kandidat: hoppa över det som redan finns, annars hämta,
konvertera och skriv. Ett misslyckat försök skriver aldrig över en
fullständig `.md`.
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


@dataclass(frozen=True)
class Steg2:
    data: Path
    kommun: str
    pool: Pool
    klient: object
    nycklar: frozenset[str]
    tid: Callable[[], datetime]
    version: str


def behandla(steg: Steg2, kandidat: Kandidat) -> str:
    if kandidat.kallnyckel in steg.pool.tidigare:
        return "tidigare källnyckel"
    sokvag = steg.pool.efter_nyckel.get(kandidat.kallnyckel)
    befintlig = steg.pool.efter_sokvag.get(sokvag) if sokvag else None
    if befintlig and befintlig["kalla_url"] == kandidat.url and hel(befintlig):
        return "oförändrad"
    if sokvag is None:
        sokvag, befintlig = placera(steg, kandidat)
    with tempfile.TemporaryDirectory() as katalog:
        pdf = Path(katalog) / "original.pdf"
        hamtad = steg.tid()
        try:
            steg.klient.fil(kandidat.url, pdf)
        except Hamtfel as fel:
            return misslyckad(steg, Doc(kandidat, sokvag, befintlig), fel.orsak, hamtad)
        return hamtad_fil(steg, Doc(kandidat, sokvag, befintlig), pdf, hamtad)


@dataclass(frozen=True)
class Doc:
    kandidat: Kandidat
    sokvag: PurePosixPath
    befintlig: dict[str, str] | None


def hel(falt: dict[str, str]) -> bool:
    return falt["kvalitet"] != "ej-hamtad"


def placera(steg: Steg2, kandidat: Kandidat) -> tuple[PurePosixPath, dict | None]:
    namn = namn_av(kandidat.filnamn.removesuffix(".pdf").removesuffix(".PDF"))
    plats = Plats(kandidat.organ, kandidat.datum, kandidat.typ)
    if kandidat.typ == "bilaga":
        plats = replace(plats, namn=ledigt_namn(namn, lambda _: False))
    upptagen = steg.pool.efter_sokvag.get(plats.sokvag(steg.kommun))
    if upptagen is None:
        return plats.sokvag(steg.kommun), None
    if upptagen["kallnyckel"] not in steg.nycklar:
        return plats.sokvag(steg.kommun), upptagen

    def finns(forslag: str) -> bool:
        return (
            replace(plats, namn=forslag).sokvag(steg.kommun) in steg.pool.efter_sokvag
        )

    return replace(plats, namn=ledigt_namn(namn, finns)).sokvag(steg.kommun), None


def misslyckad(steg: Steg2, doc: Doc, orsak: str, hamtad: datetime) -> str:
    gammal = doc.befintlig
    if gammal and hel(gammal):
        return "ej hämtad, fullständig .md orörd"
    if gammal and (gammal["fel"], gammal["kalla_url"]) == (orsak, doc.kandidat.url):
        return "ej hämtad, oförändrad"
    forsta = gammal["hamtad"] if gammal else hamtad.isoformat()
    falt = grundfalt(steg, doc) | {
        "hamtad": forsta,
        "pipeline": steg.version,
        "kvalitet": "ej-hamtad",
        "fel": orsak,
    }
    spara(steg, doc.sokvag, frontmatter.skriv(falt), {})
    return f"ej hämtad ({orsak})"


def hamtad_fil(steg: Steg2, doc: Doc, pdf: Path, hamtad: datetime) -> str:
    with pdf.open("rb") as fil:
        sha256 = hashlib.file_digest(fil, "sha256").hexdigest()
    gammal = doc.befintlig
    if (
        gammal
        and gammal["kallnyckel"] == doc.kandidat.kallnyckel
        and gammal["sha256"] == sha256
    ):
        return ny_adress(steg, doc)
    resultat = konvertera(pdf)
    falt = (
        grundfalt(steg, doc)
        | {
            "sha256": sha256,
            "bytes": pdf.stat().st_size,
            "hamtad": hamtad.isoformat(),
            "konverterad": steg.tid().isoformat(),
        }
        | kvalitetsfalt(steg, resultat)
    )
    md = steg.data / doc.sokvag
    katalog = skrivning.tabellkatalog(md).name
    text = frontmatter.skriv(falt)
    if resultat.sidor:
        text += "\n" + skrivning.brodtext(resultat.sidor, katalog)
    spara(steg, doc.sokvag, text, skrivning.tabellfiler(resultat.sidor or []))
    return "konverterad"


def kvalitetsfalt(steg: Steg2, resultat: Resultat) -> dict:
    return {
        "sidor": len(resultat.sidor) if resultat.sidor else None,
        "pipeline": " / ".join([steg.version, *versioner(resultat.verktyg)]),
        "kvalitet": resultat.kvalitet,
        "fel": resultat.fel,
        "kvalitet_per_sida": resultat.kvalitet_per_sida,
        "tal_obekraftade": resultat.tal_obekraftade,
    }


def ny_adress(steg: Steg2, doc: Doc) -> str:
    md = steg.data / doc.sokvag
    _, huvud, kropp = md.read_text(encoding="utf-8").split("---\n", 2)
    falt = frontmatter.las(f"---\n{huvud}---\n") | {"kalla_url": doc.kandidat.url}
    spara(steg, doc.sokvag, frontmatter.skriv(falt) + kropp, None)
    return "ny adress, samma innehåll"


def grundfalt(steg: Steg2, doc: Doc) -> dict:
    return (
        dict.fromkeys(frontmatter.FALT)
        | platsfalt(doc)
        | {
            "kommun": steg.kommun,
            "kallnyckel": doc.kandidat.kallnyckel,
            "tidigare_kallnycklar": tidigare(doc),
            "kalla_url": doc.kandidat.url,
        }
    )


def platsfalt(doc: Doc) -> dict:
    if doc.befintlig:
        return {f: doc.befintlig[f] for f in ("organ", "datum", "lopnr", "typ", "namn")}
    k = doc.kandidat
    namn = namn_i(doc.sokvag, k.typ)
    return {"organ": k.organ, "datum": k.datum, "typ": k.typ, "namn": namn}


def tidigare(doc: Doc) -> list[str]:
    gammal = doc.befintlig
    if not gammal:
        return []
    nycklar = frontmatter.lista(gammal["tidigare_kallnycklar"])
    if gammal["kallnyckel"] != doc.kandidat.kallnyckel:
        nycklar.append(gammal["kallnyckel"])
    return nycklar


def namn_i(sokvag: PurePosixPath, typ: str) -> str | None:
    namn = sokvag.stem.removeprefix(typ).removeprefix("-")
    return namn or None


def spara(steg: Steg2, sokvag: PurePosixPath, text: str, tabeller: dict | None) -> None:
    md = steg.data / sokvag
    if tabeller is None:
        skrivning.skriv_md(md, text)
    else:
        skrivning.skriv(md, text, tabeller)
    steg.pool.satt(sokvag, frontmatter.las(text))
