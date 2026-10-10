"""Krav: K11 och K15 i docs/02-KRAV.md, ADR-0009 och ADR-0017.
Test: tests/test_datakontroll.py och tests/test_datakontroll_tolkning.py.

Datakontrollen av en CSV i en tabellkatalog (docs/03-ARKITEKTUR.md#tabeller):
namnet, att katalogen har sin `.md`, att sidan är läst ur textlagret eller
tolkad, att numren på sidan följer på varandra och att filen är CSV med
radslut LF. Varje tal i en tolkad CSV ska stå i sidans text. En tabell över
flera sidor (K19) har varje sida läst ur textlagret, och ingen annan tabell
börjar inne i den.
"""

import csv
import re
from pathlib import Path

from kommunhandlingar import frontmatter
from kommunhandlingar.datakontroll_tolkning import talfel

NAMN = re.compile(r"([1-9]\d*)-(?:([1-9]\d*)-)?([1-9]\d*)(\.tolkad)?\.csv")
NAMNEN = "<sida>-<nr>.csv, <sida>-<sista sida>-<nr>.csv eller <sida>-<nr>.tolkad.csv"
TEXTLAGER = {"ok", "tabell-osaker"}


def tabellfel(fil: Path) -> list[str]:
    namn = delar(fil.name)
    if not namn:
        return [f"heter inte {NAMNEN}"]
    md = fil.parent.with_suffix(".md")
    if not md.is_file():
        return [f"tabellkatalogen har ingen {md.name}"]
    sida, sista, nr, tolkad = namn
    formfel = formatfel(fil)
    fel = luckfel(fil, f"{sida}-{nr - 1}{tolkad}.csv", nr) + formfel
    if not tolkad:
        sidor = range(sida, sista + 1)
        return [f for s in sidor for f in sidfel(md, s)] + spannfel(fil, sida, nr) + fel
    return tolkningsfel(md, sida) + fel + ([] if formfel else talfel(fil, md, sida))


def delar(namn: str) -> tuple[int, int, int, str] | None:
    """Första sidan, sista sidan, numret och `.tolkad`, eller None."""
    traff = NAMN.fullmatch(namn)
    if not traff or (traff[2] and (traff[4] or int(traff[2]) <= int(traff[1]))):
        return None
    sida = int(traff[1])
    return sida, int(traff[2] or sida), int(traff[3]), traff[4] or ""


def spannfel(fil: Path, sida: int, nr: int) -> list[str]:
    """En tabell över flera sidor som den här tabellen börjar inne i."""
    for annan in sorted(fil.parent.glob("*-*-*.csv")):
        span = delar(annan.name)
        if span and not span[3] and (span[0], span[2]) < (sida, nr) < (span[1], 0):
            return [f"börjar inne i {annan.name}"]
    return []


def las_lista(md: Path, namn: str) -> list[str] | None:
    try:
        falt = frontmatter.las(md.read_text(encoding="utf-8"))
        return frontmatter.lista(falt[namn])
    except (IndexError, ValueError, KeyError):
        return None  # felet i front matter rapporteras för `.md`


def sidfel(md: Path, sida: int) -> list[str]:
    sidor = las_lista(md, "kvalitet_per_sida")
    if sidor is not None and (sida > len(sidor) or sidor[sida - 1] not in TEXTLAGER):
        return [f"sidan {sida} finns inte eller är inte läst ur textlagret"]
    return []


def tolkningsfel(md: Path, sida: int) -> list[str]:
    tolkade = las_lista(md, "tolkade")
    if tolkade is not None and str(sida) not in tolkade:
        return [f"sidan {sida} står inte i tolkade"]
    return []


def luckfel(fil: Path, foregaende: str, nr: int) -> list[str]:
    if nr == 1 or fil.with_name(foregaende).is_file():
        return []
    return [f"{foregaende} saknas"]


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
