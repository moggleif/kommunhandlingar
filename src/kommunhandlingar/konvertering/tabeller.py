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

from pdfplumber.page import Page
from pdfplumber.table import Table

from kommunhandlingar.konvertering.text import TAL

LINJEBREDD = 2
SIFFERGRUPP = re.compile(r"[-−–+]?\d+(?:[,.]\d+)?%?")
# En rad i en cell som är ett tal, med eller utan parentes och en kort enhet,
# eller ett streck.
TALRAD = re.compile(r"\(?[-−–+]?\d[\d  .,]*\)?(?: ?%| [a-zåäö]{1,4})?|[-−–]")
SKILJE = re.compile(r"[\s()/]+")
SAMMA_FALT = 0.5
SIFFRA = re.compile(r"\d")


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
    return [t for t in sida.find_tables(installning) if ar_saker(t, ord_)]


def ar_saker(tabell: Table, ord_: list[dict]) -> bool:
    if len(tabell.rows) < 2 or max(len(rad.cells) for rad in tabell.rows) < 2:
        return False
    if any(flera_tal(c) for rad in rader(tabell) for c in rad):
        return False
    if any(glest([o for o in ord_ if inom(mitt(o), c)]) for c in tabell.cells):
        return False
    inne = [mitt(o) for o in ord_ if inom(mitt(o), tabell.bbox)]
    return all(any(inom(punkt, c) for c in tabell.cells) for punkt in inne)


def flera_tal(cell: str) -> bool:
    rader_ = [r.strip() for r in cell.split("\n")]
    return sum(1 for r in rader_ if TALRAD.fullmatch(r)) > 1 or any(
        map(flera_pa_raden, rader_)
    )


def flera_pa_raden(rad: str) -> bool:
    delar = [d for d in SKILJE.split(rad) if d and d != "%"]
    return (
        len(delar) > 1
        and all(SIFFERGRUPP.fullmatch(d) for d in delar)
        and not TAL.fullmatch(rad.strip("()"))
    )


def glest(ord_: list[dict]) -> bool:
    """Två ord med siffror på samma rad i cellen, med mer än en halv
    teckenhöjd emellan: två tal, som i olinjerade tabeller (ADR-0016)."""
    ord_ = sorted(ord_, key=lambda o: (round(o["top"]), o["x0"]))
    return any(
        abs(a["top"] - b["top"]) <= 3
        and SIFFRA.search(a["text"])
        and SIFFRA.search(b["text"])
        and b["x0"] - a["x1"] > SAMMA_FALT * (a["bottom"] - a["top"])
        for a, b in zip(ord_, ord_[1:], strict=False)
    )


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
