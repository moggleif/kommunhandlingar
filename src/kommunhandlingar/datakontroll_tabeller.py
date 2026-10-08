"""Krav: K11 och K15 i docs/02-KRAV.md, ADR-0009 och ADR-0017.
Test: tests/test_datakontroll.py.

Datakontrollen av en CSV i en tabellkatalog (docs/03-ARKITEKTUR.md#tabeller):
namnet, att katalogen har sin `.md`, att sidan är läst ur textlagret eller
tolkad, att numren på sidan följer på varandra och att filen är CSV med
radslut LF. Varje tal i en tolkad CSV ska stå i sidans text.
"""

import csv
import re
from pathlib import Path

from kommunhandlingar import frontmatter
from kommunhandlingar.konvertering.text import TAL

NAMN = re.compile(r"([1-9]\d*)-([1-9]\d*)(\.tolkad)?\.csv")
TEXTLAGER = {"ok", "tabell-osaker"}
TOLKNING = "<!-- tolkning"
# Ett helt tal i texten, med tusentalsmellanrum: `120` står inte i `1 120`.
TALEN = re.compile(r"(?<![\d,])[-−–]?(?:\d{1,3}(?:[  ]\d{3})+|\d+)(?:,\d+)?(?: ?%)?")


def tabellfel(fil: Path) -> list[str]:
    namn = NAMN.fullmatch(fil.name)
    if not namn:
        return ["heter inte <sida>-<nr>.csv eller <sida>-<nr>.tolkad.csv"]
    md = fil.parent.with_suffix(".md")
    if not md.is_file():
        return [f"tabellkatalogen har ingen {md.name}"]
    sida, nr, tolkad = int(namn[1]), int(namn[2]), namn[3] or ""
    format_ = formatfel(fil)
    fel = luckfel(fil, f"{sida}-{nr - 1}{tolkad}.csv", nr) + format_
    if not tolkad:
        return sidfel(md, sida) + fel
    return tolkningsfel(md, sida) + fel + ([] if format_ else talfel(fil, md, sida))


def lista(md: Path, namn: str) -> list[str] | None:
    try:
        falt = frontmatter.las(md.read_text(encoding="utf-8"))
    except (IndexError, ValueError):
        return None  # felet i front matter rapporteras för `.md`
    return frontmatter.lista(falt.get(namn, "null"))


def sidfel(md: Path, sida: int) -> list[str]:
    sidor = lista(md, "kvalitet_per_sida")
    if sidor is not None and (sida > len(sidor) or sidor[sida - 1] not in TEXTLAGER):
        return [f"sidan {sida} finns inte eller är inte läst ur textlagret"]
    return []


def tolkningsfel(md: Path, sida: int) -> list[str]:
    tolkade = lista(md, "tolkade")
    if tolkade is not None and str(sida) not in tolkade:
        return [f"sidan {sida} står inte i tolkade"]
    return []


def talfel(fil: Path, md: Path, sida: int) -> list[str]:
    text = sidans_text(md.read_text(encoding="utf-8"), sida)
    rader_ = csv.reader(fil.read_text(encoding="utf-8").splitlines())
    celler = [c for rad in rader_ for c in rad]
    return [
        f"talet {c!r} står inte i sidans text"
        for c in celler
        if TAL.fullmatch(c) and not star_i(c, text)
    ]


def star_i(tal: str, text: str) -> bool:
    return tal in TALEN.findall(text)


def sidans_text(md: str, sida: int) -> str:
    """Sidans text i `.md`, utan tolkningen, som står sist på sidan."""
    delar = re.split(r"<!-- sida (\d+) -->", md.split("---\n", 2)[-1])
    text = dict(zip(delar[1::2], delar[2::2], strict=True)).get(str(sida), "")
    return text.split(TOLKNING)[0]


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
