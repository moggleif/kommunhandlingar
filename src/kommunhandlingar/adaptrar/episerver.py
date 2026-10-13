"""Krav: K1, K2 och K23 i docs/02-KRAV.md, ADR-0039.
Test: tests/test_episerver.py.

Webbplatsens Episerver-generationer, som bara finns i Internet Archive.
Organets mappar står i kommunfilen. Typen och datumet läses med var sin
lista med mönster ur sökvägen under mappen, till exempel
`Protokoll/2013/GV protokoll 20 nov.pdf`.
"""

import re
from dataclasses import dataclass
from datetime import date

from kommunhandlingar import monster, schema
from kommunhandlingar.fel import IngenKandidat, Konfigurationsfel

FALT = {"adapter", "mappar", "typer", "datum", "manader", "rattelser"}


@dataclass(frozen=True)
class Kalla:
    mappar: dict[str, tuple[str, ...]]
    typer: tuple[monster.Monster, ...]
    datum: tuple[re.Pattern, ...]
    manader: tuple[str, ...]
    rattelser: dict[str, date]


def kalla_av(post: dict, organ_id: list[str], var: str) -> Kalla:
    schema.kontrollera_falt(post, FALT, var)
    typer = schema.varde(post, "typer", list, var)
    return Kalla(
        mappar(schema.varde(post, "mappar", dict, var), organ_id, var),
        tuple(monster.kompilera(p, set(), f"{var}, typer") for p in typer),
        tuple(datummonster(t, var) for t in schema.textlista(post, "datum", var)),
        monster.manader(post, var),
        rattelser(schema.valfritt(post, "rattelser", dict, var) or {}, var),
    )


def mappar(tabell: dict, organ_id: list[str], var: str) -> dict[str, tuple[str, ...]]:
    for organ, lista in tabell.items():
        if organ not in organ_id or not lista:
            raise Konfigurationsfel(f"{var}: mapparna för {organ!r}")
        if not all(isinstance(m, str) and m.endswith("/") for m in lista):
            raise Konfigurationsfel(f"{var}: en mapp för {organ!r} slutar inte på /")
    return {organ: tuple(lista) for organ, lista in tabell.items()}


def datummonster(text: str, var: str) -> re.Pattern:
    uttryck = monster.uttryck(text, f"{var}, datum")
    if set(uttryck.groupindex) != monster.DATUMGRUPPER:
        raise Konfigurationsfel(f"{var}: datum ska ha grupperna ar, manad och dag")
    return uttryck


def rattelser(tabell: dict, var: str) -> dict[str, date]:
    for nyckel, datum in tabell.items():
        if not nyckel.startswith("episerver:") or not schema.ar_av_slag(datum, date):
            raise Konfigurationsfel(f"{var}: rättelsen för {nyckel!r}")
    return tabell


def typ_och_datum(kalla: Kalla, text: str, nyckel: str) -> tuple[str, date]:
    """Texten är sökvägen under mappen, avkodad."""
    return typ(kalla, text), kalla.rattelser.get(nyckel) or datum(kalla, text)


def typ(kalla: Kalla, text: str) -> str:
    for monstret in kalla.typer:
        if monstret.uttryck.search(text):
            return monstret.typ
    raise IngenKandidat("inget typmönster matchar")


def datum(kalla: Kalla, text: str) -> date:
    for uttryck in kalla.datum:
        if traff := uttryck.search(text):
            grupper = traff.groupdict()
            # Episerver-generationerna är från 2000-talet.
            if len(grupper["ar"]) == 2:
                grupper["ar"] = "20" + grupper["ar"]
            return monster.datum_av(grupper, kalla.manader)
    raise IngenKandidat("inget datummönster matchar")
