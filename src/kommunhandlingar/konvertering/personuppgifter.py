"""Krav: K17 i docs/02-KRAV.md, ADR-0022. Test: tests/test_maskning.py.

Personnummer, mobilnummer, e-postadresser och gatuadresser med postnummer
byts mot en markör. Mönstren tål text som redan escapats som Markdown
(ADR-0021) och `<br>` i en tabellcell, så att samma regel gäller vid
konverteringen, i poolen och i datakontrollen.
"""

import re

# Tio siffror utan bindestreck finns bland beloppen och räknas inte.
PERSONNUMMER = re.compile(
    r"(?<![\w-])(?:(?:19|20)(\d{6})-?|(\d{6})[-+])(\d{4})(?![\w-])"
)
# Inte mitt i en följd av talgrupper, som i en tabell med belopp.
MOBILNUMMER = re.compile(
    r"(?<![\w+,.-])(?<!\d )(?:\+46 ?|0)7[02369](?:[- ]?\d){7}(?![\w-])(?! \d)"
)
EPOST = re.compile(r"(?:[\w.+-]|\\_)+@[\w-]+(?:\.[\w-]+)+")
GATA = r"\b[A-ZÅÄÖ][\w-]*? ?(?:väg|gat|gränd|stig|back|torg|allé|led|lid|plats)\w*"
NUMMER = r" \d{1,4}(?: ?[A-Z]\b)?(?:,? ?[Ll]gh\.? ?\d+)?"
POSTORT = r"(?=[ ,]*(?:(?:<br>|\n)[ \t]*){0,2}\d{3} ?\d{2} [A-ZÅÄÖ])"
GATUADRESS = re.compile(GATA + NUMMER + POSTORT)


def maska(text: str) -> str:
    text = PERSONNUMMER.sub(personnummer, text)
    text = MOBILNUMMER.sub("(mobilnummer borttaget)", text)
    text = EPOST.sub("(e-post borttagen)", text)
    return GATUADRESS.sub("(adress borttagen)", text)


def personnummer(traff: re.Match) -> str:
    datum = traff[1] or traff[2]
    return "(personnummer borttaget)" if giltigt(datum, traff[3]) else traff[0]


def giltigt(datum: str, slut: str) -> bool:
    """Månaden och dagen finns (dag 61–91 i ett samordningsnummer), och
    kontrollsiffran stämmer."""
    manad, dag = int(datum[2:4]), int(datum[4:6])
    finns = 1 <= manad <= 12 and (1 <= dag <= 31 or 61 <= dag <= 91)
    return finns and luhn(datum + slut)


def luhn(siffror: str) -> bool:
    produkter = (int(s) * (2 - i % 2) for i, s in enumerate(siffror))
    return sum(sum(divmod(p, 10)) for p in produkter) % 10 == 0
