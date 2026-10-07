"""Krav: K10 i docs/02-KRAV.md, ADR-0013. Test: tests/test_robots.py.

Läser robots.txt enligt RFC 9309: gruppen för vår produkt gäller, annars
gruppen `*`; den längsta regel som träffar avgör, och Allow vinner vid lika
längd. `urllib.robotparser` i Python 3.12 förstår inte `*` och `$`.
"""

import re
from dataclasses import dataclass
from urllib.parse import urlsplit

REGELFALT = {"allow", "disallow"}


@dataclass(frozen=True)
class Regel:
    tillat: bool
    monster: re.Pattern
    langd: int


def tolka(text: str, produkt: str) -> tuple[Regel, ...]:
    grupper = block(rader(text))
    egen = any(produkt.lower() in agenter for agenter, _ in grupper)
    agent = produkt.lower() if egen else "*"
    egna = [r for agenter, regler in grupper if agent in agenter for r in regler]
    return tuple(regel(tillat, sokvag) for tillat, sokvag in egna if sokvag)


def rader(text: str) -> list[tuple[str, str]]:
    par = []
    for rad in text.splitlines():
        falt, kolon, varde = rad.split("#", 1)[0].partition(":")
        if kolon:
            par.append((falt.strip().lower(), varde.strip()))
    return par


def block(par: list[tuple[str, str]]) -> list[tuple[list[str], list]]:
    grupper: list[tuple[list[str], list]] = []
    for falt, varde in par:
        if falt == "user-agent" and (not grupper or grupper[-1][1]):
            grupper.append(([], []))
        if falt == "user-agent":
            grupper[-1][0].append(varde.lower())
        elif falt in REGELFALT and grupper:
            grupper[-1][1].append((falt == "allow", varde))
    return grupper


def regel(tillat: bool, sokvag: str) -> Regel:
    uttryck = re.escape(sokvag.removesuffix("$")).replace(r"\*", ".*")
    slut = "$" if sokvag.endswith("$") else ""
    return Regel(tillat, re.compile(uttryck + slut), len(sokvag))


def tillater(regler: tuple[Regel, ...], url: str) -> bool:
    delar = urlsplit(url)
    sokvag = (delar.path or "/") + (f"?{delar.query}" if delar.query else "")
    traffar = [(r.langd, r.tillat) for r in regler if r.monster.match(sokvag)]
    return max(traffar, default=(0, True))[1]
