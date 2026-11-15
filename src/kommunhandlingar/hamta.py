"""Krav: K4–K6, K8, K9, K11, K13, K16 och K53 i docs/02-KRAV.md, ADR-0004,
ADR-0018, ADR-0019 och ADR-0077. Test: tests/test_hamta.py,
tests/test_omkonvertering.py och tests/test_versionslogg.py.

Steg 2: `python -m kommunhandlingar.hamta <kommunfil> <arbetskatalog>
[--arkiv] [--start N] [--utan-omkonvertering]`. Läser kandidatlistan från
steg 1, med `--arkiv` arkivets, och tar kandidaterna i dess ordning, ett
dokument i taget, in i `data/` i samma repo som kommunfilen; de som bara
ska konverteras om tas sist. Med `--start` gäller tidsbudgeten i K11,
räknad från jobbets start. Utan `--arkiv` får `versioner/<kommun>.csv` en
rad för varje dokument som kom in nytt, med en ny adress eller med en ny
sha256, också när steg 2 stoppas av ett fel. Med `--utan-omkonvertering`
tas bara det nya och ändrade, så att mötessidorna inte väntar på
omkonverteringen.
"""

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, date, datetime
from importlib.metadata import version
from pathlib import Path

from kommunhandlingar import konfiguration, pool, tidsbudget, versionslogg
from kommunhandlingar.arkivluckor import ensamma
from kommunhandlingar.behandla import Steg2, bara_omkonvertering, behandla
from kommunhandlingar.fel import Konfigurationsfel
from kommunhandlingar.hamtning import installningar
from kommunhandlingar.hamtning.klient import Klient
from kommunhandlingar.kandidat import Kandidat, lista
from kommunhandlingar.konvertering import ocr
from kommunhandlingar.tidsbudget import Tidsgrans


def las_kandidater(fil: Path) -> list[Kandidat]:
    poster = json.loads(fil.read_text(encoding="utf-8"))
    return [Kandidat(**p | lasta(p)) for p in poster]


def lasta(post: dict) -> dict:
    return {"datum": date.fromisoformat(post["datum"]), "delar": tuple(post["delar"])}


def nu() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def ordna(steg: Steg2, kandidater: list[Kandidat]) -> list[Kandidat]:
    return sorted(kandidater, key=lambda k: bara_omkonvertering(steg, k))


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


def steg2(
    steg: Steg2, kandidater: list[Kandidat], start: datetime | None, logg: Path | None
) -> Counter:
    """Loggen skrivs också när steg 2 stoppas, så att ingen version tappas."""
    fore = versionslogg.versioner(steg.pool)
    if start:
        tidsbudget.starta_hard_grans(start, nu())
    try:
        return kor(steg, ordna(steg, kandidater), tidsbudget.mjuk_grans(start))
    finally:
        tidsbudget.stoppa()
        if logg:
            versionslogg.skriv(logg, versionslogg.nya(fore, steg.pool, steg.tid()))


def main(arg: argparse.Namespace) -> None:
    ocr.kontrollera()
    rot = arg.kommunfil.resolve().parent.parent
    kommun = konfiguration.las(arg.kommunfil)
    kandidater = las_kandidater(lista(arg.arbetskatalog, kommun.id, arg.arkiv))
    steg = Steg2(
        data=rot / "data",
        kommun=kommun.id,
        pool=pool.las(rot / "data", kommun.id),
        klient=Klient(installningar.las(rot / "hamtning.toml")),
        nycklar=frozenset(k.kallnyckel for k in kandidater),
        tid=nu,
        version=f"kommunhandlingar {version('kommunhandlingar')}",
        arkiv=arg.arkiv,
        omkonvertera=kommun.omkonvertera and not arg.utan_omkonvertering,
        ensamma=ensamma(kandidater),
    )
    logg = None if arg.arkiv else rot / "versioner" / f"{kommun.id}.csv"
    utfall = steg2(steg, kandidater, arg.start, logg)
    for resultat, antal in sorted(utfall.items()):
        print(f"{antal} {resultat}")


def argument() -> argparse.Namespace:
    tolk = argparse.ArgumentParser(prog="python -m kommunhandlingar.hamta")
    tolk.add_argument("kommunfil", type=Path)
    tolk.add_argument("arbetskatalog", type=Path)
    tolk.add_argument("--arkiv", action="store_true", help="arkivets lista (K16)")
    tolk.add_argument("--start", type=tidsbudget.tidpunkt, help=tidsbudget.START)
    tolk.add_argument(
        "--utan-omkonvertering", action="store_true", help="bara nytt och ändrat (K53)"
    )
    return tolk.parse_args()


if __name__ == "__main__":
    try:
        main(argument())
    except Konfigurationsfel as fel:
        sys.exit(f"Stoppad: {fel}")
