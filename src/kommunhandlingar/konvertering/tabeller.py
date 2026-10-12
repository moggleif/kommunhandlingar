"""Krav: K5 och K19 i docs/02-KRAV.md, ADR-0005, ADR-0009, ADR-0016, ADR-0024 och
ADR-0031.
Test: tests/test_konvertering.py och tests/test_celler.py.

En säker tabell är avgränsad av ritade linjer: streck och fyllda
rektanglar som är högst 2 punkter breda eller höga. Varje ord inom
tabellens yta ska ha sin mittpunkt i en cell, och ingen cell får rymma mer
än ett tal.

Talen i en cell känns igen vidare än `text.TAL`, med decimalpunkt,
plustecken, parentes, enhet och fotnotsstjärna, eftersom ett tal för mycket bara fäller
tabellen, medan ett tal för lite ger en cell med två tal i en CSV. En
fälld tabell kan ändå delas (`delade.py`, ADR-0028).
"""

import csv
import io
import re

from pdfplumber.page import Page
from pdfplumber.table import Table

from kommunhandlingar.konvertering import markdown
from kommunhandlingar.konvertering.falt import falt, radvis
from kommunhandlingar.konvertering.text import TAL

LINJEBREDD = 2
ENHET = r"%|kr|tkr|mkr|mnkr|mdkr|st"
# Ett tal, med eller utan parentes och enhet.
TALET = rf"\(?[-−–+]?\d+(?:[ \xa0]\d{{3}})*(?:[,.]\d+)?\)?(?: ?(?:{ENHET}))?"
TALRAD = re.compile(rf"{TALET}|[-−–]", re.IGNORECASE)
# En etikett på ett eller två ord utan siffror följd av ett tal.
ETIKETT_OCH_TAL = re.compile(rf"[^\d\s]+(?: [^\d\s]+)? {TALET}", re.IGNORECASE)
VARDE = re.compile(r"[-−–+]?\d+(?:[,.]\d+)?%?|[-−–]")
SKILJE = re.compile(r"\s+/\s+|[\s()]+")
# En fotnotsstjärna direkt efter en siffra, som i `4 078*`.
FOTNOT = re.compile(r"(?<=\d)\*+(?!\d)")


def sakra(sida: Page, ord_: list[dict]) -> tuple[list[Table], list[Table]]:
    """De säkra tabellerna, och de som fälldes för att en cell rymmer flera
    tal."""
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
    hela = [t for t in sida.find_tables(installning) if ar_hel(t, ord_)]
    fallda = [t for t in hela if rymmer_flera_tal(t, ord_)]
    return [t for t in hela if t not in fallda], fallda


def ar_hel(tabell: Table, ord_: list[dict]) -> bool:
    """Minst två rader och två kolumner, text i tabellen, och varje ord i en
    cell. Ett rutnät utan text, som linjerna i ett diagram, är ingen tabell."""
    if len(tabell.rows) < 2 or max(len(rad.cells) for rad in tabell.rows) < 2:
        return False
    inne = [mitt(o) for o in ord_ if inom(mitt(o), tabell.bbox)]
    return bool(inne) and all(any(inom(p, c) for c in tabell.cells) for p in inne)


def rymmer_flera_tal(tabell: Table, ord_: list[dict]) -> bool:
    if any(flera_tal(c) for rad in rader(tabell) for c in rad):
        return True
    i_cell = ([o for o in ord_ if inom(mitt(o), c)] for c in tabell.cells)
    return any(map(flera_falt, i_cell))


def flera_tal(cell: str) -> bool:
    rader_ = [FOTNOT.sub("", r).strip() for r in cell.split("\n")]
    med_tal = sum(
        1 for r in rader_ if TALRAD.fullmatch(r) or ETIKETT_OCH_TAL.fullmatch(r)
    )
    return med_tal > 1 or any(map(flera_pa_raden, rader_))


def flera_pa_raden(rad: str) -> bool:
    delar = [d for d in SKILJE.split(rad) if d and not enhet(d)]
    return (
        len(delar) > 1
        and all(VARDE.fullmatch(d) for d in delar)
        and not TAL.fullmatch(" ".join(delar).replace(".", ","))
    )


def flera_falt(ord_: list[dict]) -> bool:
    """Två fält på samma rad i cellen som var för sig är ett tal eller ett
    streck."""
    for rad in radvis(ord_):
        if sum(1 for f in falt(rad, dela_tvetydiga=True) if talfalt(f.text)) > 1:
            return True
    return False


def talfalt(text: str) -> bool:
    """Ett tal eller ett streck, med eller utan fotnotsstjärna."""
    return TALRAD.fullmatch(FOTNOT.sub("", text)) is not None


def enhet(text: str) -> bool:
    return re.fullmatch(ENHET, text, re.I) is not None


def forsta_med_text(rader: list[list[str]]) -> int:
    """Tabellens första kolumn med text, där etiketterna står."""
    return next(i for i in range(len(rader[0])) if any(r[i] for r in rader))


def siffra(text: str) -> bool:
    return any(c.isdigit() for c in text)


def mitt(objekt: dict) -> tuple[float, float]:
    return ((objekt["x0"] + objekt["x1"]) / 2, (objekt["top"] + objekt["bottom"]) / 2)


def inom(punkt: tuple[float, float], ruta: tuple) -> bool:
    return ruta[0] <= punkt[0] <= ruta[2] and ruta[1] <= punkt[1] <= ruta[3]


def kanter(tabell: Table) -> tuple[float, ...]:
    """Kolumnernas vänsterkanter och tabellens högerkant."""
    return (*(k.bbox[0] for k in tabell.columns), tabell.bbox[2])


def rader(tabell: Table) -> list[list[str]]:
    return [[cell or "" for cell in rad] for rad in tabell.extract()]


def som_csv(rader_: list[list[str]]) -> str:
    ut = io.StringIO()
    csv.writer(ut, lineterminator="\n").writerows(rader_)
    return ut.getvalue()


def som_markdown(rader_: list[list[str]]) -> str:
    celler = [[markdown.cell(c) for c in r] for r in rader_]
    rubrik, *ovriga = celler
    linjer = [rubrik, ["---"] * len(rubrik), *ovriga]
    return "\n".join("| " + " | ".join(rad) + " |" for rad in linjer)
