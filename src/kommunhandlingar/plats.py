"""Krav: K2, K8, K9 och K45 i docs/02-KRAV.md, ADR-0003 och ADR-0068.
Test: tests/test_plats.py.

Var ett nytt dokument hamnar i poolen. Platsen bestäms första gången
källnyckeln hittas: bilagor och filer som adaptern namngett (ADR-0068)
har alltid ett namn, övriga får ett bara när
platsen är upptagen. En ny källnyckel på en upptagen plats är en ny version
av dokumentet där, om dess källnyckel inte längre finns bland kandidaterna.
"""

import re
import unicodedata
from dataclasses import dataclass, replace
from datetime import date
from pathlib import PurePosixPath

from kommunhandlingar.kandidat import Kandidat

LANGSTA_NAMN = 80


@dataclass(frozen=True)
class Plats:
    organ: str
    datum: date
    typ: str
    namn: str | None = None

    def sokvag(self, kommun: str) -> PurePosixPath:
        dag = self.datum.isoformat()
        fil = self.typ + (f"-{self.namn}" if self.namn else "") + ".md"
        return PurePosixPath(kommun, self.organ, str(self.datum.year), dag, fil)


def namn_av(text: str) -> str:
    text = text.lower().replace("å", "a").replace("ä", "a").replace("ö", "o")
    text = "".join(
        t for t in unicodedata.normalize("NFKD", text) if not unicodedata.combining(t)
    )
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if len(text) > LANGSTA_NAMN:
        kort = text[:LANGSTA_NAMN]
        text = kort.rsplit("-", 1)[0] if "-" in kort else kort
    return text


def ledigt_namn(onskat: str, upptagen, bas: str = "") -> str:
    """Det önskade namnet, annars ett löpnummer, efter `bas` när
    adaptern gett ett namn (ADR-0068), så att projektet står kvar."""
    if onskat and not upptagen(onskat):
        return onskat
    nummer = 2
    while upptagen(lopnamn(bas, nummer)):
        nummer += 1
    return lopnamn(bas, nummer)


def ledigt_for(kandidat: Kandidat, upptagen) -> str:
    return ledigt_namn(onskat_namn(kandidat), upptagen, kandidat.namn)


def lopnamn(bas: str, nummer: int) -> str:
    return f"{bas}-{nummer}" if bas else str(nummer)


def grundplats(kandidat: Kandidat) -> Plats:
    plats = Plats(kandidat.organ, kandidat.datum, kandidat.typ)
    if kandidat.typ == "bilaga" or kandidat.namn:
        return replace(plats, namn=onskat_namn(kandidat) or "2")
    return plats


def onskat_namn(kandidat: Kandidat) -> str:
    """Adapterns namn (ADR-0068), annars filnamnets."""
    return kandidat.namn or namn_av(
        kandidat.filnamn.removesuffix(".pdf").removesuffix(".PDF")
    )
