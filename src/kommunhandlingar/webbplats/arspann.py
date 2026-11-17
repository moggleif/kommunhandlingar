"""Krav: K60 i docs/02-KRAV.md, ADR-0086. Test: tests/test_arspann.py.

Åren som varje sida över tid i en kommun visar, lika för alla organ och
flikar så att de går att jämföra: från poolens första år till året då
webbplatsen byggs, och längre åt något håll om ett mål eller ett steg
ligger utanför, som en budget för nästa år.
"""

from pathlib import Path


def arspann(katalog: Path, radernas: list[int], byggd: int) -> range:
    poolens = [int(p.name) for p in katalog.glob("*/[0-9][0-9][0-9][0-9]")]
    alla = [*poolens, *radernas, byggd]
    return range(min(alla), max(alla) + 1)


def radernas_ar(kommun: str, malen: dict, uppfoljda: dict, sparen: dict) -> list[int]:
    rader = [*malen.get(kommun, []), *uppfoljda.get(kommun, [])]
    rader += [s for slag in sparen.values() for s in slag.get(kommun, [])]
    return [r.ar for r in rader]
