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
    return sida.filter(
        lambda o: (
            o.get("object_type") != "char"
            or not mellanslag_i_siffra(o, siffror.get(round(o["top"]), []))
        )
    )


def mellanslag_i_siffra(tecken: dict, siffror: list[dict]) -> bool:
    if not tecken["text"].isspace():
        return False
    x0, x1 = tecken["x0"], tecken["x1"]
    halva = (x1 - x0) / 2
    return any(c["x0"] <= x0 and min(x1, c["x1"]) - x0 > halva for c in siffror)
