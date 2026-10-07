"""Krav: K2 och K13 i docs/02-KRAV.md, ADR-0013. Test: tests/test_upptack.py.

Steg 1: `python -m kommunhandlingar.upptack <kommunfil> <arbetskatalog>`.
Hämtar kommunens källsidor, kör adaptern och skriver kandidatlistan.
"""

import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from kommunhandlingar import konfiguration
from kommunhandlingar.adaptrar import sitevision
from kommunhandlingar.fel import Hamtfel, Konfigurationsfel
from kommunhandlingar.hamtning import installningar
from kommunhandlingar.hamtning.klient import Klient
from kommunhandlingar.kandidat import Avvisad, Kandidat, ordna


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


def sida(klient, adress: str) -> str:
    try:
        return klient.text(adress)
    except Hamtfel as fel:
        raise Hamtfel(f"{adress}: {fel}") from fel


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


def main(kommunfil: str, arbetskatalog: str) -> None:
    kommun = konfiguration.las(Path(kommunfil))
    klient = Klient(installningar.las(Path("hamtning.toml")))
    kandidater, avvisade = upptack(kommun, klient)
    katalog = Path(arbetskatalog)
    katalog.mkdir(parents=True, exist_ok=True)
    skriv(kandidater, katalog / f"{kommun.id}.kandidater.json")
    print(sammanfattning(kommun, kandidater, avvisade))


if __name__ == "__main__":
    try:
        main(*sys.argv[1:])
    except (Konfigurationsfel, Hamtfel) as fel:
        sys.exit(f"Stoppad: {fel}")
