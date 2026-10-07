"""Krav: K2, K8 och K9 i docs/02-KRAV.md, ADR-0003. Test: tests/test_plats.py.

Var ett nytt dokument hamnar i poolen. Platsen bestäms första gången
källnyckeln hittas: bilagor har alltid ett namn, övriga får ett bara när
platsen är upptagen. En ny källnyckel på en upptagen plats är en ny version
av dokumentet där, om dess källnyckel inte längre finns bland kandidaterna.
"""

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import PurePosixPath

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


def ledigt_namn(onskat: str, upptagen) -> str:
    if onskat and not upptagen(onskat):
        return onskat
    nummer = 2
    while upptagen(str(nummer)):
        nummer += 1
    return str(nummer)
