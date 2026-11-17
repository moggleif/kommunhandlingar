"""Krav: K59 i docs/02-KRAV.md, ADR-0085. Test: tests/test_nya_spar.py.

Remisser och yttranden som ett slag av spår över tid: från remissen eller
begäran om yttrande till organets svar och det beslut som svaret gällde.
Motioner står bland initiativärendena (`sparslag.py`).
"""

from kommunhandlingar.webbplats.spar import Slag
from kommunhandlingar.webbplats.sparformer import BOCK, BUBBLA, CIRKEL, FYLLD

REMISSER = Slag(
    id="remisser",
    kolumn="remiss",
    rubrik="Remisser och yttranden",
    sak="Remiss",
    saker="Remisserna",
    antal="remisser",
    faser={
        "remiss": (CIRKEL, "remissen eller begäran om yttrande"),
        "yttrande": (BUBBLA, "organets yttrande"),
        "beslut": (FYLLD + BOCK, "svaret eller beslutet i sista instans"),
    },
    inledning=(
        "<p>Remisser och begäran om yttrande år för år: vad som kom till "
        "organet, vad organet svarade och vad som till sist beslutades. "
        "Varje ikon länkar till sidan i dokumentet som visar steget.</p>"
    ),
    metod=(
        "<p>En remiss står med när organet har ett eget steg: ett yttrande, "
        "ett remissvar eller ett beslut om att svara. Motioner står bland "
        "initiativärendena, och revisionens rapporter bland granskningarna. "
        "Varje steg har en text som står på källans sida, och bygget prövar "
        "det.</p>"
        "<p>En remiss har ett namn på sidan även när källorna kallar den "
        "olika. Där källan inte själv säger att det gäller remissen är "
        "kopplingen en bedömning och ikonen har en streckad ram. Ett år utan "
        "ikon betyder att inget steg står i poolen det året, inte att inget "
        "hände. Sidan visar vad som står var och värderar inte svaren.</p>"
    ),
    adr="0085-lokaler-remisser-och-overenskommelser-som-spar.md",
)
