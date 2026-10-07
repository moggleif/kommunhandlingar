"""Krav: K2 och K13 i docs/02-KRAV.md. Test: tests/test_kandidat.py."""

from dataclasses import dataclass
from datetime import date

# Ordningen inom ett organ (ADR-0010); också de typer som finns (K2).
TYPORDNING = ("protokoll", "kallelse", "bilaga", "handlingar")


@dataclass(frozen=True)
class Kandidat:
    organ: str
    datum: date
    typ: str
    url: str
    kalla: str
    kallnyckel: str
    filnamn: str


@dataclass(frozen=True)
class Avvisad:
    kalla: str
    filnamn: str
    orsak: str


def ordna(kandidater: list[Kandidat], organordning: list[str]) -> list[Kandidat]:
    def nyckel(kandidat: Kandidat) -> tuple:
        return (
            organordning.index(kandidat.organ),
            TYPORDNING.index(kandidat.typ),
            kandidat.datum,
            kandidat.kallnyckel,
        )

    return sorted(kandidater, key=nyckel)
