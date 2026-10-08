"""Krav: K2, K13 och K16 i docs/02-KRAV.md, ADR-0013 och ADR-0018.
Test: tests/test_upptack.py.

Steg 1: `python -m kommunhandlingar.upptack <kommunfil> <arbetskatalog>
[--arkiv] [--start N]`. Hämtar kommunens källsidor, kör adaptern och
skriver kandidatlistan; med `--arkiv` arkivets lista, som inte skrivs med
några kandidater när tidsbudgetens mjuka gräns räknat från `--start` är
passerad. `hamtning.toml` läses från repot som kommunfilen ligger i.
"""

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from kommunhandlingar import konfiguration, tidsbudget
from kommunhandlingar.adaptrar import sitevision, sitevision_arkiv
from kommunhandlingar.fel import Hamtfel, Konfigurationsfel
from kommunhandlingar.hamtning import installningar
from kommunhandlingar.hamtning.klient import Klient
from kommunhandlingar.kandidat import Avvisad, Kandidat, lista, ordna, ordna_bakat


def upptack(
    kommun: konfiguration.Kommun, klient
) -> tuple[list[Kandidat], list[Avvisad]]:
    kandidater: list[Kandidat] = []
    avvisade: list[Avvisad] = []
    for kalla in kommun.kallor:
        html = {adress: sida(klient, adress) for adress in kalla.sidor.values()}
        nya, bort = sitevision.upptack(kalla, html)
        kandidater += nya
        avvisade += bort
    return ordna(kandidater, [o.id for o in kommun.organ]), avvisade


def upptack_arkiv(
    kommun: konfiguration.Kommun, klient
) -> tuple[list[Kandidat], list[Avvisad], list[str]]:
    kandidater: list[Kandidat] = []
    avvisade: list[Avvisad] = []
    obesvarade: list[str] = []
    for kalla in kommun.kallor:
        if kalla.arkiv:
            nya, bort, utan_svar = sitevision_arkiv.upptack(kalla, klient)
            kandidater, avvisade = kandidater + nya, avvisade + bort
            obesvarade += utan_svar
    return ordna_bakat(kandidater, [o.id for o in kommun.organ]), avvisade, obesvarade


def sida(klient, adress: str) -> str:
    try:
        return klient.text(adress)
    except Hamtfel as fel:
        raise Hamtfel(fel.orsak, adress) from fel


def skriv(kandidater: list[Kandidat], fil: Path) -> None:
    poster = [asdict(k) | {"datum": k.datum.isoformat()} for k in kandidater]
    fil.write_text(json.dumps(poster, ensure_ascii=False, indent=1) + "\n", "utf-8")


def sammanfattning(
    kommun: konfiguration.Kommun, kandidater: list[Kandidat], avvisade: list[Avvisad]
) -> str:
    antal = Counter(k.organ for k in kandidater)
    rader = [f"{len(kandidater)} kandidater, {len(avvisade)} filer utan kandidat"]
    rader += [f"  {o.id}: {antal[o.id]}" for o in kommun.organ]
    rader += [f"Ingen kandidat: {a.filnamn} ({a.orsak}) på {a.kalla}" for a in avvisade]
    return "\n".join(rader)


def utanfor_repot(katalog: Path, rot: Path) -> Path:
    if katalog.resolve().is_relative_to(rot.resolve()):
        raise Konfigurationsfel(f"arbetskatalogen {katalog} ligger i repot")
    return katalog


def main(arg: argparse.Namespace) -> None:
    rot = arg.kommunfil.resolve().parent.parent
    katalog = utanfor_repot(arg.arbetskatalog, rot)
    kommun = konfiguration.las(arg.kommunfil)
    klient = Klient(installningar.las(rot / "hamtning.toml"))
    katalog.mkdir(parents=True, exist_ok=True)
    fil = lista(katalog, kommun.id, arg.arkiv)
    if arg.arkiv and datetime.now(UTC) >= tidsbudget.mjuk_grans(arg.start):
        skriv([], fil)
        print("Arkivet väntar på nästa körning: tidsbudgeten är slut.")
        return
    obesvarade: list[str] = []
    if arg.arkiv:
        kandidater, avvisade, obesvarade = upptack_arkiv(kommun, klient)
    else:
        kandidater, avvisade = upptack(kommun, klient)
    skriv(kandidater, fil)
    print(sammanfattning(kommun, kandidater, avvisade))
    print("".join(f"Arkivet svarade inte: {fraga}\n" for fraga in obesvarade), end="")


def argument() -> argparse.Namespace:
    tolk = argparse.ArgumentParser(prog="python -m kommunhandlingar.upptack")
    tolk.add_argument("kommunfil", type=Path)
    tolk.add_argument("arbetskatalog", type=Path)
    tolk.add_argument("--arkiv", action="store_true", help="arkivets lista (K16)")
    tolk.add_argument("--start", type=tidsbudget.tidpunkt, help=tidsbudget.START)
    return tolk.parse_args()


if __name__ == "__main__":
    try:
        main(argument())
    except (Konfigurationsfel, Hamtfel) as fel:
        sys.exit(f"Stoppad: {fel}")
