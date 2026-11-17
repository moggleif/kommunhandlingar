"""Krav: K59 i docs/02-KRAV.md, ADR-0085. Test: tests/test_nya_spar.py.

Lokaler och investeringar som ett slag av spår över tid: från behovet
eller förslaget till beslutet, arbetet och den färdiga lokalen.
Lokalbehoven (`sparslag.py`) följer en kommuns lokalplan; det här slaget
följer organets egna beslut om lokaler, hyresavtal och investeringar.
"""

from kommunhandlingar.webbplats.spar import Slag
from kommunhandlingar.webbplats.sparformer import (
    CIRKEL,
    FYLLD,
    KLART,
    KRYSS,
    RUTER,
)

INVESTERINGAR = Slag(
    id="investeringar",
    kolumn="investering",
    rubrik="Lokaler och investeringar",
    sak="Investering",
    saker="Investeringarna",
    antal="investeringar",
    faser={
        "behov": (CIRKEL, "behov, förslag eller avsikt"),
        "beslut": (FYLLD, "beslut om lokal, avtal eller investering"),
        "pagar": (RUTER, "på gång"),
        "utfort": (KLART, "klar eller i drift"),
        "avbruten": (FYLLD + KRYSS, "avbruten"),
    },
    inledning=(
        "<p>Lokaler, hyresavtal och investeringar år för år: när behovet "
        "eller förslaget kom, när det beslutades, hur arbetet gick och när "
        "lokalen blev klar eller arbetet avbröts. Varje ikon länkar till "
        "sidan i dokumentet som visar steget.</p>"
    ),
    metod=(
        "<p>Stegen är lästa ur poolens dokument, från vilket organ som helst. "
        "En lokal eller investering står med när den har ett eget ärende i "
        "organets protokoll; budgetens investeringsram i stort och "
        "delegationsbeslut står inte med. Varje steg har en text som står på "
        "källans sida, och bygget prövar det.</p>"
        "<p>En investering har ett namn på sidan även när källorna kallar den "
        "olika. Där källan inte själv säger att det gäller investeringen är "
        "kopplingen en bedömning och ikonen har en streckad ram. Ett år utan "
        "ikon betyder att inget steg står i poolen det året, inte att inget "
        "hände. Sidan visar vad som står var och värderar inte "
        "investeringarna.</p>"
    ),
    adr="0085-lokaler-remisser-och-overenskommelser-som-spar.md",
)
