"""Krav: K2, K13 och K16 i docs/02-KRAV.md, ADR-0013 och ADR-0018.
Test: tests/test_upptack.py.

Steg 1: `python -m kommunhandlingar.upptack <kommunfil> <arbetskatalog>
[--arkiv] [--start N]`. Hämtar kommunens källsidor, kör adaptern och
skriver kandidatlistan; med `--arkiv` arkivets lista, som blir tom när
tidsbudgetens mjuka gräns räknat från `--start` är passerad, eller när den
hårda nås under upptäckten. `hamtning.toml` läses från repot som
kommunfilen ligger i.
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
from kommunhandlingar.tidsbudget import Tidsgrans


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
    kommun: konfiguration.Kommun, klient, start: datetime | None
) -> tuple[list[Kandidat], list[Avvisad], list[str]]:
    """Arkivet frågas inte efter den mjuka gränsen och avbryts vid den hårda."""
    if datetime.now(UTC) >= tidsbudget.mjuk_grans(start):
        return [], [], ["väntar på nästa körning; tidsbudgeten är slut"]
    if start:
        tidsbudget.starta_hard_grans(start, datetime.now(UTC))
    try:
        return las_arkivet(kommun, klient)
    except Tidsgrans:
        return [], [], ["avbrutet vid tidsbudgetens hårda gräns"]
    finally:
        tidsbudget.stoppa()


def las_arkivet(
    kommun: konfiguration.Kommun, klient
) -> tuple[list[Kandidat], list[Avvisad], list[str]]:
    kandidater: list[Kandidat] = []
    avvisade: list[Avvisad] = []
    noteringar: list[str] = []
    for kalla in kommun.kallor:
        if kalla.wayback:
            nya, bort, noterat = sitevision_arkiv.upptack(kalla, klient)
            kandidater, avvisade = kandidater + nya, avvisade + bort
            noteringar += noterat
    return ordna_bakat(kandidater, [o.id for o in kommun.organ]), avvisade, noteringar


def sida(klient, adress: str) -> str:
    try:
        return klient.text(adress)
    except Hamtfel as fel:
        raise Hamtfel(fel.orsak, adress) from fel


def skriv(kandidater: list[Kandidat], fil: Path) -> None:
    poster = [asdict(k) | {"datum": k.datum.isoformat()} for k in kandidater]
    fil.write_text(json.dumps(poster, ensure_ascii=False, indent=1) + "\n", "utf-8")


def sammanfattning(
    kommun: konfiguration.Kommun,
    kandidater: list[Kandidat],
    avvisade: list[Avvisad],
    noteringar: tuple[str, ...] | list[str] = (),
) -> str:
    antal = Counter(k.organ for k in kandidater)
    rader = [f"{len(kandidater)} kandidater, {len(avvisade)} filer utan kandidat"]
    rader += [f"  {o.id}: {antal[o.id]}" for o in kommun.organ]
    rader += [f"Ingen kandidat: {a.filnamn} ({a.orsak}) på {a.kalla}" for a in avvisade]
    rader += [f"Arkivet: {notering}" for notering in noteringar]
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
    if arg.arkiv:
        kandidater, avvisade, noteringar = upptack_arkiv(kommun, klient, arg.start)
    else:
        (kandidater, avvisade), noteringar = upptack(kommun, klient), []
    katalog.mkdir(parents=True, exist_ok=True)
    skriv(kandidater, lista(katalog, kommun.id, arg.arkiv))
    print(sammanfattning(kommun, kandidater, avvisade, noteringar))


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
