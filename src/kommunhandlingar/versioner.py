"""Krav: K53 i docs/02-KRAV.md, ADR-0077. Test: tests/test_versioner.py.

Versionsloggen: en rad för varje källnyckel som efter steg 2 är ny i poolen
eller har en annan adress än före, räknad ur poolens front matter före och
efter. Formatet står i docs/03-ARKITEKTUR.md#versionsloggen.
"""

import csv
from datetime import datetime
from pathlib import Path

from kommunhandlingar.pool import Pool

KOLUMNER = ("sedd", "organ", "datum", "typ", "kallnyckel", "kalla_url", "sha256")


def adresser(pool: Pool) -> dict[str, str]:
    return {
        nyckel: pool.efter_sokvag[sokvag]["kalla_url"]
        for nyckel, sokvag in pool.efter_nyckel.items()
    }


def nya(fore: dict[str, str], efter: Pool, sedd: datetime) -> list[list[str]]:
    rader = []
    for nyckel, sokvag in sorted(efter.efter_nyckel.items()):
        falt = efter.efter_sokvag[sokvag]
        if fore.get(nyckel) != falt["kalla_url"]:
            varden = [sedd.isoformat()] + [falt[k] for k in KOLUMNER[1:]]
            rader.append([tomt_for_null(v) for v in varden] + [str(sokvag)])
    return rader


def tomt_for_null(varde: str) -> str:
    return "" if varde == "null" else varde


def skriv(fil: Path, rader: list[list[str]]) -> None:
    if not rader:
        return
    ny = not fil.exists()
    fil.parent.mkdir(parents=True, exist_ok=True)
    with fil.open("a", encoding="utf-8", newline="") as ut:
        skrivare = csv.writer(ut, lineterminator="\n")
        if ny:
            skrivare.writerow([*KOLUMNER, "dokument"])
        skrivare.writerows(rader)
