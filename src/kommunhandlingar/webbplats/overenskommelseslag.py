"""Krav: K59 i docs/02-KRAV.md, ADR-0085. Test: tests/test_nya_spar.py.

Överenskommelser och vårdval som ett slag av spår över tid: från förslaget
till beslutet, revideringarna, uppföljningen och uppsägningen.
"""

from kommunhandlingar.webbplats.spar import Slag
from kommunhandlingar.webbplats.sparformer import (
    BOCK,
    CIRKEL,
    FYLLD,
    KRYSS,
    RUTER,
    TIMGLAS,
)

OVERENSKOMMELSER = Slag(
    id="overenskommelser",
    kolumn="overenskommelse",
    rubrik="Överenskommelser och vårdval",
    sak="Överenskommelse",
    saker="Överenskommelserna",
    antal="överenskommelser",
    faser={
        "forslag": (CIRKEL, "förslag eller förhandling"),
        "beslut": (FYLLD + BOCK, "beslutad eller godkänd"),
        "revidering": (TIMGLAS, "revidering"),
        "uppfoljning": (RUTER, "uppföljning"),
        "uppsagd": (FYLLD + KRYSS, "uppsagd eller avslutad"),
    },
    inledning=(
        "<p>Överenskommelser med andra huvudmän och staten, och vårdvalets "
        "villkor, år för år: när de föreslogs och beslutades, hur de "
        "reviderades och följdes upp och när de sades upp. Varje ikon länkar "
        "till sidan i dokumentet som visar steget.</p>"
    ),
    metod=(
        "<p>En överenskommelse står med när organet har ett eget steg i sitt "
        "protokoll: ett beslut, ett yttrande, en revidering eller en "
        "uppföljning. Fullmäktiges och styrelsens beslut om den står med när "
        "de finns bland organets handlingar. Hyresavtal står bland "
        "lokalerna och investeringarna, och anställningsavtal står inte "
        "med. Varje steg har en text som står på källans sida, och bygget "
        "prövar det.</p>"
        "<p>En överenskommelse har ett namn på sidan även när källorna kallar "
        "den olika. Där källan inte själv säger att det gäller "
        "överenskommelsen är kopplingen en bedömning och ikonen har en "
        "streckad ram. Ett år utan ikon betyder att inget steg står i poolen "
        "det året, inte att inget hände. Sidan visar vad som står var och "
        "värderar inte överenskommelserna.</p>"
    ),
    adr="0085-lokaler-remisser-och-overenskommelser-som-spar.md",
)
