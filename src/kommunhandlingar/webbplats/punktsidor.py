"""Krav: K54 i docs/02-KRAV.md, ADR-0078. Test: tests/test_punktsidor.py.

Handlingarna följer dagordningen. En punkt börjar på första sidan, efter
förra punktens början, där ett diarienummer efter `Dnr` eller
`Diarienummer` är punktens, och slutar sidan före nästa punkts början.
Sammanfattningen är tjänsteskrivelsens avsnitt om ärendet, som det står.
"""

import re

from kommunhandlingar.diarienummer import MED_ETIKETT, normaliserat
from kommunhandlingar.webbplats.dagordning import Punkt, fogat
from kommunhandlingar.webbplats.text import SIDA

SAMMANFATTNING = re.compile(r"^Sammanfattning(?: av ärendet)?$")
# Det som avslutar sammanfattningen: tjänsteskrivelsens nästa rubrik och
# sidnumret i sidfoten, `1 (2)`.
SLUT = re.compile(r"^(?:Beskrivning av ärendet|Beslutsunderlag|Bakgrund|\d+ \(\d+\))$")


def sidor(text: str) -> dict[int, str]:
    delar = SIDA.split(text)
    return {int(nr): sida for nr, sida in zip(delar[1::2], delar[2::2], strict=True)}


def diarienummer(sida: str) -> list[str]:
    return list(dict.fromkeys(normaliserat(n) for n in MED_ETIKETT.findall(sida)))


# Kallelsen skriver numret utan organets förled: `2026-00543` är
# `KS-2026-00543`.
def ar_punktens(nummer: str, punkt: Punkt) -> bool:
    return nummer == punkt.diarienummer or nummer.endswith("-" + punkt.diarienummer)


def handlingen(handlingar: dict[int, str], punkter: list[Punkt]) -> dict[int, range]:
    borjan, fran = {}, min(handlingar, default=1)
    for punkt in punkter:
        for nr in range(fran, max(handlingar, default=0) + 1):
            if any(ar_punktens(n, punkt) for n in diarienummer(handlingar[nr])):
                borjan[punkt.nummer], fran = nr, nr + 1
                break
    starter = sorted(borjan.items(), key=lambda p: p[1])
    slut = [s for _, s in starter[1:]] + [max(handlingar, default=0) + 1]
    return {nr: range(start, s) for (nr, start), s in zip(starter, slut, strict=True)}


def sammanfattning(handlingar: dict[int, str], omfang: range) -> tuple[str, ...]:
    for nr in omfang:
        rader = handlingar[nr].splitlines()
        rubriker = [i for i, rad in enumerate(rader) if SAMMANFATTNING.match(rad)]
        if rubriker:
            return stycken(rader[rubriker[0] + 1 :])
    return ()


def stycken(rader: list[str]) -> tuple[str, ...]:
    slut = next((i for i, rad in enumerate(rader) if SLUT.match(rad)), len(rader))
    text = "\n".join(rader[:slut])
    return tuple(fogat(s.splitlines()) for s in text.split("\n\n") if s.strip())
