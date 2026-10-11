"""Krav: K20 i docs/02-KRAV.md, ADR-0025. Test: tests/test_facit.py.

Talen i ett dokument, i text och tabeller, mot facits tal på de sidor där
talen inte är märkta obekräftade (docs/03-ARKITEKTUR.md#facit-för-konverteringen).
"""

from collections import Counter

from kommunhandlingar.facit.lasa import Facit
from kommunhandlingar.facit.rader import siffror
from kommunhandlingar.konvertering.dokument import Resultat
from kommunhandlingar.konvertering.flersidiga import tabeller


def avvikelser(facit: Facit, resultat: Resultat) -> tuple[Counter, Counter]:
    """Talen som saknas i utdatan och talen som tillkommit."""
    utanfor = set(resultat.tal_obekraftade) | set(facit.skannade)
    ut = Counter(utdatans_siffror(resultat, utanfor))
    ratt = Counter(siffror([t for nr, t in facit.tal.items() if nr not in utanfor]))
    return ratt - ut, ut - ratt


def utdatans_siffror(resultat: Resultat, utanfor: set[int]) -> list[str]:
    sidor = enumerate(resultat.sidor, 1)
    texter = [[s.text] for nr, s in sidor if nr not in utanfor]
    csv = [
        r for t in tabeller(resultat.sidor) if t.sida not in utanfor for r in t.rader
    ]
    return siffror(texter + csv)
