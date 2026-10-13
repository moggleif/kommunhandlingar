"""Krav: K16 och K23 i docs/02-KRAV.md, ADR-0018 och ADR-0039.
Test: tests/test_hamta_arkiv.py och tests/test_plattformar.py.

Vilka luckor en kandidat ur arkivet får fylla. Plattformen är källnyckelns
första del, till exempel `sitevision` eller `episerver`.
"""

from kommunhandlingar.adaptrar import wayback
from kommunhandlingar.kandidat import Kandidat
from kommunhandlingar.plats import grundplats
from kommunhandlingar.pool import Pool


def hel(falt: dict[str, str]) -> bool:
    return falt["kvalitet"] != "ej-hamtad"


def ingen_lucka(pool: Pool, kommun: str, kandidat: Kandidat, gammal) -> bool:
    """Arkivet tar inte en källnyckel med ett fullständigt dokument, ett
    sammanträde som har typen från en annan plattform, en plats med ett
    dokument från en levande källa, eller en plats vars dokument ur arkivet
    har en källnyckel som inte står i listan (`placera` ger det), utom ett
    försök från en annan plattform."""
    if kandidat.kallnyckel in pool.efter_nyckel:
        return hel(gammal)
    if typen_finns(pool, kandidat):
        return True
    upptagen = pool.efter_sokvag.get(grundplats(kandidat).sokvag(kommun))
    levande = upptagen is not None and not wayback.ar_kopia(upptagen["kalla_url"])
    return levande or (gammal is not None and not tas_over(gammal, kandidat))


def plattform(kallnyckel: str) -> str:
    return kallnyckel.split(":", 1)[0]


def tas_over(falt: dict[str, str], kandidat: Kandidat) -> bool:
    """Ett försök från en annan plattform ger plats åt kandidaten."""
    annan = plattform(falt["kallnyckel"]) != plattform(kandidat.kallnyckel)
    return annan and not hel(falt)


def typen_finns(pool: Pool, kandidat: Kandidat) -> bool:
    """Sammanträdet har ett fullständigt dokument av typen från en annan
    plattform."""
    motet = (kandidat.organ, kandidat.datum.isoformat(), kandidat.typ)
    return any(
        (falt["organ"], falt["datum"], falt["typ"]) == motet
        and hel(falt)
        and plattform(falt["kallnyckel"]) != plattform(kandidat.kallnyckel)
        for falt in pool.efter_sokvag.values()
    )
