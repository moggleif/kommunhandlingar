"""Krav: K48 i docs/02-KRAV.md, ADR-0071. Test: tests/test_paragrafindex.py.

Protokollens paragrafer som en rad i JSON Lines per paragraf, i
sökvägarnas och paragrafernas ordning, med var paragrafen står och hur
väl dess sida lästes.
"""

import json
from pathlib import Path

from kommunhandlingar.frontmatter import brodtext, lista
from kommunhandlingar.paragrafer import Paragraf, paragrafer
from kommunhandlingar.webbplats.dokumentindex import platser, varde


def av_dokument(falt: dict[str, str], text: str, katalog: Path) -> list[str]:
    if falt["typ"] != "protokoll":
        return []
    return [rad(falt, p, katalog) for p in paragrafer(brodtext(text))]


def rad(falt: dict[str, str], paragraf: Paragraf, katalog: Path) -> str:
    plats = platser(falt, katalog)
    plats["sida"] += f"#sida-{paragraf.sida}"
    objekt = {
        "organ": falt["organ"],
        "datum": falt["datum"],
        "lopnr": varde("lopnr", falt["lopnr"]),
        "paragraf": paragraf.nummer,
        "rubrik": paragraf.rubrik,
        "diarienummer": paragraf.diarienummer,
        "beslut": paragraf.beslut,
        "sidnummer": paragraf.sida,
        "kvalitet": lista(falt["kvalitet_per_sida"])[paragraf.sida - 1],
        "tal_obekraftade": str(paragraf.sida) in lista(falt["tal_obekraftade"]),
    }
    return json.dumps(objekt | plats, ensure_ascii=False)


def skriv(ut: Path, rader: list[str], katalog: Path) -> None:
    text = "".join(r + "\n" for r in rader)
    (ut / katalog.name / "paragrafer.jsonl").write_text(text, encoding="utf-8")
