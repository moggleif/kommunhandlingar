"""Krav: K20 i docs/02-KRAV.md, ADR-0025. Test: tests/test_facit.py.

`python -m kommunhandlingar.facit [--spara]` konverterar urvalet, skriver
måtten per dokument och totalt, och med `--spara` måtten för poolens
version i matt.csv.
"""

import csv
import sys
from collections import Counter
from importlib.metadata import version
from pathlib import Path

from kommunhandlingar.facit.jamfor import MATT, Utfall, jamfor
from kommunhandlingar.facit.lasa import urvalet
from kommunhandlingar.konvertering.dokument import konvertera

KATALOG = Path("tests/fixtures/facit")
MATTFIL = KATALOG / "matt.csv"


def urvalets_utfall(katalog: Path) -> dict[str, Utfall]:
    return {f.namn: jamfor(f, konvertera(f.pdf)) for f in urvalet(katalog)}


def totalt(utfall: dict[str, Utfall]) -> Counter:
    summa = Counter(dict.fromkeys(MATT, 0))
    for u in utfall.values():
        summa.update(u.matt)
    return summa


def skriv(utfall: dict[str, Utfall]):
    for namn, u in utfall.items():
        print(rad(namn, u.matt))
        print("".join(f"  {n}\n" for n in u.noter), end="")
    print(rad("totalt", totalt(utfall)))


def rad(namn: str, matt: Counter) -> str:
    return f"{namn:<30}" + " ".join(f"{m}={matt[m]}" for m in MATT)


def sparade(fil: Path) -> dict[str, dict[str, str]]:
    with fil.open(encoding="utf-8", newline="") as f:
        return {r["version"]: r for r in csv.DictReader(f)}


def spara(fil: Path, poolens_version: str, matt: Counter):
    rader = sparade(fil)
    rader[poolens_version] = {"version": poolens_version, **{m: matt[m] for m in MATT}}
    with fil.open("w", encoding="utf-8", newline="") as f:
        skrivare = csv.DictWriter(f, ["version", *MATT], lineterminator="\n")
        skrivare.writeheader()
        skrivare.writerows(rader.values())


if __name__ == "__main__":
    utfall = urvalets_utfall(KATALOG)
    skriv(utfall)
    if "--spara" in sys.argv[1:]:
        spara(MATTFIL, version("kommunhandlingar"), totalt(utfall))
