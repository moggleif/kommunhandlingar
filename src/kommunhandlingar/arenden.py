"""Krav: K48 i docs/02-KRAV.md, ADR-0071. Test: tests/test_arenden.py.

`arenden` i ett protokoll är paragrafernas diarienummer, sorterade och
utan dubbletter: `[]` när protokollet har paragrafer men inga
diarienummer, och `null` när inga paragrafer hittas eller dokumentet inte
är ett protokoll.

`python -m kommunhandlingar.arenden <data>` skriver fältet i dokument som
en äldre version konverterat, och i granskade dokument, utan att hämta
PDF:en. Bara raden `arenden` ändras, och en andra körning ändrar ingenting.
"""

import sys
from pathlib import Path

from kommunhandlingar import frontmatter
from kommunhandlingar.paragrafer import paragrafer
from kommunhandlingar.skrivning import skriv_md


def arenden(typ: str, brodtext: str) -> list[str] | None:
    if typ != "protokoll":
        return None
    funna = paragrafer(brodtext)
    return sorted({n for p in funna for n in p.diarienummer}) if funna else None


def ratt_varde(text: str) -> str:
    """Fältets värde som front matter skriver det, räknat ur texten."""
    typ = frontmatter.las(text)["typ"]
    return frontmatter.varde_av(arenden(typ, frontmatter.brodtext(text)))


def fyll(data: Path) -> int:
    andrade = 0
    for fil in sorted(data.rglob("*.md")):
        text = fil.read_text(encoding="utf-8")
        gammal = frontmatter.las(text)["arenden"]
        if (ny := ratt_varde(text)) != gammal:
            rad = f"\narenden: {gammal}\n"
            skriv_md(fil, text.replace(rad, f"\narenden: {ny}\n", 1))
            andrade += 1
    return andrade


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Användning: python -m kommunhandlingar.arenden <data>")
    print(f"{fyll(Path(sys.argv[1]))} dokument fick nya ärenden.")
