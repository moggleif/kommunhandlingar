"""Krav: K4, ADR-0021. Engångsrättning av poolens text (issue #65).

Escapar texten i varje `.md` som skrevs före version 0.4.0 med samma regel
som konverteringen, utan att hämta PDF:en igen. Sidkommentarerna och
tabellänkarna står kvar, kodblocken får ett staket som räcker, och
pipe-tabellerna byggs om ur sina CSV:er. `pipeline` rörs inte, så att
omkonverteringen (ADR-0019) ser att dokumentet lästes av en äldre version.

Escapningen tål inte att köras två gånger på samma fil, så skriptet tar
filerna som ska rättas som argument. Det stannar om en tabell inte stämmer
med sin CSV eller om den renderade texten inte är den som stod förut.

    python scripts/escapa_poolen.py data/kungsbacka/**/*.md
"""

import csv
import re
import sys
from pathlib import Path

from markdown_it import MarkdownIt

from kommunhandlingar.konvertering import markdown
from kommunhandlingar.konvertering.tabeller import som_markdown

TABELLANK = re.compile(r"\[Tabell \d+-\d+\]\(([^)]+)\)")
GFM = MarkdownIt("commonmark").enable(["table", "strikethrough"])
BLOCK = {"paragraph_open", "paragraph_close", "inline", "fence", "html_block"}
TABELL = {"table_open", "table_close", "thead_open", "thead_close", "tbody_open"}
TABELL |= {"tbody_close", "tr_open", "tr_close", "th_open", "th_close"}
TABELL |= {"td_open", "td_close"}


def escapa(md: Path) -> str:
    text = md.read_text(encoding="utf-8")
    slut = text.index("\n---\n", 4) + 5
    rader, ut, i = text[slut:].split("\n"), [], 0
    while i < len(rader):
        nya, i = nasta(rader, i, md.parent)
        ut += nya
    return text[:slut] + "\n".join(ut)


def nasta(rader: list[str], i: int, katalog: Path) -> tuple[list[str], int]:
    rad = rader[i]
    if rad.startswith("```osaker-tabell"):
        slut = rader.index("```", i + 1)
        staket = markdown.kodstaket("\n".join(rader[i + 1 : slut]))
        return [staket + "osaker-tabell", *rader[i + 1 : slut], staket], slut + 1
    if lank := TABELLANK.fullmatch(rad):
        return tabell(rader, i, katalog / lank.group(1))
    if rad.startswith("<!-- sida ") or not rad:
        return [rad], i + 1
    return [markdown.rad(rad)], i + 1


def tabell(rader: list[str], i: int, csv_fil: Path) -> tuple[list[str], int]:
    slut = i + 2
    while slut < len(rader) and rader[slut].startswith("| "):
        slut += 1
    celler = list(csv.reader(csv_fil.open(encoding="utf-8", newline="")))
    gammal = [[c.replace("|", "\\|").replace("\n", "<br>") for c in r] for r in celler]
    gammal_text = "\n".join(
        "| " + " | ".join(r) + " |"
        for r in [gammal[0], ["---"] * len(gammal[0]), *gammal[1:]]
    )
    if "\n".join(rader[i + 2 : slut]) != gammal_text:
        sys.exit(f"{csv_fil}: tabellen i texten stämmer inte med CSV:n")
    return [rader[i], "", *som_markdown(celler).split("\n")], slut


def styckenas_text(text: str) -> list[str]:
    tokens = GFM.parse(text)
    fel = {t.type for t in tokens} - BLOCK - TABELL
    if fel:
        raise ValueError(f"oväntad struktur: {fel}")
    rader = []
    for nr, t in enumerate(tokens):
        if t.type == "inline" and tokens[nr - 1].type == "paragraph_open":
            rader += synlig(t).split("\n")
    return rader


def synlig(inline) -> str:
    typer = {c.type for c in inline.children} - {"text", "softbreak"}
    if typer - {"link_open", "link_close"}:
        raise ValueError(f"oväntad struktur i ett stycke: {typer}")
    return "".join(
        "\n" if c.type == "softbreak" else c.content for c in inline.children
    )


def textrader(text: str) -> list[str]:
    kropp = text[text.index("\n---\n", 4) + 5 :]
    rader, ut, i = kropp.split("\n"), [], 0
    while i < len(rader):
        if rader[i].startswith("```osaker-tabell"):
            i = rader.index("```", i + 1)
        elif TABELLANK.fullmatch(rader[i]):
            ut.append(rader[i].split("]")[0][1:])
            i += 2
            while i + 1 < len(rader) and rader[i + 1].startswith("| "):
                i += 1
        elif rader[i] and not rader[i].startswith("<!-- sida "):
            ut.append(rader[i].strip())
        i += 1
    return ut


def main(filer: list[str]) -> None:
    for namn in filer:
        md = Path(namn)
        fore = md.read_text(encoding="utf-8")
        efter = escapa(md)
        kropp = efter[efter.index("\n---\n", 4) + 5 :]
        if styckenas_text(kropp) != textrader(fore):
            sys.exit(f"{md}: texten visas inte som den stod")
        md.write_text(efter, encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
