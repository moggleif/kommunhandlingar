"""Krav: K5 i docs/02-KRAV.md, ADR-0005, ADR-0009 och ADR-0016.
Test: tests/test_konvertering.py.

En säker tabell är avgränsad av ritade linjer: streck och fyllda
rektanglar som är högst 2 punkter breda eller höga. Varje ord inom
tabellens yta ska ha sin mittpunkt i en cell, och ingen cell får rymma mer
än ett tal.
"""

import csv
import io
import re
from itertools import pairwise

from pdfplumber.page import Page
from pdfplumber.table import Table

from kommunhandlingar.konvertering.falt import Falt, falt, radvis
from kommunhandlingar.konvertering.text import TAL

LINJEBREDD = 2
# En rad i en cell som är ett tal, med eller utan parentes och en kort enhet,
# eller ett streck.
TALRAD = re.compile(
    r"\(?[-−–+]?\d+(?:[  ]\d{3})*(?:[,.]\d+)?\)?(?: ?%| [a-zåäö]{1,4})?|[-−–]"
)
VARDE = re.compile(r"[-−–+]?\d+(?:[,.]\d+)?%?|[-−–]")
ENHET = re.compile(r"%|kr|tkr|mkr|mnkr|mdkr|st")
SKILJE = re.compile(r"\s+/\s+|[\s()]+")


def sakra(sida: Page) -> tuple[list[Table], list[tuple]]:
    """De säkra tabellerna, och rutorna kring dem som fälldes för att en
    cell rymmer flera tal."""
    linjer = sida.lines + [
        r for r in sida.rects if min(r["width"], r["height"]) <= LINJEBREDD
    ]
    if len(linjer) < 2:
        return [], []
    installning = {
        "vertical_strategy": "explicit",
        "horizontal_strategy": "explicit",
        "explicit_vertical_lines": linjer,
        "explicit_horizontal_lines": linjer,
    }
    ord_ = sida.extract_words()
    hela = [t for t in sida.find_tables(installning) if ar_hel(t, ord_)]
    fallda = [t for t in hela if rymmer_flera_tal(t, ord_)]
    return [t for t in hela if t not in fallda], [t.bbox for t in fallda]


def ar_hel(tabell: Table, ord_: list[dict]) -> bool:
    if len(tabell.rows) < 2 or max(len(rad.cells) for rad in tabell.rows) < 2:
        return False
    inne = [mitt(o) for o in ord_ if inom(mitt(o), tabell.bbox)]
    return all(any(inom(punkt, c) for c in tabell.cells) for punkt in inne)


def rymmer_flera_tal(tabell: Table, ord_: list[dict]) -> bool:
    if any(flera_tal(c) for rad in rader(tabell) for c in rad):
        return True
    i_cell = ([o for o in ord_ if inom(mitt(o), c)] for c in tabell.cells)
    return any(map(flera_falt, i_cell))


def flera_tal(cell: str) -> bool:
    rader_ = [r.strip() for r in cell.split("\n")]
    talrader = [TALRAD.fullmatch(r) is not None for r in rader_]
    i_foljd = any(a and b for a, b in pairwise(talrader))
    return i_foljd or any(map(flera_pa_raden, rader_))


def flera_pa_raden(rad: str) -> bool:
    delar = [d for d in SKILJE.split(rad) if d and not ENHET.fullmatch(d)]
    return (
        len(delar) > 1
        and all(VARDE.fullmatch(d) for d in delar)
        and not TAL.fullmatch(" ".join(delar).replace(".", ","))
    )


def flera_falt(ord_: list[dict]) -> bool:
    """Två fält på samma rad i cellen som var för sig är ett tal eller ett
    streck."""
    for rad in radvis(ord_):
        falt_ = falt(rad) or [Falt(o["text"], o["x0"], o["x1"]) for o in rad]
        if sum(1 for f in falt_ if TALRAD.fullmatch(f.text)) > 1:
            return True
    return False


def mitt(objekt: dict) -> tuple[float, float]:
    return ((objekt["x0"] + objekt["x1"]) / 2, (objekt["top"] + objekt["bottom"]) / 2)


def inom(punkt: tuple[float, float], ruta: tuple) -> bool:
    return ruta[0] <= punkt[0] <= ruta[2] and ruta[1] <= punkt[1] <= ruta[3]


def rader(tabell: Table) -> list[list[str]]:
    return [[cell or "" for cell in rad] for rad in tabell.extract()]


def som_csv(rader_: list[list[str]]) -> str:
    ut = io.StringIO()
    csv.writer(ut, lineterminator="\n").writerows(rader_)
    return ut.getvalue()


def som_markdown(rader_: list[list[str]]) -> str:
    celler = [[c.replace("|", "\\|").replace("\n", "<br>") for c in r] for r in rader_]
    rubrik, *ovriga = celler
    linjer = [rubrik, ["---"] * len(rubrik), *ovriga]
    return "\n".join("| " + " | ".join(rad) + " |" for rad in linjer)
