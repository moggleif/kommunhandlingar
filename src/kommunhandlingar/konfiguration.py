"""Krav: K1 i docs/02-KRAV.md, ADR-0019. Test: tests/test_konfiguration.py."""

import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from kommunhandlingar import schema
from kommunhandlingar.adaptrar import sitevision
from kommunhandlingar.fel import Konfigurationsfel

ORGANFALT = {"id", "namn", "fran", "till", "foregangare"}


@dataclass(frozen=True)
class Organ:
    id: str
    namn: tuple[str, ...]
    fran: date | None
    till: date | None
    foregangare: tuple[str, ...]


@dataclass(frozen=True)
class Kommun:
    id: str
    namn: str
    organ: tuple[Organ, ...]
    kallor: tuple[sitevision.Kalla, ...]
    omkonvertera: bool


def las(sokvag: Path) -> Kommun:
    with sokvag.open("rb") as fil:
        return tolka(sokvag.stem, tomllib.load(fil))


def tolka(kommun_id: str, data: dict) -> Kommun:
    schema.kontrollera_falt(
        data, {"namn", "organ", "kalla", "omkonvertera"}, "kommunen"
    )
    namn = schema.varde(data, "namn", str, "kommunen")
    organ = tuple(organ_av(post) for post in poster(data, "organ"))
    kontrollera_organ(organ)
    organ_id = [o.id for o in organ]
    kallor = tuple(
        kalla_av(post, i, organ_id) for i, post in enumerate(poster(data, "kalla"), 1)
    )
    omkonvertera = schema.valfritt(data, "omkonvertera", bool, "kommunen") or False
    return Kommun(
        schema.katalognamn(kommun_id, "kommunen"), namn, organ, kallor, omkonvertera
    )


def poster(data: dict, falt: str) -> list[dict]:
    lista = schema.varde(data, falt, list, "kommunen")
    if not lista or not all(isinstance(post, dict) for post in lista):
        raise Konfigurationsfel(f"kommunen: {falt} ska vara en lista med tabeller")
    return lista


def organ_av(post: dict) -> Organ:
    var = f"organ {post.get('id')!r}"
    schema.kontrollera_falt(post, ORGANFALT, var)
    namn = schema.textlista(post, "namn", var)
    if not namn:
        raise Konfigurationsfel(f"{var}: organet har inget namn")
    return Organ(
        schema.katalognamn(schema.varde(post, "id", str, var), var),
        namn,
        schema.valfritt(post, "fran", date, var),
        schema.valfritt(post, "till", date, var),
        schema.textlista(post, "foregangare", var),
    )


def kontrollera_organ(organ: tuple[Organ, ...]) -> None:
    kontrollera_id_och_foregangare(organ)
    for i, a in enumerate(organ):
        for b in organ[i + 1 :]:
            if delar_namn(a, b) and overlappar(a, b):
                raise Konfigurationsfel(
                    f"organ {a.id!r} och {b.id!r}: samma namn samtidigt"
                )


def kontrollera_id_och_foregangare(organ: tuple[Organ, ...]) -> None:
    id_ = [o.id for o in organ]
    for o in organ:
        if id_.count(o.id) > 1:
            raise Konfigurationsfel(f"organ {o.id!r}: två organ har samma id")
        saknade = [f for f in o.foregangare if f not in id_]
        if saknade:
            raise Konfigurationsfel(
                f"organ {o.id!r}: föregångaren {saknade[0]!r} finns inte"
            )


def normaliserat(namn: str) -> str:
    return " ".join(namn.casefold().split())


def delar_namn(a: Organ, b: Organ) -> bool:
    return bool({normaliserat(n) for n in a.namn} & {normaliserat(n) for n in b.namn})


def overlappar(a: Organ, b: Organ) -> bool:
    return (a.fran or date.min) <= (b.till or date.max) and (b.fran or date.min) <= (
        a.till or date.max
    )


def kalla_av(post: dict, nummer: int, organ_id: list[str]) -> sitevision.Kalla:
    var = f"kalla {nummer}"
    adapter = schema.varde(post, "adapter", str, var)
    if adapter != "sitevision":
        raise Konfigurationsfel(f"{var}: okänd adapter {adapter!r}")
    return sitevision.kalla_av(post, organ_id, var)
