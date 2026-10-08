"""Krav: K11 och K15 i docs/02-KRAV.md, ADR-0017. Test: tests/test_datakontroll.py.

Datakontrollen av tolkningarna (docs/03-ARKITEKTUR.md#tolkade-figurer):
att `tolkade` hör ihop med `figurer`, att varje tolkad sida har precis en
tolkning, och att varje tal i en tolkad CSV står i sidans text.
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
    r"(?<![\d,.:])(?<!\d[-−–])[-−–]?(?:\d{1,3}(?:[  ]\d{3})+|\d+)(?:,\d+)?"
    r"(?: ?%)?(?![.,:−–-]?\d)"
)


def dokumentfel(falt: dict[str, str], text: str) -> list[str]:
    figurer, tolkade = falt["figurer"], falt["tolkade"]
    if (figurer == "null") != (tolkade == "null"):
        return ["figurer och tolkade är inte null samtidigt"]
    sidor = frontmatter.lista(tolkade)
    if sidor != [s for s in frontmatter.lista(figurer) if s in sidor]:
        return ["tolkade är inte sidor ur figurer, i ordning"]
    return [
        f"sidan {nr} har {antal} tolkningar"
        + (", och står i tolkade" if nr in sidor else ", men står inte i tolkade")
        for nr, antal in tolkningar(text).items()
        if antal != (nr in sidor)
    ]


def tolkningar(text: str) -> dict[str, int]:
    delar = SIDA.split(text)
    return {
        nr: d.count(TOLKNING) for nr, d in zip(delar[1::2], delar[2::2], strict=True)
    }


def sidans_text(md: str, sida: int) -> str:
    """Sidans text i `.md` före tolkningen, utan länkarna till tabellerna."""
    delar = SIDA.split(md.split("---\n", 2)[-1])
    text = dict(zip(delar[1::2], delar[2::2], strict=True)).get(str(sida), "")
    return LANK.sub("", text.split(TOLKNING)[0])


def talfel(fil: Path, md: Path, sida: int) -> list[str]:
    talen = set(TALEN.findall(sidans_text(md.read_text(encoding="utf-8"), sida)))
    celler = csv.reader(fil.read_text(encoding="utf-8").splitlines())
    fel = []
    for cell in (c for rad in celler for c in rad):
        if SIFFRA.search(TALEN.sub("", cell)):
            fel.append(f"cellen {cell!r} har siffror som inte är ett helt tal")
        fel += [
            f"talet {t!r} står inte i sidans text"
            for t in TALEN.findall(cell)
            if t not in talen
        ]
    return fel
