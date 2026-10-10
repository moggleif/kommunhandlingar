"""Krav: K17 i docs/02-KRAV.md, ADR-0022. Test: tests/test_maska_poolen.py.

`python -m kommunhandlingar.maska_poolen <data>` maskar personuppgifterna
i text och tabeller som en äldre version skrivit, utan att hämta PDF:en.
Front matter och `pipeline` rörs inte, så omkonverteringen (ADR-0019) ser
fortfarande vilken version som läste dokumentet. En fil skrivs bara om
något maskas, och en andra körning ändrar ingenting.
"""

import sys
from pathlib import Path

from kommunhandlingar.konvertering.tabeller import som_csv
from kommunhandlingar.personuppgifter import maskad_md, maskade_celler
from kommunhandlingar.skrivning import skriv_md


def maska_poolen(data: Path) -> int:
    andrade = 0
    for fil in sorted(data.rglob("*")):
        maskad = maskad_fil(fil)
        if maskad is not None:
            skriv_md(fil, maskad)  # skriver via en temporär fil, också för CSV
            andrade += 1
    return andrade


def maskad_fil(fil: Path) -> str | None:
    if fil.suffix not in (".md", ".csv"):
        return None
    text = fil.read_text(encoding="utf-8")
    if fil.suffix == ".md":
        maskad = maskad_md(text)
        return None if maskad == text else maskad
    celler = maskade_celler(text)
    return None if celler is None else som_csv(celler)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Användning: python -m kommunhandlingar.maska_poolen <data>")
    print(f"{maska_poolen(Path(sys.argv[1]))} filer maskades.")
