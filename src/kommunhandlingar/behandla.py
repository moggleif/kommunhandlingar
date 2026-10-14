"""Krav: K4, K6, K8, K9, K16, K23 och K30 i docs/02-KRAV.md, ADR-0003,
ADR-0004, ADR-0018, ADR-0019, ADR-0039 och ADR-0048. Test: tests/test_hamta.py,
tests/test_omkonvertering.py och tests/test_plattformar.py.

Steg 2 för en kandidat: hoppa över det som redan finns, annars hämta,
konvertera och skriv. Ett misslyckat försök skriver aldrig över en
fullständig `.md`. En kandidat ur ett arkiv fyller bara luckor, så att en
äldre kopia aldrig ersätter ett dokument i poolen; har sammanträdet typen
från en annan plattform står den med högst kvalitet kvar. Med omkonverteringen
påslagen räknas ett dokument från en annan version av poolen inte som
befintligt. Skrivningen avbryts aldrig av tidsgränsen (K11).
"""

import tempfile
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path, PurePosixPath

from kommunhandlingar import frontmatter, original, skrivning
from kommunhandlingar.arkivluckor import (
    forlorar,
    hel,
    ingen_lucka,
    levande,
    motstandare,
    tas_over,
)
from kommunhandlingar.fel import Hamtfel
from kommunhandlingar.kandidat import Kandidat
from kommunhandlingar.konvertering.dokument import Resultat, konvertera, versioner
from kommunhandlingar.plats import filnamnet, grundplats, ledigt_namn
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
    arkiv: bool = False
    omkonvertera: bool = False
    ensamma: frozenset[str] = frozenset()  # arkivluckor.ensamma


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
    rival = motstandare_for(steg, kandidat) if sokvag is None else None
    if rival:
        dokument = Dokument(kandidat, rival, steg.pool.efter_sokvag[rival])
    elif sokvag is None:
        dokument = placera(steg, kandidat)
    else:
        dokument = Dokument(kandidat, sokvag, steg.pool.efter_sokvag[sokvag])
    gammal = dokument.befintlig
    luckor = steg.arkiv and not rival
    if luckor and ingen_lucka(steg.pool, steg.kommun, kandidat, gammal):
        return "finns redan; arkivet fyller bara luckor"
    if sokvag and samma_kalla(gammal, kandidat) and aktuell(steg, gammal):
        return "oförändrad"
    with tempfile.TemporaryDirectory() as katalog:
        pdf = Path(katalog) / "original.pdf"
        hamtad = steg.tid()
        try:
            hamtat = original.hamta(steg.klient, kandidat.adresser(), pdf, steg.arkiv)
        except Hamtfel as fel:
            return misslyckad(steg, dokument, fel.orsak, hamtad)
        return hamtad_fil(steg, dokument, hamtat, hamtad)


def motstandare_for(steg: Steg2, kandidat: Kandidat) -> PurePosixPath | None:
    if not steg.arkiv or kandidat.kallnyckel not in steg.ensamma:
        return None
    return motstandare(steg.pool, steg.kommun, kandidat)


def samma_kalla(falt: dict[str, str], kandidat: Kandidat) -> bool:
    return falt["kalla_url"] == frontmatter.varde_av(kandidat.kalla_url()) and hel(falt)


def aktuell(steg: Steg2, falt: dict[str, str]) -> bool:
    if not steg.omkonvertera:
        return True
    return falt["pipeline"].split(" / ")[0] == steg.version


def bara_omkonvertering(steg: Steg2, kandidat: Kandidat) -> bool:
    sokvag = steg.pool.efter_nyckel.get(kandidat.kallnyckel)
    gammal = steg.pool.efter_sokvag[sokvag] if sokvag else None
    return bool(gammal) and samma_kalla(gammal, kandidat) and not aktuell(steg, gammal)


def placera(steg: Steg2, kandidat: Kandidat) -> Dokument:
    plats = grundplats(kandidat)
    sokvag = plats.sokvag(steg.kommun)
    upptagen = steg.pool.efter_sokvag.get(sokvag)
    if upptagen is None:
        return Dokument(kandidat, sokvag, None, plats.namn)
    if upptagen["kallnyckel"] not in steg.nycklar or tas_over(upptagen, kandidat):
        return Dokument(kandidat, sokvag, upptagen)

    def finns(forslag: str) -> bool:
        return (
            replace(plats, namn=forslag).sokvag(steg.kommun) in steg.pool.efter_sokvag
        )

    plats = replace(plats, namn=ledigt_namn(filnamnet(kandidat), finns))
    return Dokument(kandidat, plats.sokvag(steg.kommun), None, plats.namn)


