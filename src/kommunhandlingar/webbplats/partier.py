"""Krav: K37 och K38 i docs/02-KRAV.md, ADR-0058. Test: tests/test_initiativ.py.

En avsändare skrivs med partiets förkortning, eller Alliansen, också när
källan skriver ut namnet. Förkortningen står på källans sida när den står
inom parentes, som i "Initiativärende (S)", eller när partiets namn står
där. Alliansen står också där när de fyra partiernas förkortningar står
där, som i "Initiativärende (M) (L) (C) (KD)". Andra avsändare prövas som
andra värden.
"""

from kommunhandlingar.webbplats.mal import provbar

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


ALLIANSPARTIERNA = ("(M)", "(L)", "(C)", "(KD)")


def former(avsandare: str) -> tuple[str, ...]:
    if avsandare not in NAMN:
        return (avsandare,)
    return (f"({avsandare})", *NAMN[avsandare])


def star_pa(avsandare: str, sidan: str) -> bool:
    if avsandare == "Alliansen" and all(p in sidan for p in ALLIANSPARTIERNA):
        return True
    return any(provbar(f) in sidan for f in former(avsandare))
