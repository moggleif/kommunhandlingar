"""Krav: K43 i docs/02-KRAV.md, ADR-0066. Test: tests/test_granskningar.py.

Revisionens granskningar som ett slag av spår över tid: från projektplanen
och rapporten i revisionens protokoll till bedömningen, nämndens svar,
informationen i fullmäktige och den uppföljande granskningen.
"""

from kommunhandlingar.webbplats.spar import Slag
from kommunhandlingar.webbplats.sparformer import BUBBLA, CIRKEL, DRAG, FYLLD, RUTER

GRANSKNINGAR = Slag(
    id="granskningar",
    kolumn="granskning",
    rubrik="Granskningar",
    sak="Granskning",
    saker="Granskningarna",
    antal="granskningar",
    faser={
        "projektplan": (CIRKEL, "projektplanen beslutad"),
        "rapport": (FYLLD, "rapporten godkänd av revisionen"),
        "bedomning": (
            f'<rect x="2" y="2" width="12" height="12" {DRAG}/>',
            "revisionens bedömning",
        ),
        "svar": (BUBBLA, "nämndens svar eller åtgärder"),
        "fullmaktige": (
            f'<path d="M2 6.5l6-4.5 6 4.5zM3.5 8v5M8 8v5M12.5 8v5M2 14h12" {DRAG}/>',
            "redovisad för fullmäktige",
        ),
        "uppfoljning": (RUTER, "uppföljande granskning"),
    },
    inledning=(
        "<p>Kommunrevisionens granskningar av nämnden år för år: när "
        "revisionen beslutade projektplanen och godkände rapporten, vad "
        "revisorerna bedömde, hur nämnden svarade, när revisionen berättade "
        "om granskningen i fullmäktige och när den följdes upp. Varje ikon "
        "länkar till sidan i dokumentet som visar steget.</p>"
    ),
    metod=(
        "<p>Revisionen publicerar bara sina protokoll, och där står sällan "
        "bedömningen. Rapporten finns i poolen när den ligger bland "
        "nämndens, kommunstyrelsens eller fullmäktiges handlingar, oftast "
        "som underlag till nämndens svar. Bedömningen står som revisorerna "
        "skriver den; saknas rapporten står ingen bedömning. Granskningar av "
        "hela kommunen står under kommunstyrelsen, och under en nämnd när "
        "nämnden själv svarar. Den grundläggande granskningen, som "
        "revisionen gör av alla nämnder varje år, står med när nämnden har "
        "ett eget steg. Granskningar av bolag, stiftelser och gemensamma "
        "nämnder står inte med. Varje steg har en text som står på källans "
        "sida, och bygget prövar det.</p>"
        "<p>Där källan inte själv säger att det gäller granskningen är "
        "kopplingen en bedömning och ikonen har en streckad ram. Ett år "
        "utan ikon betyder att inget steg står i poolen det året, inte att "
        "inget hände; poolen saknar en del protokoll. Sidan visar vad som "
        "står var och värderar inte granskningarna.</p>"
    ),
    adr="0066-revisionens-granskningar-foljs-per-namnd.md",
    varden={
        "bedomning": (
            r"inte|inte fullt ut|delvis|i stort|i huvudsak|i allt väsentligt",
            "en bedömning",
        )
    },
)
