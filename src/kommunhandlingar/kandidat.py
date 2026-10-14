"""Krav: K2, K13, K16 och K31 i docs/02-KRAV.md. Test: tests/test_kandidat.py."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

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
    # Ett möte i flera filer (ADR-0049): delarnas adresser i ordning.
    delar: tuple[str, ...] = ()

    def kalla_url(self) -> str | list[str]:
        return list(self.delar) if self.delar else self.url

    def adresser(self) -> list[str]:
        return list(self.delar) or [self.url]


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


def ordna_bakat(kandidater: list[Kandidat], organordning: list[str]) -> list[Kandidat]:
    """Arkivets ordning (ADR-0018): det nyaste sammanträdet först, för alla organ."""

    def nyckel(kandidat: Kandidat) -> tuple:
        return (
            -kandidat.datum.toordinal(),
            organordning.index(kandidat.organ),
            TYPORDNING.index(kandidat.typ),
            kandidat.kallnyckel,
        )

    return sorted(kandidater, key=nyckel)


def lista(arbetskatalog: Path, kommun: str, arkiv: bool) -> Path:
    slag = ".arkiv" if arkiv else ""
    return arbetskatalog / f"{kommun}{slag}.kandidater.json"
