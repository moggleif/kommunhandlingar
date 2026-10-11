"""Krav: K20 i docs/02-KRAV.md, ADR-0025. Test: tests/test_facit.py.

Läser urvalet: en katalog per dokument med utdraget, `facit.toml` och en
CSV per tabell (docs/03-ARKITEKTUR.md#facit-för-konverteringen).
"""

import csv
import tomllib
from dataclasses import dataclass
from pathlib import Path

RUBRIKRADER = 1


@dataclass(frozen=True)
class Tabell:
    namn: str
    sida: int
    sista_sida: int
    rubrikrader: int
    rader: list[list[str]]


@dataclass(frozen=True)
class Facit:
    namn: str
    pdf: Path
    tal: dict[int, list[str]]
    skannade: list[int]
    tabeller: list[Tabell]


def urvalet(katalog: Path) -> list[Facit]:
    return [facit(d) for d in sorted(katalog.iterdir()) if d.is_dir()]


def facit(katalog: Path) -> Facit:
    data = tomllib.loads((katalog / "facit.toml").read_text(encoding="utf-8"))
    sidor = list(enumerate(data["sida"], 1))
    rubriker = data.get("rubrikrader", {})
    filer = sorted(katalog.glob("*.csv"), key=lambda f: nummer(f.stem))
    return Facit(
        katalog.name,
        katalog / "utdrag.pdf",
        {nr: s["tal"] for nr, s in sidor if not s.get("skannad")},
        [nr for nr, s in sidor if s.get("skannad")],
        [tabell(f, rubriker.get(f.stem, RUBRIKRADER)) for f in filer],
    )


def nummer(namn: str) -> list[int]:
    return [int(n) for n in namn.split("-")]


def tabell(fil: Path, rubrikrader: int) -> Tabell:
    *sidor, _ = nummer(fil.stem)
    with fil.open(encoding="utf-8", newline="") as f:
        rader = list(csv.reader(f))
    return Tabell(fil.stem, sidor[0], sidor[-1], rubrikrader, rader)
