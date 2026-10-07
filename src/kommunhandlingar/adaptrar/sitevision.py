"""Krav: K1 och K2 i docs/02-KRAV.md, ADR-0011. Test: tests/test_sitevision.py."""

import re
from dataclasses import dataclass
from datetime import date

from kommunhandlingar import monster, schema
from kommunhandlingar.adaptrar.sitevision_html import Forekomst, forekomster
from kommunhandlingar.fel import IngenKandidat, Konfigurationsfel
from kommunhandlingar.kandidat import Avvisad, Kandidat

FALT = {"adapter", "monster", "manader", "sidor", "rubrik", "rattelser"}
MONSTERGRUPPER = {"ar", "manad", "dag", "typ"}


@dataclass(frozen=True)
class Kalla:
    sidor: dict[str, str]
    rubrik: re.Pattern
    monster: tuple[monster.Monster, ...]
    manader: tuple[str, ...]
    rattelser: dict[str, date]


def kalla_av(post: dict, organ_id: list[str], var: str) -> Kalla:
    schema.kontrollera_falt(post, FALT, var)
    monsterposter = schema.varde(post, "monster", list, var)
    return Kalla(
        sidor(schema.varde(post, "sidor", dict, var), organ_id, var),
        rubrik(schema.varde(post, "rubrik", str, var), var),
        tuple(
            monster.kompilera(p, MONSTERGRUPPER, f"{var}, mönster")
            for p in monsterposter
        ),
        monster.manader(post, var),
        rattelser(schema.valfritt(post, "rattelser", dict, var) or {}, var),
    )


def sidor(tabell: dict, organ_id: list[str], var: str) -> dict[str, str]:
    for organ, adress in tabell.items():
        if organ not in organ_id or not isinstance(adress, str):
            raise Konfigurationsfel(f"{var}: sidan för {organ!r}")
    return tabell


def rubrik(text: str, var: str) -> re.Pattern:
    uttryck = monster.uttryck(text, var)
    if set(uttryck.groupindex) != monster.DATUMGRUPPER:
        raise Konfigurationsfel(f"{var}: rubrik ska ha grupperna ar, manad och dag")
    return uttryck


def rattelser(tabell: dict, var: str) -> dict[str, date]:
    for nyckel, datum in tabell.items():
        if not nyckel.startswith("sitevision:") or not schema.ar_av_slag(datum, date):
            raise Konfigurationsfel(f"{var}: rättelsen för {nyckel!r}")
    return tabell


def upptack(
    kalla: Kalla, html_per_sida: dict[str, str]
) -> tuple[list[Kandidat], list[Avvisad]]:
    kandidater: dict[str, Kandidat] = {}
    avvisade: dict[str, Avvisad] = {}
    for organ, adress in kalla.sidor.items():
        for forekomst in forekomster(html_per_sida[adress], adress):
            nyckel = kallnyckel(forekomst)
            if nyckel in kandidater:
                continue
            try:
                kandidater[nyckel] = kandidat(kalla, organ, adress, forekomst)
                avvisade.pop(nyckel, None)
            except IngenKandidat as fel:
                avvisade.setdefault(
                    nyckel, Avvisad(adress, forekomst.filnamn, str(fel))
                )
    return list(kandidater.values()), list(avvisade.values())


def kallnyckel(forekomst: Forekomst) -> str:
    return f"sitevision:{forekomst.nodid}"


def kandidat(kalla: Kalla, organ: str, adress: str, forekomst: Forekomst) -> Kandidat:
    nyckel = kallnyckel(forekomst)
    tolkning = monster.tolka(kalla.monster, forekomst.filnamn, kalla.manader)
    datum = kalla.rattelser.get(nyckel) or motesdatum(
        kalla, tolkning.datum, forekomst.rubrik
    )
    return Kandidat(
        organ=organ,
        datum=datum,
        typ=tolkning.typ,
        url=forekomst.adress,
        kalla=adress,
        kallnyckel=nyckel,
        filnamn=forekomst.filnamn,
    )


def motesdatum(kalla: Kalla, filnamnsdatum: date | None, rubriktext: str) -> date:
    traff = kalla.rubrik.search(rubriktext)
    rubriksdatum = monster.datum_av(traff.groupdict(), kalla.manader) if traff else None
    if filnamnsdatum and rubriksdatum and filnamnsdatum != rubriksdatum:
        raise IngenKandidat(f"filnamnet säger {filnamnsdatum}, rubriken {rubriksdatum}")
    if not (filnamnsdatum or rubriksdatum):
        raise IngenKandidat("varken filnamnet eller rubriken har ett datum")
    return filnamnsdatum or rubriksdatum
