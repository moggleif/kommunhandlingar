"""Krav: K73 i docs/02-KRAV.md, ADR-0100. Test: tests/test_kand_inlasning.py.

`python -m kommunhandlingar.kand_inlasning <data>` skriver, per kommun, hur
många av poolens sidor som har känd inläsning, alltså inte är
`ej-konverterad`, och hur många sidor varje sidkvalitet har. Ett dokument
utan sidor, som inte gick att hämta eller öppna, räknas för sig
(docs/03-ARKITEKTUR.md#känd-inläsning).
"""

import sys
from collections import Counter
from pathlib import Path

from kommunhandlingar import frontmatter
from kommunhandlingar.konvertering.kvalitet import SIDKVALITETER

OLAST = "ej-konverterad"


def rakna(kommun: Path) -> tuple[Counter, int]:
    """Sidorna per kvalitet och antalet dokument utan sidor."""
    sidor, utan_sidor = Counter(), 0
    for md in kommun.rglob("*.md"):
        per_sida = frontmatter.lista(
            frontmatter.las(md.read_text(encoding="utf-8"))["kvalitet_per_sida"]
        )
        sidor.update(per_sida)
        utan_sidor += not per_sida
    return sidor, utan_sidor


def rad(namn: str, sidor: Counter, utan_sidor: int) -> str:
    alla = sum(sidor.values())
    kanda = alla - sidor[OLAST]
    andel = f"{100 * kanda / alla:.2f}".replace(".", ",") if alla else "–"
    per_kvalitet = ", ".join(f"{k} {sidor[k]}" for k in SIDKVALITETER)
    return (
        f"{namn}: {kanda} av {alla} sidor har känd inläsning ({andel} %); "
        f"{per_kvalitet}; {utan_sidor} dokument utan sidor"
    )


def main(data: Path) -> None:
    for kommun in sorted(p for p in data.iterdir() if p.is_dir()):
        print(rad(kommun.name, *rakna(kommun)))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Användning: python -m kommunhandlingar.kand_inlasning <data>")
    main(Path(sys.argv[1]))
