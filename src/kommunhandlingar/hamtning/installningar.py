"""Krav: K10 i docs/02-KRAV.md, ADR-0013. Test: tests/test_klient.py."""

import tomllib
from dataclasses import dataclass
from pathlib import Path

from kommunhandlingar import schema
from kommunhandlingar.fel import Konfigurationsfel

VAR = "hamtning.toml"


@dataclass(frozen=True)
class Installningar:
    user_agent: str
    intervall: int


def las(sokvag: Path) -> Installningar:
    with sokvag.open("rb") as fil:
        data = tomllib.load(fil)
    schema.kontrollera_falt(data, {"user_agent", "intervall"}, VAR)
    intervall = schema.varde(data, "intervall", int, VAR)
    if isinstance(intervall, bool) or intervall < 0:
        raise Konfigurationsfel(f"{VAR}: intervall ska vara ett antal sekunder")
    return Installningar(schema.varde(data, "user_agent", str, VAR), intervall)
