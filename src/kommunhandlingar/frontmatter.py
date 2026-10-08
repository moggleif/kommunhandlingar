"""Krav: K4, K6, K14 och K15 i docs/02-KRAV.md. Test: tests/test_hamta.py,
tests/test_webbplats.py.

Front matter så som schemat i docs/03-ARKITEKTUR.md#front-matter skriver den:
varje fält på en egen rad, i schemats ordning, listor inom hakparenteser.
"""

from datetime import date

FALT = (
    "kommun",
    "organ",
    "datum",
    "lopnr",
    "typ",
    "namn",
    "kallnyckel",
    "tidigare_kallnycklar",
    "arenden",
    "kalla_url",
    "sha256",
    "bytes",
    "sidor",
    "hamtad",
    "konverterad",
    "pipeline",
    "kvalitet",
    "fel",
    "kvalitet_per_sida",
    "tal_obekraftade",
    "figurer",
    "tolkade",
)


def las(text: str) -> dict[str, str]:
    huvud = text.split("---\n")[1]
    return dict(rad.split(": ", 1) for rad in huvud.splitlines())


def lista(varde: str) -> list[str]:
    if varde == "null":
        return []
    return [del_ for del_ in varde.strip("[]").split(", ") if del_]


def skriv(falt: dict) -> str:
    rader = [f"{namn}: {varde_av(falt[namn])}" for namn in FALT]
    return "---\n" + "\n".join(rader) + "\n---\n"


def varde_av(varde) -> str:
    if varde is None:
        return "null"
    if isinstance(varde, list):
        return "[" + ", ".join(varde_av(v) for v in varde) + "]"
    if isinstance(varde, date):
        return varde.isoformat()
    return str(varde)
