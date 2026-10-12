"""Krav: K5 i docs/02-KRAV.md, ADR-0034. Test: tests/test_avskurna.py.

En tabell med linjer är avskuren när linjerna bara ramar in en del av den,
så att ett tal står utanför den på samma höjd
(docs/03-ARKITEKTUR.md#konvertering-och-kvalitet). Den fälls, så att
siffrorna i den märker sidan. Orden delas i fält som i tabellerna utan
lodräta linjer, så att ett tal i en mening inte räknas.
"""

from kommunhandlingar.konvertering.falt import falt, radvis
from kommunhandlingar.konvertering.olinjerade import ar_varde, fria


def avskuren(ruta: tuple, ord_: list[dict], rutor: list[tuple]) -> bool:
    x0, top, x1, bottom = ruta
    rader = [r for r in radvis(fria(ord_, rutor)) if top < hojd(r) < bottom]
    falt_ = [f for r in rader for f in falt(r, dela_tvetydiga=True)]
    return any(ar_varde(f) and (f.x1 < x0 or f.x0 > x1) for f in falt_)


def hojd(rad: list[dict]) -> float:
    return (rad[0]["top"] + rad[0]["bottom"]) / 2
