"""Krav: K11 i docs/02-KRAV.md, ADR-0009. Test: tests/test_datakontroll.py.

Datakontrollen av en CSV i en tabellkatalog (docs/03-ARKITEKTUR.md#tabeller):
namnet, att katalogen har sin `.md`, att sidan är läst ur textlagret, att
numren på sidan följer på varandra och att filen är CSV med radslut LF.
"""

import csv
import re
from pathlib import Path

from kommunhandlingar import frontmatter

NAMN = re.compile(r"([1-9]\d*)-([1-9]\d*)\.csv")
TEXTLAGER = {"ok", "tabell-osaker"}


def tabellfel(fil: Path) -> list[str]:
    namn = NAMN.fullmatch(fil.name)
    if not namn:
        return ["heter inte <sida>-<nr>.csv"]
    md = fil.parent.with_suffix(".md")
    if not md.is_file():
        return [f"tabellkatalogen har ingen {md.name}"]
    sida, nr = int(namn[1]), int(namn[2])
    return sidfel(md, sida) + luckfel(fil, sida, nr) + formatfel(fil)


def sidfel(md: Path, sida: int) -> list[str]:
    try:
        falt = frontmatter.las(md.read_text(encoding="utf-8"))
        sidor = frontmatter.lista(falt["kvalitet_per_sida"])
    except (IndexError, ValueError, KeyError):
        return []  # felet i front matter rapporteras för `.md`
    if sida > len(sidor) or sidor[sida - 1] not in TEXTLAGER:
        return [f"sidan {sida} finns inte eller är inte läst ur textlagret"]
    return []


def luckfel(fil: Path, sida: int, nr: int) -> list[str]:
    if nr == 1 or fil.with_name(f"{sida}-{nr - 1}.csv").is_file():
        return []
    return [f"{sida}-{nr - 1}.csv saknas"]


def formatfel(fil: Path) -> list[str]:
    data = fil.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        return ["börjar med BOM"]
    if b"\r\n" in data:
        return ["radslut CRLF"]
    try:
        rader = list(csv.reader(data.decode("utf-8").splitlines(keepends=True)))
    except (UnicodeDecodeError, csv.Error) as fel:
        return [f"inte CSV i UTF-8: {fel}"]
    if len({len(rad) for rad in rader}) > 1:
        return ["raderna har olika många fält"]
    return []
