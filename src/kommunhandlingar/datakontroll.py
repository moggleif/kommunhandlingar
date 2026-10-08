"""Krav: K11 och K15 i docs/02-KRAV.md, ADR-0006 och ADR-0017.
Test: tests/test_datakontroll.py.

`python -m kommunhandlingar.datakontroll <data>` prövar varje fil under
`data/` mot schemat i docs/03-ARKITEKTUR.md: front matter, sökvägen,
tabellkatalogerna och att inga temporära filer finns kvar. Varje fel
skrivs ut, och kommandot avslutas med fel om något hittades.
"""

import re
import sys
from pathlib import Path

from kommunhandlingar import datakontroll_tolkning, frontmatter
from kommunhandlingar.datakontroll_tabeller import tabellfel
from kommunhandlingar.kandidat import TYPORDNING
from kommunhandlingar.konvertering.kvalitet import KVALITETER, SIDKVALITETER

ALLTID = ("kommun", "organ", "datum", "typ", "kallnyckel", "kalla_url")
ALLTID += ("tidigare_kallnycklar", "hamtad", "pipeline", "kvalitet")
EJ_HAMTAD_NULL = ("sha256", "bytes", "sidor", "konverterad")
EJ_HAMTAD_NULL += ("kvalitet_per_sida", "tal_obekraftade", "figurer", "tolkade")
OBEKRAFTADE = {"ocr", "ej-konverterad"}


def fel_i(data: Path) -> list[str]:
    fel = []
    for fil in sorted(data.rglob("*")):
        if fil.is_file():
            relativ = fil.relative_to(data).as_posix()
            fel += [f"{relativ}: {f}" for f in filfel(data, fil)]
    return fel


def filfel(data: Path, fil: Path) -> list[str]:
    if fil.suffix == ".md" and fil.parent != data:
        return dokumentfel(fil.relative_to(data), fil.read_text(encoding="utf-8"))
    if fil.parent.suffix == ".tabeller":
        return tabellfel(fil)
    return ["oväntad fil, till exempel kvar efter en avbruten körning"]


def dokumentfel(relativ: Path, text: str) -> list[str]:
    try:
        falt = frontmatter.las(text)
    except (IndexError, ValueError):
        return ["front matter går inte att läsa"]
    if tuple(falt) != frontmatter.FALT:
        return ["front matter har inte schemats fält i schemats ordning"]
    fel = [f"{namn} är null" for namn in ALLTID if falt[namn] == "null"]
    if fel:
        return fel
    fel = vardefel(falt) + sokvagsfel(relativ, falt) + statusfel(falt)
    return fel + datakontroll_tolkning.dokumentfel(falt, text)


def vardefel(falt: dict[str, str]) -> list[str]:
    fel = [] if falt["typ"] in TYPORDNING else [f"okänd typ {falt['typ']!r}"]
    if falt["kvalitet"] not in KVALITETER:
        fel.append(f"okänd kvalitet {falt['kvalitet']!r}")
    sidor = frontmatter.lista(falt["kvalitet_per_sida"])
    fel += [f"okänd sidkvalitet {s!r}" for s in sidor if s not in SIDKVALITETER]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", falt["datum"]):
        fel.append(f"datum {falt['datum']!r} är inte ÅÅÅÅ-MM-DD")
    return fel


def sokvagsfel(relativ: Path, falt: dict[str, str]) -> list[str]:
    def med(grund: str, tillagg: str) -> str:
        return grund if tillagg == "null" else f"{grund}-{tillagg}"

    vantad = Path(
        falt["kommun"],
        falt["organ"],
        falt["datum"][:4],
        med(falt["datum"], falt["lopnr"]),
        med(falt["typ"], falt["namn"]) + ".md",
    )
    return [] if relativ == vantad else [f"sökvägen borde vara {vantad}"]


def statusfel(falt: dict[str, str]) -> list[str]:
    if falt["kvalitet"] == "ej-hamtad":
        fel = [f"{n} ska vara null" for n in EJ_HAMTAD_NULL if falt[n] != "null"]
        return fel + (["fel saknas"] if falt["fel"] == "null" else [])
    sidor = frontmatter.lista(falt["kvalitet_per_sida"])
    if falt["sidor"] not in ("null", str(len(sidor))):
        return ["sidor stämmer inte med kvalitet_per_sida"]
    obekraftade = set(frontmatter.lista(falt["tal_obekraftade"]))
    return [
        f"sidan {nr} är {s} men står inte i tal_obekraftade"
        for nr, s in enumerate(sidor, 1)
        if s in OBEKRAFTADE and str(nr) not in obekraftade
    ]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Användning: python -m kommunhandlingar.datakontroll <data>")
    hittade = fel_i(Path(sys.argv[1]))
    print("\n".join(hittade) or "Datakontrollerna gick igenom.")
    sys.exit(1 if hittade else 0)
