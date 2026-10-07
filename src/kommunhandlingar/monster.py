"""Krav: K1 och K2 i docs/02-KRAV.md. Test: tests/test_monster.py."""

import re
from dataclasses import dataclass
from datetime import date

from kommunhandlingar import schema
from kommunhandlingar.fel import IngenKandidat, Konfigurationsfel
from kommunhandlingar.kandidat import TYPORDNING

DATUMGRUPPER = {"ar", "manad", "dag"}


@dataclass(frozen=True)
class Monster:
    uttryck: re.Pattern
    typ: str | None


@dataclass(frozen=True)
class Tolkning:
    typ: str
    datum: date | None


def uttryck(text: str, var: str) -> re.Pattern:
    try:
        return re.compile(text)
    except re.error as fel:
        raise Konfigurationsfel(f"{var}: ogiltigt uttryck: {fel}") from fel


def kompilera(post: dict, grupper: set[str], var: str) -> Monster:
    schema.kontrollera_falt(post, {"regex", "typ"}, var)
    monster = uttryck(schema.varde(post, "regex", str, var), var)
    typ = schema.valfritt(post, "typ", str, var)
    funna = set(monster.groupindex)
    if funna - grupper:
        raise Konfigurationsfel(f"{var}: gruppen {', '.join(sorted(funna - grupper))}")
    if funna & DATUMGRUPPER not in (set(), DATUMGRUPPER):
        raise Konfigurationsfel(f"{var}: ar, manad och dag ska stå tillsammans")
    if ("typ" in funna) == (typ is not None):
        raise Konfigurationsfel(f"{var}: antingen gruppen eller fältet typ")
    if typ is not None and typ not in TYPORDNING:
        raise Konfigurationsfel(f"{var}: okänd typ {typ!r}")
    return Monster(monster, typ)


def manader(post: dict, var: str) -> tuple[str, ...]:
    namn = schema.textlista(post, "manader", var)
    if namn and (len(namn) != 12 or len({manad.casefold() for manad in namn}) != 12):
        raise Konfigurationsfel(f"{var}: manader ska ha tolv olika namn")
    return tuple(manad.casefold() for manad in namn)


def tolka(
    monster: tuple[Monster, ...], text: str, manadsnamn: tuple[str, ...]
) -> Tolkning:
    for monstret in monster:
        traff = monstret.uttryck.search(text)
        if traff:
            grupper = traff.groupdict()
            typ = (monstret.typ or grupper["typ"] or "").casefold()
            if typ not in TYPORDNING:
                raise IngenKandidat(f"okänd typ {typ!r}")
            return Tolkning(typ, datum_av(grupper, manadsnamn))
    raise IngenKandidat("inget mönster matchar")


def datum_av(grupper: dict, manadsnamn: tuple[str, ...]) -> date | None:
    if None in (grupper.get("ar"), grupper.get("manad"), grupper.get("dag")):
        return None
    if not re.fullmatch(r"\d{4}", grupper["ar"]):
        raise IngenKandidat(f"året {grupper['ar']!r} har inte fyra siffror")
    manad = manadsnummer(grupper["manad"], manadsnamn)
    try:
        return date(int(grupper["ar"]), manad, int(grupper["dag"]))
    except ValueError as fel:
        raise IngenKandidat(f"datumet finns inte: {fel}") from fel


def manadsnummer(manad: str, manadsnamn: tuple[str, ...]) -> int:
    if manad.isdigit():
        return int(manad)
    if manad.casefold() not in manadsnamn:
        raise IngenKandidat(f"okänt månadsnamn {manad!r}")
    return manadsnamn.index(manad.casefold()) + 1
