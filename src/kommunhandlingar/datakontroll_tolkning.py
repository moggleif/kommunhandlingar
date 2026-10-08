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
MARKERING = re.compile(r"<!-- tolkning: [^,\n]+, \d{4}-\d{2}-\d{2} -->")
SIDA = re.compile(r"<!-- sida (\d+) -->")
LANK = re.compile(r"\[[^\]]*\]\([^)]*\)")
SIFFRA = re.compile(r"\d")
# Blanksteg som kan skilja tusentalen men inte läses så.
SMALT = "[\t\u2009\u202f]"
# Ett helt tal, med tusentalsmellanrum: `120` står inte i `1 120` eller
# `1 250–1 120`, och inget tal står i `13.30`, `2025-10-08`, `2022/23`
# eller `K15`.
FORE = (
    r"(?<![\w,.:/])(?<!\w[-−–])"
    r"(?<!\d[-−–]\d[ \xa0])(?<!\d[-−–]\d\d[ \xa0])(?<!\d[-−–]\d\d\d[ \xa0])"
)
EFTER = r"(?![.,:/−–-]?\d)(?!\w)"
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
    if antal != ska:
        return [f"sidan {nr} har {antal} tolkningar men ska ha {ska}"]
    if len(MARKERING.findall(sida)) != antal:
        return [f"sidan {nr} har en tolkning utan modell och datum"]
    return []


def sidorna(md: str) -> dict[str, str]:
    delar = SIDA.split(md)
    return dict(zip(delar[1::2], delar[2::2], strict=True))


def sidans_text(md: str, sida: int) -> str:
    """Sidans text i `.md` före tolkningen, utan länkarna till tabellerna."""
    text = sidorna(md.split("---\n", 2)[-1]).get(str(sida), "")
    return LANK.sub("", text.split(TOLKNING)[0])


def talfel(fil: Path, md: Path, sida: int) -> list[str]:
    text = sidans_text(md.read_text(encoding="utf-8"), sida)
    talen = sidans_tal(text)
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


def sidans_tal(text: str) -> set[str]:
    return {m.group() for m in TALEN.finditer(text) if fristaende(text, m)}


def ordagrant(cell: str, text: str) -> bool:
    """Cellen står som den är i sidans text, som etiketten `65–79 år`, och
    är ingen del av ett tal med tusentalsmellanrum."""
    fore = FORE + (r"(?<!\d[ \xa0])" if cell[:1].isdigit() else "")
    efter = EFTER + (r"(?![ \xa0]\d)" if cell[-1:].isdigit() else "")
    traffar = re.finditer(fore + re.escape(cell) + efter, text)
    return any(fristaende(text, m) for m in traffar)


def fristaende(text: str, traff: re.Match) -> bool:
    """Träffen är ingen del av ett tal över en radbrytning eller ett annat
    blanksteg: står en siffra intill på andra sidan ska både träffen och
    grannraden stå ensamma på sina rader, som talen i ett diagram."""
    fore, efter = text[: traff.start()], text[traff.end() :]
    if re.search(rf"\d{SMALT}\Z", fore) or re.match(rf"{SMALT}\d", efter):
        return False
    fore, efter = re.search(r"\d\n\Z", fore), re.match(r"\n\d", efter)
    if not (fore or efter):
        return True
    rader = text.split("\n")
    nr = text.count("\n", 0, traff.start())
    grannar = [rader[nr - 1] if fore else "", rader[nr + 1] if efter else ""]
    return rader[nr].strip() == traff.group() and all(map(ensamt, grannar))


def ensamt(rad: str) -> bool:
    """Raden är tom, ett tal eller ett enda ord."""
    return TALEN.fullmatch(rad.strip()) is not None or len(rad.split()) <= 1
