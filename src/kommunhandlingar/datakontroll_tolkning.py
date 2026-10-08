"""Krav: K11 och K15 i docs/02-KRAV.md, ADR-0017. Test:
tests/test_datakontroll_tolkning.py.

Datakontrollen av tolkningarna (docs/03-ARKITEKTUR.md#tolkade-figurer):
att `tolkade` hör ihop med `figurer`, att sidorna står en gång var och i
ordning, att varje tolkad sida har precis en tolkning, och att varje tal
i en tolkad CSV står i sidans text.
"""

import csv
import re
from pathlib import Path

from kommunhandlingar import frontmatter

TOLKNING = "<!-- tolkning:"
SIDA = re.compile(r"<!-- sida (\d+) -->")
LANK = re.compile(r"\[[^\]]*\]\([^)]*\)")
SIFFRA = re.compile(r"\d")
# Ett helt tal, med tusentalsmellanrum: `120` står inte i `1 120`, och
# inget tal står i `13.30` eller `2025-10-08`.
TALEN = re.compile(
    r"(?<![\d,.:])(?<!\d[-−–])[-−–]?(?:\d{1,3}(?:[ \xa0]\d{3})+|\d+)(?:,\d+)?"
    r"(?: ?%)?(?![.,:−–-]?\d)"
)


def dokumentfel(falt: dict[str, str], text: str) -> list[str]:
    figurer, tolkade = falt["figurer"], falt["tolkade"]
    if (figurer == "null") != (tolkade == "null"):
        return ["figurer och tolkade är inte null samtidigt"]
    sidor = frontmatter.lista(tolkade)
    if sidor != [s for s in frontmatter.lista(figurer) if s in sidor]:
        return ["tolkade är inte sidor ur figurer, i ordning"]
    if sidor and not i_ordning(SIDA.findall(text), falt["sidor"]):
        return ["sidorna står inte en gång var och i ordning"]
    return [
        f"sidan {nr} har {d.count(TOLKNING)} tolkningar men ska ha {int(nr in sidor)}"
        for nr, d in sidorna(text).items()
        if d.count(TOLKNING) != int(nr in sidor)
    ]


def i_ordning(nummer: list[str], antal: str) -> bool:
    return (
        nummer == [str(n) for n in range(1, len(nummer) + 1)]
        and str(len(nummer)) == antal
    )


def sidorna(md: str) -> dict[str, str]:
    delar = SIDA.split(md)
    return dict(zip(delar[1::2], delar[2::2], strict=True))


def sidans_text(md: str, sida: int) -> str:
    """Sidans text i `.md` före tolkningen, utan länkarna till tabellerna."""
    text = sidorna(md.split("---\n", 2)[-1]).get(str(sida), "")
    return LANK.sub("", text.split(TOLKNING)[0])


def talfel(fil: Path, md: Path, sida: int) -> list[str]:
    text = sidans_text(md.read_text(encoding="utf-8"), sida)
    talen = set(TALEN.findall(text))
    celler = csv.reader(fil.read_text(encoding="utf-8").splitlines())
    fel = []
    for cell in (c for rad in celler for c in rad):
        if SIFFRA.search(TALEN.sub("", cell)) and not ordagrant(cell, text):
            fel.append(f"cellen {cell!r} har siffror som inte är ett helt tal")
        fel += [
            f"talet {t!r} står inte i sidans text"
            for t in TALEN.findall(cell)
            if t not in talen
        ]
    return fel


def ordagrant(cell: str, text: str) -> bool:
    """Cellen står som den är i sidans text, som etiketten `65–79 år`."""
    return re.search(rf"(?<!\w){re.escape(cell)}(?!\w)", text) is not None
