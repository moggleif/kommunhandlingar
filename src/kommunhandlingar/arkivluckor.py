"""Krav: K16, K23 och K30 i docs/02-KRAV.md, ADR-0018, ADR-0039 och ADR-0048.
Test: tests/test_hamta_arkiv.py och tests/test_plattformar.py.

Vilka luckor en kandidat ur arkivet får fylla, och vilken av två plattformar
som får ett sammanträdes typ. Plattformen är källnyckelns första del, till
exempel `sitevision` eller `episerver`.
"""

from collections import Counter
from pathlib import PurePosixPath

from kommunhandlingar.adaptrar import wayback
from kommunhandlingar.frontmatter import lista
from kommunhandlingar.kandidat import Kandidat
from kommunhandlingar.konvertering.kvalitet import KVALITETER
from kommunhandlingar.plats import grundplats
from kommunhandlingar.pool import Pool


def hel(falt: dict[str, str]) -> bool:
    return falt["kvalitet"] != "ej-hamtad"


def ingen_lucka(pool: Pool, kommun: str, kandidat: Kandidat, gammal) -> bool:
    """Arkivet tar inte en källnyckel med ett fullständigt dokument, ett
    sammanträde som har typen från en annan plattform, en plats med ett
    dokument från en levande källa, eller en plats vars dokument ur arkivet
    har en källnyckel som inte står i listan (`placera` ger det), utom ett
    försök från en annan plattform. `motstandare` prövas före."""
    if kandidat.kallnyckel in pool.efter_nyckel:
        return hel(gammal)
    if typen_finns(pool, kandidat):
        return True
    upptagen = pool.efter_sokvag.get(grundplats(kandidat).sokvag(kommun))
    return levande(upptagen) or (gammal is not None and not tas_over(gammal, kandidat))


def levande(falt: dict[str, str] | None) -> bool:
    return falt is not None and not wayback.ar_kopia(falt["kalla_url"])


def plattform(kallnyckel: str) -> str:
    return kallnyckel.split(":", 1)[0]


def annan_plattform(falt: dict[str, str], kandidat: Kandidat) -> bool:
    return plattform(falt["kallnyckel"]) != plattform(kandidat.kallnyckel)


def tas_over(falt: dict[str, str], kandidat: Kandidat) -> bool:
    """Ett försök från en annan plattform ger plats åt kandidaten."""
    return annan_plattform(falt, kandidat) and not hel(falt)


def provas_mot(falt: dict[str, str] | None, kandidat: Kandidat) -> bool:
    """Ett fullständigt dokument från en annan plattform, som kandidaten
    jämförs med (`motstandare` ger det)."""
    return falt is not None and hel(falt) and annan_plattform(falt, kandidat)


def typen_finns(pool: Pool, kandidat: Kandidat) -> bool:
    """Sammanträdet har ett fullständigt dokument av typen från en annan
    plattform."""
    return any(
        samma_mote(falt, kandidat) and provas_mot(falt, kandidat)
        for falt in pool.efter_sokvag.values()
    )


def samma_mote(falt: dict[str, str], kandidat: Kandidat) -> bool:
    motet = (kandidat.organ, kandidat.datum.isoformat(), kandidat.typ)
    return (falt["organ"], falt["datum"], falt["typ"]) == motet


def motstandare(pool: Pool, kommun: str, kandidat: Kandidat) -> PurePosixPath | None:
    """Sammanträdets enda dokument av typen, utan namn och ur arkivet från
    en annan plattform, som kandidatens plattform inte redan har prövats
    mot. Kandidaten ska vara sin plattforms enda för typen (`ensamma`)."""
    plats = grundplats(kandidat)
    falt = pool.efter_sokvag.get(plats.sokvag(kommun))
    if plats.namn or not provas_mot(falt, kandidat) or levande(falt):
        return None
    tidigare = lista(falt["tidigare_kallnycklar"])
    if any(plattform(n) == plattform(kandidat.kallnyckel) for n in tidigare):
        return None
    flera = sum(samma_mote(f, kandidat) for f in pool.efter_sokvag.values()) > 1
    return None if flera else plats.sokvag(kommun)


def forlorar(gammal, kandidat: Kandidat, kvalitet: str) -> bool:
    """Ett fullständigt dokument från en annan plattform står kvar om
    kandidaten inte har högre kvalitet."""
    if not provas_mot(gammal, kandidat):
        return False
    return KVALITETER.index(kvalitet) >= KVALITETER.index(gammal["kvalitet"])


def ensamma(kandidater: list[Kandidat]) -> frozenset[str]:
    """Källnycklarna som är sin plattforms enda kandidat av typen för
    sammanträdet."""
    grupper = Counter(grupp(k) for k in kandidater)
    return frozenset(k.kallnyckel for k in kandidater if grupper[grupp(k)] == 1)


def grupp(kandidat: Kandidat) -> tuple:
    motet = (kandidat.organ, kandidat.datum, kandidat.typ)
    return (*motet, plattform(kandidat.kallnyckel))
