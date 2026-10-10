"""Krav: K17 i docs/02-KRAV.md, ADR-0022. Test: tests/test_maskning.py.

Personnummer, mobilnummer, e-postadresser och gatuadresser med postnummer
byts mot en markör. Regeln är gemensam för konverteringen, poolkommandot
och datakontrollen, och mönstren tål därför text som redan escapats som
Markdown (ADR-0021) och `<br>` i en tabellcell.
"""

import csv
import io
import re

# Tio siffror utan bindestreck finns bland beloppen och räknas inte.
PERSONNUMMER = re.compile(
    r"(?<![\w-])(?:(?:19|20)(\d{6})-?|(\d{6})[-+])(\d{4})(?![\w-])"
)
# Inte mitt i en följd av korta talgrupper, som i en tabell med belopp; ett
# annat nummer bredvid hindrar inte.
MOBILNUMMER = re.compile(
    r"(?<![\w+-])(?<!\d[,.])(?<!\b\d )(?<!\b\d\d )(?<!\b\d{3} )(?<!\b\d{4} )"
    r"(?:\+46 ?|0)7[02369](?:[- ]?\d){7}(?![\w-])(?! \d{1,4}\b)"
)
EPOST = re.compile(r"(?:[\w.+-]|\\_)+@[\w-]+(?:\.[\w-]+)+")
# Efterleden är en fast lista, så att "platser" eller "vägar" följt av tal
# i en tabellrad inte läses som en adress.
EFTERLED = "väg|vägen|gata|gatan|gränd|gränden|stig|stigen|backe|backen"
EFTERLED += "|torg|torget|allé|alléen|led|leden|lid|liden|plats|platsen"
GATA = rf"\b[A-ZÅÄÖ][\w-]*? ?(?:{EFTERLED})"
NUMMER = r" \d{1,4}(?: ?[A-Z]\b)?(?:,? ?[Ll]gh\.? ?\d+)?"
POSTORT = r"(?=[ ,]*(?:(?:<br>|\n)[ \t]*){0,2}\d{3} ?\d{2} [A-ZÅÄÖ])"
GATUADRESS = re.compile(GATA + NUMMER + POSTORT)


def maska(text: str) -> str:
    text = PERSONNUMMER.sub(personnummer, text)
    text = MOBILNUMMER.sub("(mobilnummer borttaget)", text)
    text = EPOST.sub("(e-post borttagen)", text)
    return GATUADRESS.sub("(adress borttagen)", text)


def maskad_md(text: str) -> str:
    """Brödtexten maskas; front matter rörs inte."""
    huvud, slut, brodtext = text.partition("\n---\n")
    return huvud + slut + maska(brodtext) if slut else text


def maskade_celler(text: str) -> list[list[str]] | None:
    """Cellerna i en CSV maskade, eller None när ingen cell ändras."""
    rader = list(csv.reader(io.StringIO(text)))
    maskade = [[maska(cell) for cell in rad] for rad in rader]
    return None if maskade == rader else maskade


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
