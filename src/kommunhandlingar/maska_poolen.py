"""Krav: K17 i docs/02-KRAV.md, ADR-0022. Test: tests/test_maskning.py.

`python -m kommunhandlingar.maska_poolen <data>` maskar personuppgifterna
i text och tabeller som en äldre version skrivit, utan att hämta PDF:en.
Front matter och `pipeline` rörs inte, så omkonverteringen (ADR-0019) ser
fortfarande vilken version som läste dokumentet. En fil skrivs bara om
något maskas, och en andra körning ändrar ingenting.
"""

import csv
import io
import sys
from pathlib import Path

from kommunhandlingar.konvertering.personuppgifter import maska
from kommunhandlingar.konvertering.tabeller import som_csv
from kommunhandlingar.skrivning import skriv_md


def maska_poolen(data: Path) -> int:
    andrade = 0
    for fil in sorted(data.rglob("*")):
        maskad = maskad_fil(fil)
        if maskad is not None:
            skriv_md(fil, maskad)
            andrade += 1
    return andrade


def maskad_fil(fil: Path) -> str | None:
    if fil.suffix == ".md":
        text = fil.read_text(encoding="utf-8")
        maskad = maskad_md(text)
    elif fil.suffix == ".csv":
        text = fil.read_text(encoding="utf-8")
        maskad = maskad_csv(text)
    else:
        return None
    return None if maskad == text else maskad


def maskad_md(text: str) -> str:
    huvud, slut, brodtext = text.partition("\n---\n")
    return huvud + slut + maska(brodtext) if slut else text


def maskad_csv(text: str) -> str:
    rader = csv.reader(io.StringIO(text))
    return som_csv([[maska(cell) for cell in rad] for rad in rader])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Användning: python -m kommunhandlingar.maska_poolen <data>")
    print(f"{maska_poolen(Path(sys.argv[1]))} filer maskades.")
