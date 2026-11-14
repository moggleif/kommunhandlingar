"""Krav: K53 i docs/02-KRAV.md, ADR-0077. Test: tests/test_versionslogg.py.

Versionsloggen: en rad för varje källnyckel som efter steg 2 är ny i poolen
eller har en annan adress eller sha256 än före, räknad ur poolens front
matter före och efter. Formatet står i docs/03-ARKITEKTUR.md#versionsloggen.
"""

import csv
from datetime import datetime
from pathlib import Path

from kommunhandlingar.pool import Pool

FRONT_MATTER = ("organ", "datum", "typ", "kallnyckel", "kalla_url", "sha256")
RUBRIK = ("sedd", *FRONT_MATTER, "dokument")


def versioner(pool: Pool) -> dict[str, tuple[str, str]]:
    return {
        nyckel: version(pool.efter_sokvag[sokvag])
        for nyckel, sokvag in pool.efter_nyckel.items()
    }


def version(falt: dict[str, str]) -> tuple[str, str]:
    return falt["kalla_url"], falt["sha256"]


def nya(fore: dict[str, tuple[str, str]], efter: Pool, sedd: datetime) -> list:
    rader = []
    for nyckel, sokvag in sorted(efter.efter_nyckel.items()):
        falt = efter.efter_sokvag[sokvag]
        if fore.get(nyckel) != version(falt):
            varden = [falt[k] for k in FRONT_MATTER]
            rader.append([sedd.isoformat(), *varden, str(sokvag)])
    return [["" if v == "null" else v for v in rad] for rad in rader]


def skriv(fil: Path, rader: list[list[str]]) -> None:
    if not rader:
        return
    ny = not fil.exists()
    fil.parent.mkdir(parents=True, exist_ok=True)
    with fil.open("a", encoding="utf-8", newline="") as ut:
        skrivare = csv.writer(ut, lineterminator="\n")
        if ny:
            skrivare.writerow(RUBRIK)
        skrivare.writerows(rader)
