"""Krav: K15 i docs/02-KRAV.md, ADR-0017. Test: tests/test_figurer.py.

Verktygen för den som tolkar figurerna (docs/03-ARKITEKTUR.md#tolkade-figurer):

- `python -m kommunhandlingar.tolkning lista <data>` skriver arbetslistan,
  varje dokument med sidor i `figurer` som inte står i `tolkade`.
- `python -m kommunhandlingar.tolkning rendera <md> <katalog>` hämtar
  dokumentets original, prövar att sha256 stämmer med front matter och
  sparar de otolkade figursidorna som PNG i katalogen. PDF:en raderas.
  Ett dokument utan otolkade sidor hämtas inte.
"""

import argparse
import hashlib
import sys
import tempfile
from pathlib import Path

import pypdfium2 as pdfium

from kommunhandlingar import frontmatter
from kommunhandlingar.fel import Hamtfel
from kommunhandlingar.hamtning import installningar
from kommunhandlingar.hamtning.klient import Klient

SKALA = 2


class AndratOriginal(Exception):
    """Originalet har inte samma sha256 som när det konverterades."""


def otolkade(falt: dict[str, str]) -> list[int]:
    tolkade = set(frontmatter.lista(falt["tolkade"]))
    return [int(s) for s in frontmatter.lista(falt["figurer"]) if s not in tolkade]


def arbetslista(data: Path) -> list[str]:
    rader = []
    for md in sorted(data.rglob("*.md")):
        sidor = otolkade(frontmatter.las(md.read_text(encoding="utf-8")))
        if sidor:
            rader.append(f"{md.relative_to(data).as_posix()}: {sidor}")
    return rader


def rendera(md: Path, katalog: Path, klient: Klient) -> list[Path]:
    falt = frontmatter.las(md.read_text(encoding="utf-8"))
    if not otolkade(falt):
        return []
    katalog.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tillfallig:
        pdf = Path(tillfallig) / "original.pdf"
        klient.fil(falt["kalla_url"], pdf)
        if hashlib.sha256(pdf.read_bytes()).hexdigest() != falt["sha256"]:
            raise AndratOriginal(f"{md}: originalet har ändrats sedan konverteringen")
        with pdfium.PdfDocument(pdf) as dokument:
            return [spara(dokument, nr, katalog) for nr in otolkade(falt)]


def spara(dokument: pdfium.PdfDocument, nr: int, katalog: Path) -> Path:
    png = katalog / f"{nr}.png"
    dokument[nr - 1].render(scale=SKALA).to_pil().save(png)
    return png


def klient_for(md: Path) -> Klient:
    data = next(p for p in md.resolve().parents if p.name == "data")
    return Klient(installningar.las(data.parent / installningar.VAR))


def argument() -> argparse.Namespace:
    tolk = argparse.ArgumentParser(prog="python -m kommunhandlingar.tolkning")
    kommandon = tolk.add_subparsers(dest="kommando", required=True)
    kommandon.add_parser("lista").add_argument("data", type=Path)
    rendering = kommandon.add_parser("rendera")
    rendering.add_argument("md", type=Path)
    rendering.add_argument("katalog", type=Path)
    return tolk.parse_args()


def main(arg: argparse.Namespace) -> None:
    if arg.kommando == "lista":
        for rad in arbetslista(arg.data):
            print(rad)
        return
    try:
        for png in rendera(arg.md, arg.katalog, klient_for(arg.md)):
            print(png)
    except (AndratOriginal, Hamtfel) as fel:
        sys.exit(f"Stoppad: {fel}")


if __name__ == "__main__":
    main(argument())