def misslyckad(steg: Steg2, dokument: Dokument, orsak: str, hamtad: datetime) -> str:
    gammal = dokument.befintlig
    if gammal and hel(gammal):
        return f"ej hämtad ({orsak}), fullständig .md orörd"
    adress = frontmatter.varde_av(dokument.kandidat.kalla_url())
    if gammal and (gammal["fel"], gammal["kalla_url"]) == (orsak, adress):
        return f"ej hämtad ({orsak}), oförändrad"
    if steg.arkiv and gammal and levande(gammal):
        # Annars skriver den levande källan och arkivet om filen varannan gång.
        return f"ej hämtad ({orsak}), den levande källans försök orört"
    falt = grundfalt(steg, dokument) | {
        "hamtad": gammal["hamtad"] if gammal else hamtad.isoformat(),
        "pipeline": steg.version,
        "kvalitet": "ej-hamtad",
        "fel": orsak,
    }
    spara(steg, dokument.sokvag, frontmatter.skriv(falt), {})
    return f"ej hämtad ({orsak})"


def hamtad_fil(
    steg: Steg2, dokument: Dokument, hamtat: original.Original, hamtad: datetime
) -> str:
    gammal = dokument.befintlig
    samma_fil = gammal is not None and (gammal["kallnyckel"], gammal["sha256"]) == (
        dokument.kandidat.kallnyckel,
        frontmatter.varde_av(hamtat.sha256),
    )
    if samma_fil and aktuell(steg, gammal):
        return ny_adress(steg, dokument)
    resultat = (
        Resultat("ej-konverterad", hamtat.fel) if hamtat.fel else konvertera(hamtat.pdf)
    )
    if steg.arkiv and forlorar(gammal, dokument.kandidat, resultat.kvalitet):
        return behall(steg, dokument)
    falt = grundfalt(steg, dokument) | kvalitetsfalt(steg, resultat)
    falt |= {"sha256": hamtat.sha256, "bytes": hamtat.bytes}
    falt |= {"hamtad": hamtad.isoformat(), "konverterad": steg.tid().isoformat()}
    md = steg.data / dokument.sokvag
    text = frontmatter.skriv(falt)
    if resultat.sidor:
        katalog = skrivning.tabellkatalog(md).name
        text += "\n" + skrivning.brodtext(resultat.sidor, katalog)
    spara(steg, dokument.sokvag, text, skrivning.tabellfiler(resultat.sidor or []))
    return "konverterad om" if samma_fil else "konverterad"


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
    andra_falt(steg, dokument.sokvag, {"kalla_url": dokument.kandidat.kalla_url()})
    return "ny adress, samma innehåll"


def behall(steg: Steg2, dokument: Dokument) -> str:
    """Kandidaten blir en tidigare källnyckel, så att den inte hämtas igen."""
    nycklar = frontmatter.lista(dokument.befintlig["tidigare_kallnycklar"])
    nycklar.append(dokument.kandidat.kallnyckel)
    andra_falt(steg, dokument.sokvag, {"tidigare_kallnycklar": nycklar})
    return "lika eller lägre kvalitet; det befintliga behålls"


def andra_falt(steg: Steg2, sokvag: PurePosixPath, nya: dict) -> None:
    md = steg.data / sokvag
    _, huvud, kropp = md.read_text(encoding="utf-8").split("---\n", 2)
    falt = frontmatter.las(f"---\n{huvud}---\n") | nya
    text = frontmatter.skriv(falt) + kropp
    with utan_avbrott():
        skrivning.skriv_md(md, text)
    steg.pool.satt(sokvag, frontmatter.las(text))


def grundfalt(steg: Steg2, dokument: Dokument) -> dict:
    return (
        dict.fromkeys(frontmatter.FALT)
        | platsfalt(dokument)
        | {
            "kommun": steg.kommun,
            "kallnyckel": dokument.kandidat.kallnyckel,
            "tidigare_kallnycklar": tidigare(dokument),
            "kalla_url": dokument.kandidat.kalla_url(),
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
