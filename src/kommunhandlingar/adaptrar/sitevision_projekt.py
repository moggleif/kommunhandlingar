"""Krav: K45 i docs/02-KRAV.md, ADR-0068. Test: tests/test_sitevision_projekt.py.

Kommunens lista med projekt: listan och dess bläddringssidor ger
projektsidorna, och en sida en nivå under en projektsida är ett eget
projekt. Varje fil på en projektsida blir handlingar under organet,
daterad med dagen den lades upp och namngiven efter projektet och filen.
"""

import re
from collections.abc import Callable
from datetime import UTC, date, datetime
from html.parser import HTMLParser
from pathlib import PurePosixPath
from urllib.parse import urljoin, urlsplit
from zoneinfo import ZoneInfo

from kommunhandlingar.adaptrar.sitevision import kallnyckel
from kommunhandlingar.adaptrar.sitevision_html import NEDLADDNING, forekomster
from kommunhandlingar.fel import Hamtfel
from kommunhandlingar.kandidat import Avvisad, Kandidat
from kommunhandlingar.plats import namn_av

TIDSZON = ZoneInfo("Europe/Stockholm")


class Lankar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.adresser: list[str] = []

    def handle_starttag(self, tagg, attribut):
        if tagg == "a" and (adress := dict(attribut).get("href")):
            self.adresser.append(adress)


def lankar(html: str, sidadress: str) -> list[str]:
    tolk = Lankar()
    tolk.feed(html)
    tolk.close()
    return [urljoin(sidadress, a).split("#")[0] for a in tolk.adresser]


def projektsidor(lista: str, hamta: Callable[[str], str]) -> list[str]:
    """Listans projekt i sidornas ordning."""
    sidor, projekt, i = [lista], [], 0
    while i < len(sidor):
        for adress in lankar(hamta(sidor[i]), sidor[i]):
            if bladdring(lista, adress) and adress not in sidor:
                sidor.append(adress)
            elif ar_projekt(lista, adress) and adress not in projekt:
                projekt.append(adress)
        i += 1
    return projekt


def bladdring(lista: str, adress: str) -> bool:
    """Listans sida med ett sidnummer från 2, `?<parameter>=2`; sida 1 är
    listan själv, och filtren har fler parametrar."""
    sokvag, _, fraga = adress.partition("?")
    traff = re.fullmatch(r"[^&=]+=(\d+)", fraga)
    return sokvag == lista and bool(traff) and int(traff[1]) > 1


# En sida direkt under listan, eller under en projektsida.
def ar_projekt(ovan: str, adress: str) -> bool:
    delar = urlsplit(adress)
    sokvag = PurePosixPath(delar.path)
    return not delar.query and str(sokvag.parent) == urlsplit(ovan).path.rstrip("/")


# Ett fel här stoppar aldrig upptäckten (ADR-0068): sidan hoppas över och
# står i sammanfattningen, så att mötena hämtas ändå.
FEL = (Hamtfel, ValueError, KeyError)


def upptack(
    projekt: dict[str, str], hamta: Callable[[str], str]
) -> tuple[list[Kandidat], list[Avvisad]]:
    kandidater: dict[str, Kandidat] = {}
    avvisade: list[Avvisad] = []
    for organ, lista in projekt.items():
        try:
            sidor = projektsidor(lista, hamta)
        except FEL as fel:
            avvisade.append(Avvisad(lista, "", f"listan: {fel}"))
            continue
        for sida in sidor:
            nya, bort = projektet(organ, sida, hamta)
            avvisade += bort
            for kandidat in nya:
                kandidater.setdefault(kandidat.kallnyckel, kandidat)
    return list(kandidater.values()), avvisade


def projektet(
    organ: str, sida: str, hamta: Callable[[str], str]
) -> tuple[list[Kandidat], list[Avvisad]]:
    """Projektsidans filer och filerna på sidorna en nivå under den, som
    räknas som egna projekt. Djupare sidor finns inte och läses inte."""
    try:
        html, kandidater = pa_sidan(organ, sida, hamta)
    except FEL as fel:
        return [], [Avvisad(sida, "", f"projektsidan: {fel}")]
    avvisade = []
    for under in dict.fromkeys(a for a in lankar(html, sida) if ar_projekt(sida, a)):
        try:
            kandidater += pa_sidan(organ, under, hamta)[1]
        except FEL as fel:
            avvisade.append(Avvisad(under, "", f"sidan under projektet: {fel}"))
    return kandidater, avvisade


def pa_sidan(
    organ: str, sida: str, hamta: Callable[[str], str]
) -> tuple[str, list[Kandidat]]:
    html = hamta(sida)
    return html, kandidater_pa(organ, sida, html)


def kandidater_pa(organ: str, sida: str, html: str) -> list[Kandidat]:
    projektet = PurePosixPath(urlsplit(sida).path).name
    return [
        Kandidat(
            organ=organ,
            datum=upplagd(f.adress),
            typ="handlingar",
            url=f.adress,
            kalla=sida,
            kallnyckel=kallnyckel(f),
            filnamn=f.filnamn,
            namn=namn_av(f"{projektet} {PurePosixPath(f.filnamn).stem}"),
        )
        for f in forekomster(html, sida)
    ]


def upplagd(adress: str) -> date:
    """Dagen i Sitevisions tidsstämpel, millisekunder sedan 1970, i svensk tid."""
    millisekunder = int(NEDLADDNING.match(adress)[2])
    return datetime.fromtimestamp(millisekunder / 1000, UTC).astimezone(TIDSZON).date()
