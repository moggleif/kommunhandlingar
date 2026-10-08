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
# Ett helt tal, med tusentalsmellanrum: `120` står inte i `1 120` eller
# `1 250–1 120`, och inget tal står i `13.30`, `2025-10-08` eller `K15`.
FORE = r"(?<![\w,.:])(?<!\w[-−–])" + "".join(
    rf"(?<!\d[-−–]\d{{{n}}}[ \xa0])" for n in (1, 2, 3)
)
EFTER = r"(?![.,:−–-]?\d)(?!\w)"
TALEN = re.compile(
    rf"{FORE}[-−–]?(?>\d{{1,3}}(?:[ \xa0]\d{{3}})+|\d+)(?:,\d+)?(?: ?%)?{EFTER}"
)


def dokumentfel(falt: dict[str, str], text: str) -> list[str]:
    figurer, tolkade = falt["figurer"], falt["tolkade"]
    if (figurer == "null") != (tolkade == "null"):
        return ["figurer och tolkade är inte null samtidigt"]
    sidor = frontmatter.lista(tolkade)
    if sidor != [s for s in frontmatter.lista(figurer) if s in sidor]:
        return ["tolkade är inte sidor ur figurer, i ordning"]
    if figurer == "null":
        return []
    antal = len(frontmatter.lista(falt["kvalitet_per_sida"]))
    finns = [str(n) for n in range(1, antal + 1)]
    if any(s not in finns for s in frontmatter.lista(figurer)):
        return ["figurer har sidor som inte finns i dokumentet"]
    if sidor and SIDA.findall(text) != finns:
        return ["sidorna står inte en gång var och i ordning"]
    return [fel for nr, d in sidorna(text).items() for fel in antalfel(nr, d, sidor)]


def antalfel(nr: str, sida: str, tolkade: list[str]) -> list[str]:
    antal, ska = sida.count(TOLKNING), 1 if nr in tolkade else 0
    return (
        [f"sidan {nr} har {antal} tolkningar men ska ha {ska}"] if antal != ska else []
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
            fel.append(
                f"cellen {cell!r} har siffror som inte är ett helt tal"
                " och står inte ordagrant i sidans text"
            )
        fel += [
            f"talet {t!r} står inte i sidans text"
            for t in TALEN.findall(cell)
            if t not in talen
        ]
    return fel


def ordagrant(cell: str, text: str) -> bool:
    """Cellen står som den är i sidans text, som etiketten `65–79 år`."""
    return re.search(rf"{FORE}{re.escape(cell)}{EFTER}", text) is not None
