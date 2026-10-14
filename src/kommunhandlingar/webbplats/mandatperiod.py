"""Krav: K29 i docs/02-KRAV.md. Test: tests/test_malkort.py.

Kommunfullmäktiges mandatperioder i tidslinjen. Valet hålls vart fjärde år,
samma år i alla kommuner, och en mandatperiods budgetar gäller de fyra åren
efter valåret: 2019–2022, 2023–2026 och så vidare.
"""

from collections import Counter

FORSTA_ARET = 2023
SKUGGAD = ' class="skuggad"'


def start(ar: int) -> int:
    return ar - (ar - FORSTA_ARET) % 4


def perioder(ar: range) -> Counter[int]:
    return Counter(start(a) for a in ar)


# Varannan period skuggas, så att perioderna skiljs åt i hela tabellen.
def kolumner(ar: range) -> str:
    kolumner = "".join(
        f'<col span="{antal}"{SKUGGAD * ((s - FORSTA_ARET) // 4 % 2 == 0)}>'
        for s, antal in perioder(ar).items()
    )
    return f'<colgroup><col class="rubrik">{kolumner}</colgroup>'


def rubriker(ar: range) -> str:
    celler = "".join(
        f'<th scope="colgroup" colspan="{antal}">Mandatperiod {s}–{s + 3}</th>'
        for s, antal in perioder(ar).items()
    )
    return f'<tr class="perioder"><td></td>{celler}</tr>'
