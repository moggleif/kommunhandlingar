"""Krav: K4–K6, K8, K9 och K13 i docs/02-KRAV.md, ADR-0004. Test: tests/test_hamta.py.

Steg 2: `python -m kommunhandlingar.hamta <kommunfil> <arbetskatalog>`.
Läser kandidatlistan från steg 1 och tar kandidaterna i dess ordning, ett
dokument i taget, in i `data/` i samma repo som kommunfilen.
"""

import json
import sys
from collections import Counter
from datetime import UTC, date, datetime
from importlib.metadata import version
from pathlib import Path

from kommunhandlingar import konfiguration, pool
from kommunhandlingar.behandla import Steg2, behandla
from kommunhandlingar.fel import Konfigurationsfel
from kommunhandlingar.hamtning import installningar
from kommunhandlingar.hamtning.klient import Klient
from kommunhandlingar.kandidat import Kandidat
from kommunhandlingar.konvertering import ocr


def las_kandidater(fil: Path) -> list[Kandidat]:
    poster = json.loads(fil.read_text(encoding="utf-8"))
    return [Kandidat(**p | {"datum": date.fromisoformat(p["datum"])}) for p in poster]


def nu() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def kor(steg: Steg2, kandidater: list[Kandidat]) -> Counter:
    utfall: Counter = Counter()
    for kandidat in kandidater:
        resultat = behandla(steg, kandidat)
        utfall[resultat] += 1
        if resultat.startswith("ej hämtad"):
            print(f"{resultat}: {kandidat.url}", flush=True)
    return utfall


def main(kommunfil: Path, arbetskatalog: Path) -> None:
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
    for resultat, antal in sorted(kor(steg, kandidater).items()):
        print(f"{antal} {resultat}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(
            "Användning: python -m kommunhandlingar.hamta <kommunfil> <arbetskatalog>"
        )
    try:
        main(Path(sys.argv[1]), Path(sys.argv[2]))
    except Konfigurationsfel as fel:
        sys.exit(f"Stoppad: {fel}")
