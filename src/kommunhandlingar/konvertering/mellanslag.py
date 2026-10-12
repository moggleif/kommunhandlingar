"""Krav: K4 i docs/02-KRAV.md, ADR-0036. Test: tests/test_mellanslag.py.

Ett mellanslag som börjar inne i en siffra på samma rad och till mer än
hälften täcks av den, som utfyllnaden i en cell ur ett kalkylark, tas
bort innan sidan läses. Det sorteras efter siffran och delar annars talet
där, så att `476,7` blir `4 76,7`
(docs/03-ARKITEKTUR.md#konvertering-och-kvalitet). Ett mellanslag som
börjar före siffran skiljer den från texten framför och står kvar.
"""

from collections import defaultdict

from pdfplumber.page import Page


def utan_mellanslag_i_tal(sida: Page) -> Page:
    siffror = defaultdict(list)
    for c in sida.chars:
        if c["text"].isdigit():
            siffror[round(c["top"])].append(c)
    i_tal = {plats(m) for m in sida.chars if inne_i(m, siffror[round(m["top"])])}
    return sida.filter(
        lambda o: o.get("object_type") != "char" or plats(o) not in i_tal
    )


def inne_i(mellanslag: dict, siffror: list[dict]) -> bool:
    x0, x1 = mellanslag["x0"], mellanslag["x1"]
    halva = (x1 - x0) / 2
    tackt = (c for c in siffror if c["x0"] <= x0 and min(x1, c["x1"]) - x0 > halva)
    return mellanslag["text"].isspace() and any(tackt)


def plats(tecken: dict) -> tuple:
    return tecken["text"], tecken["x0"], tecken["top"]
