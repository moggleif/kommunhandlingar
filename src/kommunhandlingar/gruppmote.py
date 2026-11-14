"""Krav: K49 i docs/02-KRAV.md, ADR-0072. Test: tests/test_gruppmoten.py.

Kommunfilens `[gruppmote]`: vilket organs sammanträden partierna har
gruppmöte inför, på vilken veckodag före och vid vilken tid.
"""

from dataclasses import dataclass

from kommunhandlingar import schema
from kommunhandlingar.fel import Konfigurationsfel

VECKODAGAR = ["måndag", "tisdag", "onsdag", "torsdag", "fredag", "lördag", "söndag"]


@dataclass(frozen=True)
class Gruppmote:
    fore: str
    veckodag: int
    tid: str


def gruppmote_av(post: dict, organ_id: list[str]) -> Gruppmote:
    schema.kontrollera_falt(post, {"fore", "veckodag", "tid"}, "gruppmote")
    fore = schema.varde(post, "fore", str, "gruppmote")
    veckodag = schema.varde(post, "veckodag", str, "gruppmote")
    if fore not in organ_id:
        raise Konfigurationsfel(f"gruppmote: organet {fore!r} finns inte")
    if veckodag not in VECKODAGAR:
        raise Konfigurationsfel(f"gruppmote: {veckodag!r} är ingen veckodag")
    tid = schema.varde(post, "tid", str, "gruppmote")
    return Gruppmote(fore, VECKODAGAR.index(veckodag), tid)
