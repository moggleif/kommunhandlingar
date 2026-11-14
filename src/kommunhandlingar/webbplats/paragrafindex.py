"""Krav: K48 i docs/02-KRAV.md, ADR-0071. Test: tests/test_paragrafindex.py.

Protokollens paragrafer som en rad i JSON Lines per paragraf, i
sökvägarnas och paragrafernas ordning, med var paragrafen står och hur
väl dess sida lästes.
"""

import json
from pathlib import Path

from kommunhandlingar.frontmatter import brodtext, lista
from kommunhandlingar.paragrafer import Paragraf, paragrafer


def av_dokument(falt: dict[str, str], text: str, katalog: Path) -> list[str]:
    if falt["typ"] != "protokoll" or falt["kvalitet"] == "ej-hamtad":
        return []
    return [rad(falt, p, katalog) for p in paragrafer(brodtext(text))]


def rad(falt: dict[str, str], paragraf: Paragraf, katalog: Path) -> str:
    md = Path(falt["adress"]).with_suffix(".md").as_posix()
    sida = f"{katalog.name}/{falt['adress']}"
    objekt = {
        "organ": falt["organ"],
        "datum": falt["datum"],
        "lopnr": None if falt["lopnr"] == "null" else int(falt["lopnr"]),
        "paragraf": paragraf.nummer,
        "rubrik": paragraf.rubrik,
        "diarienummer": paragraf.diarienummer,
        "beslut": paragraf.beslut,
        "sidnummer": paragraf.sida,
        "kvalitet": sidans(falt["kvalitet_per_sida"], paragraf.sida),
        "tal_obekraftade": str(paragraf.sida) in lista(falt["tal_obekraftade"]),
        "fil": f"data/{katalog.name}/{md}",
        "sida": f"{sida}#sida-{paragraf.sida}" if paragraf.sida else sida,
    }
    return json.dumps(objekt, ensure_ascii=False)


def sidans(kvalitet_per_sida: str, sida: int | None) -> str | None:
    sidor = lista(kvalitet_per_sida)
    return sidor[sida - 1] if sida and sida <= len(sidor) else None


def skriv(ut: Path, rader: list[str], katalog: Path) -> None:
    text = "".join(r + "\n" for r in rader)
    (ut / katalog.name / "paragrafer.jsonl").write_text(text, encoding="utf-8")
