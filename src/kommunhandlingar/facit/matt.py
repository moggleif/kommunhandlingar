"""Krav: K20 i docs/02-KRAV.md, ADR-0025. Test: tests/test_facit.py.

Urvalets mått, totalt och per dokument, och raden per version i matt.csv.
"""

import csv
from collections import Counter
from pathlib import Path

from kommunhandlingar.facit.jamfor import MATT, Utfall, jamfor
from kommunhandlingar.facit.lasa import urvalet
from kommunhandlingar.konvertering.dokument import konvertera

URVALET = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "facit"


def urvalets_utfall(katalog: Path) -> dict[str, Utfall]:
    return {f.namn: jamfor(f, konvertera(f.pdf)) for f in urvalet(katalog)}


def totalt(utfall: dict[str, Utfall]) -> Counter:
    summa = Counter(dict.fromkeys(MATT, 0))
    for u in utfall.values():
        summa.update(u.matt)
    return summa


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
