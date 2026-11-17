"""Krav: K36–K38, K42–K44 och K59 i docs/02-KRAV.md. Test: tests/test_navigering.py.

Alla slag av spår över tid, i flikarnas och kolumnernas ordning. Ett
organ får ett slags sida när kommunen har en fil för slaget med rader för
organet (K39).
"""

from kommunhandlingar.webbplats.granskningsslag import GRANSKNINGAR
from kommunhandlingar.webbplats.investeringsslag import INVESTERINGAR
from kommunhandlingar.webbplats.overenskommelseslag import OVERENSKOMMELSER
from kommunhandlingar.webbplats.remissslag import REMISSER
from kommunhandlingar.webbplats.sparslag import (
    DETALJPLANER,
    HANDLINGSPLANER,
    INITIATIV,
    LOKALBEHOV,
    REDOVISNINGAR,
)

SLAGEN = (
    LOKALBEHOV,
    INVESTERINGAR,
    INITIATIV,
    HANDLINGSPLANER,
    REDOVISNINGAR,
    DETALJPLANER,
    GRANSKNINGAR,
    REMISSER,
    OVERENSKOMMELSER,
)
