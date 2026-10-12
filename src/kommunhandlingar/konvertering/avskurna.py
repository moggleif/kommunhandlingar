"""Krav: K5 i docs/02-KRAV.md, ADR-0034. Test: tests/test_avskurna.py.

En tabell med linjer är avskuren när linjerna bara ramar in en del av den,
så att ett tal står utanför den på samma höjd
(docs/03-ARKITEKTUR.md#konvertering-och-kvalitet). Den fälls, så att
siffrorna i den märker sidan. Orden delas i fält som i tabellerna utan
lodräta linjer, så att bara ett tal som står för sig självt räknas.
Etiketter utanför räknas inte, som de gör i `talkolumner.etiketter_utanfor`:
text bredvid en tabell är oftast löptext.
"""

from kommunhandlingar.konvertering.falt import falt, radvis
from kommunhandlingar.konvertering.olinjerade import ar_varde, fria
from kommunhandlingar.konvertering.tabeller import mitt


def avskuren(ruta: tuple, ord_: list[dict], upptagna: list[tuple]) -> bool:
    """Ett tal på tabellens höjd bland orden utanför `upptagna`, de
    tabeller med linjer som hittats på sidan."""
    _, top, _, bottom = ruta
    rader = [r for r in radvis(fria(ord_, upptagna)) if top < mitt(r[0])[1] < bottom]
    return any(ar_varde(f) for r in rader for f in falt(r, dela_tvetydiga=True))
