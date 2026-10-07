"""Krav: K10 i docs/02-KRAV.md, ADR-0013. Test: tests/test_klient.py."""

import tomllib
from dataclasses import dataclass
from pathlib import Path

from kommunhandlingar import schema

VAR = "hamtning.toml"


@dataclass(frozen=True)
class Installningar:
    user_agent: str
    intervall: int


def las(sokvag: Path) -> Installningar:
    with sokvag.open("rb") as fil:
        data = tomllib.load(fil)
    schema.kontrollera_falt(data, {"user_agent", "intervall"}, VAR)
    return Installningar(
        schema.varde(data, "user_agent", str, VAR),
        schema.varde(data, "intervall", int, VAR),
    )
