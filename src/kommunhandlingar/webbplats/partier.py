"""Krav: K37 och K38 i docs/02-KRAV.md, ADR-0058. Test: tests/test_initiativ.py.

En avsändare skrivs med partiets förkortning, eller Alliansen, också när
källan skriver ut namnet. Förkortningen står på källans sida när den står
inom parentes, som i "Initiativärende (S)", eller när partiets namn står
där. Andra avsändare prövas som andra värden.
"""

NAMN = {
    "S": ("Socialdemokrat",),
    "SD": ("Sverigedemokrat",),
    "M": ("Moderat",),
    "KD": ("Kristdemokrat",),
    "L": ("Liberal",),
    "C": ("Centerpartiet",),
    "V": ("Vänsterpartiet",),
    "MP": ("Miljöpartiet",),
    "Alliansen": ("Alliansen", "alliansen", "Allianspartierna", "allianspartierna"),
}


def former(avsandare: str) -> tuple[str, ...]:
    if avsandare not in NAMN:
        return (avsandare,)
    return (f"({avsandare})", *NAMN[avsandare])
