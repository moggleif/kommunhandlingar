"""Krav: K48 i docs/02-KRAV.md, ADR-0071. Test: tests/test_paragrafer.py.

Ett protokolls text delas vid raderna som inleder en paragraf, `§ 121`,
`BN § 1` eller `§ 121 Dnr GA-2026-00004`. Vilka avsnitt som blir
paragrafer avgör `paragrafer`.
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass

from kommunhandlingar.diarienummer import i_huvudet
from kommunhandlingar.paragrafinnehall import SIDA, beslut, dnr_rader, rubrik

RUBRIKRAD = re.compile(r"^\s*(?:[A-ZÅÄÖ]{2,4}\s*)?§\s*(\d+)(.*)$")
FORTS = re.compile(r"^[\s,./]*forts", re.IGNORECASE)
DATUM = re.compile(r"\d{4}-\d{2}-\d{2}")
PUNKTER = re.compile(r"\.{4}|…")


@dataclass(frozen=True)
class Paragraf:
    nummer: int
    rubrik: str | None
    diarienummer: list[str]
    beslut: str | None
    sida: int


def paragrafer(text: str) -> list[Paragraf]:
    """Innehållsförteckningens rader hoppas över, ett avsnitt direkt efter
    ett med samma nummer är en fortsättningssida, och annars gäller det
    sista avsnittet, eftersom närvarolistan räknar upp numren först."""
    rader = text.splitlines()
    valda, forra = {}, None
    for nummer, start, slut in avsnitten(rader):
        if forteckning(rader[start + 1 : slut]):
            forra = None
            continue
        if forra and forra[0] == nummer and forra[2] == start:
            start = forra[1]
        valda[nummer] = (start, slut)
        forra = (nummer, start, slut)
    ordning = sorted(valda.items(), key=lambda par: par[1][0])
    return [paragraf(n, rader, s, e) for n, (s, e) in ordning]


def forteckning(rader: list[str]) -> bool:
    """Innehållsförteckningens rad: rubriken följs av punkter och sidan."""
    forsta = next((r for r in rader if r.strip()), "")
    return bool(PUNKTER.search(forsta))


def avsnitten(rader: list[str]) -> list[tuple[int, int, int]]:
    starter = [(i, int(m[1])) for i, m in rubriker(rader)]
    slut = [i for i, _ in starter[1:]] + [len(rader)]
    return [(n, i, e) for (i, n), e in zip(starter, slut, strict=False)]


def rubriker(rader: list[str]) -> Iterator[tuple[int, re.Match]]:
    for i, rad in enumerate(rader):
        if (m := RUBRIKRAD.match(rad)) and inleder(m[2], rader[i - 1] if i else ""):
            yield i, m


def inleder(rest: str, forra: str) -> bool:
    """Ett ensamt `§ 4` efter en rad text hör till närvarolistan eller texten."""
    rest = rest.strip()
    if not rest:
        forra = forra.strip()
        return not forra or bool(SIDA.match(forra) or DATUM.fullmatch(forra))
    return bool(FORTS.match(rest)) or bool(i_huvudet(rest, ensam=True))


def paragraf(nummer: int, rader: list[str], start: int, slut: int) -> Paragraf:
    rest = rader[start + 1 : slut]
    numren = i_huvudet(RUBRIKRAD.match(rader[start])[2], ensam=True)
    for rad in dnr_rader(rest):
        numren += i_huvudet(rad)
    return Paragraf(
        nummer=nummer,
        rubrik=rubrik(rest),
        diarienummer=list(dict.fromkeys(numren)),
        beslut=beslut(rest),
        sida=sida(rader, start),
    )


def sida(rader: list[str], start: int) -> int:
    """Sidan med den senaste sidbrytningen före raden; utan brytning sidan 1."""
    for rad in reversed(rader[:start]):
        if m := SIDA.match(rad):
            return int(m[1])
    return 1
