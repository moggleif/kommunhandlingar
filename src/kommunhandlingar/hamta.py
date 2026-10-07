"""Krav: K4–K6, K8, K9, K11 och K13 i docs/02-KRAV.md, ADR-0004.
Test: tests/test_hamta.py.

Steg 2: `python -m kommunhandlingar.hamta <kommunfil> <arbetskatalog> [--start N]`.
Läser kandidatlistan från steg 1 och tar kandidaterna i dess ordning, ett
dokument i taget, in i `data/` i samma repo som kommunfilen. Med `--start`
gäller tidsbudgeten i K11, räknad från jobbets start.
"""

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, date, datetime
from importlib.metadata import version
from pathlib import Path

from kommunhandlingar import konfiguration, pool, tidsbudget
from kommunhandlingar.behandla import Steg2, behandla
from kommunhandlingar.fel import Konfigurationsfel
from kommunhandlingar.hamtning import installningar
from kommunhandlingar.hamtning.klient import Klient
from kommunhandlingar.kandidat import Kandidat
from kommunhandlingar.konvertering import ocr
from kommunhandlingar.tidsbudget import Tidsgrans


def las_kandidater(fil: Path) -> list[Kandidat]:
    poster = json.loads(fil.read_text(encoding="utf-8"))
    return [Kandidat(**p | {"datum": date.fromisoformat(p["datum"])}) for p in poster]


def nu() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def kor(steg: Steg2, kandidater: list[Kandidat], mjuk: datetime) -> Counter:
    utfall: Counter = Counter()
    for nr, kandidat in enumerate(kandidater):
        try:
            if steg.tid() >= mjuk:
                utfall["väntar på nästa körning"] += len(kandidater) - nr
                break
            resultat = behandla(steg, kandidat)
        except Tidsgrans:
            print(f"lagd åt sidan vid tidsgränsen: {kandidat.url}", flush=True)
            utfall["lagd åt sidan vid tidsgränsen"] += 1
            utfall["väntar på nästa körning"] += len(kandidater) - nr - 1
            break
        utfall[resultat] += 1
        if resultat.startswith("ej hämtad"):
            print(f"{resultat}: {kandidat.url}", flush=True)
    return utfall


def main(kommunfil: Path, arbetskatalog: Path, start: datetime | None) -> None:
    ocr.kontrollera()
    rot = kommunfil.resolve().parent.parent
    kommun = konfiguration.las(kommunfil)
    kandidater = las_kandidater(arbetskatalog / f"{kommun.id}.kandidater.json")
    steg = Steg2(
        data=rot / "data",
        kommun=kommun.id,
        pool=pool.las(rot / "data", kommun.id),
        klient=Klient(installningar.las(rot / "hamtning.toml")),
        nycklar=frozenset(k.kallnyckel for k in kandidater),
        tid=nu,
        version=f"kommunhandlingar {version('kommunhandlingar')}",
    )
    if start:
        tidsbudget.starta_hard_grans(start, nu())
    try:
        utfall = kor(steg, kandidater, tidsbudget.mjuk_grans(start))
    finally:
        tidsbudget.stoppa()
    for resultat, antal in sorted(utfall.items()):
        print(f"{antal} {resultat}")


def argument() -> argparse.Namespace:
    tolk = argparse.ArgumentParser(prog="python -m kommunhandlingar.hamta")
    tolk.add_argument("kommunfil", type=Path)
    tolk.add_argument("arbetskatalog", type=Path)
    tolk.add_argument(
        "--start",
        type=lambda s: datetime.fromtimestamp(int(s), UTC),
        help="jobbets start i sekunder sedan epoken; tidsbudgeten räknas därifrån",
    )
    return tolk.parse_args()


if __name__ == "__main__":
    arg = argument()
    try:
        main(arg.kommunfil, arg.arbetskatalog, arg.start)
    except Konfigurationsfel as fel:
        sys.exit(f"Stoppad: {fel}")
