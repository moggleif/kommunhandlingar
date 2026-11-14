"""Krav: K47 i docs/02-KRAV.md, ADR-0070. Test: tests/test_dokumentindex.py.

Indexet över en kommuns dokument: en rad i JSON Lines per dokument, med
front matter som JSON-typer och var dokumentet och dess tabeller finns.
"""

import json
from pathlib import Path

from kommunhandlingar.frontmatter import FALT, lista

TAL = {"lopnr", "bytes", "sidor", "tal_obekraftade", "figurer", "tolkade"}


def skriv(ut: Path, dokument: list[dict], katalog: Path) -> None:
    rader = "".join(rad(falt, katalog) + "\n" for falt in dokument)
    (ut / katalog.name / "index.jsonl").write_text(rader, encoding="utf-8")


def rad(falt: dict[str, str], katalog: Path) -> str:
    md = Path(falt["adress"]).with_suffix(".md")
    tabeller = (katalog / md).with_suffix(".tabeller").glob("*.csv")
    objekt = {namn: varde(namn, falt[namn]) for namn in FALT} | {
        "fil": f"data/{katalog.name}/{md.as_posix()}",
        "sida": f"{katalog.name}/{falt['adress']}",
        "tabeller": sorted(tabell.name for tabell in tabeller),
    }
    return json.dumps(objekt, ensure_ascii=False)


def varde(namn: str, text: str) -> str | int | list | None:
    if text == "null":
        return None
    tolka = int if namn in TAL else str
    if text.startswith("["):
        return [tolka(del_) for del_ in lista(text)]
    return tolka(text)
