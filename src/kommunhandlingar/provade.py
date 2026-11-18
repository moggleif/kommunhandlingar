"""Krav: K11 i docs/02-KRAV.md, ADR-0088. Test: tests/test_delar.py.

Kandidaterna som steg 2 redan provat i en körning som går i delar, en
källnyckel per rad bredvid kandidatlistan. Varje kandidat provas en gång
per körning, som när steg 2 gick i ett svep: ett dokument som inte gick
att hämta eller nådde sin tidsgräns väntar till nästa körning i stället
för att tas om först i varje del. En kandidat som lagts åt sidan vid
budgetens hårda gräns räknas inte som provad.
"""

from pathlib import Path

from kommunhandlingar.kandidat import Kandidat


def fil(kandidatlista: Path) -> Path:
    return kandidatlista.with_suffix(".provade")


def kvar(kandidater: list[Kandidat], provfil: Path | None) -> list[Kandidat]:
    if provfil is None or not provfil.exists():
        return kandidater
    provade = set(provfil.read_text(encoding="utf-8").splitlines())
    return [k for k in kandidater if k.kallnyckel not in provade]


def skriv(provfil: Path | None, provade: list[Kandidat]) -> None:
    if provfil is None:
        return
    with provfil.open("a", encoding="utf-8") as ut:
        ut.writelines(f"{k.kallnyckel}\n" for k in provade)
