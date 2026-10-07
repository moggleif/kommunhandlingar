"""Krav: K5 i docs/02-KRAV.md, ADR-0005 och ADR-0009. Test: tests/test_konvertering.py.

En säker tabell är avgränsad av ritade linjer: streck och fyllda
rektanglar som är högst 2 punkter breda eller höga. Varje ord inom
tabellens yta ska ha sin mittpunkt i en cell.
"""

import csv
import io

from pdfplumber.page import Page
from pdfplumber.table import Table

LINJEBREDD = 2


def sakra(sida: Page) -> list[Table]:
    linjer = sida.lines + [
        r for r in sida.rects if min(r["width"], r["height"]) <= LINJEBREDD
    ]
    if len(linjer) < 2:
        return []
    installning = {
        "vertical_strategy": "explicit",
        "horizontal_strategy": "explicit",
        "explicit_vertical_lines": linjer,
        "explicit_horizontal_lines": linjer,
    }
    ord_ = sida.extract_words()
    tabeller = [t for t in sida.find_tables(installning) if ar_saker(t, ord_)]
    return sorted(tabeller, key=lambda t: (round(t.bbox[1]), t.bbox[0]))


def ar_saker(tabell: Table, ord_: list[dict]) -> bool:
    if len(tabell.rows) < 2 or max(len(rad.cells) for rad in tabell.rows) < 2:
        return False
    inne = [mitt(o) for o in ord_ if inom(mitt(o), tabell.bbox)]
    return all(any(inom(punkt, c) for c in tabell.cells) for punkt in inne)


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
