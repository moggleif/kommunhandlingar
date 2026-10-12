"""Krav: K22 i docs/02-KRAV.md, ADR-0032. Test: tests/test_kalender.py.

Ett organ och organen som hör till det (`hor_till`) får samma färgton, och
tonerna fördelas jämnt runt färgcirkeln i kommunfilens ordning. Färgen bär
aldrig informationen ensam: rutan har alltid organets förkortning.
"""

from kommunhandlingar.konfiguration import Kommun

KANT = "hsl({} 60% 30%)"
NAMND = "hsl({} 70% 80%)"
UTSKOTT = "hsl({} 70% 93%)"


def farger(kommun: Kommun, organ: set[str]) -> dict[str, tuple[str, str]]:
    """Bakgrund och kant för varje organ i `organ`."""
    valda = [o for o in kommun.organ if o.id in organ]
    grupper = list(dict.fromkeys(o.hor_till or o.id for o in valda))
    farg = {}
    for o in valda:
        ton = round(360 * grupper.index(o.hor_till or o.id) / len(grupper))
        bakgrund = UTSKOTT if o.hor_till else NAMND
        farg[o.id] = bakgrund.format(ton), KANT.format(ton)
    return farg


def stil(farg: dict[str, tuple[str, str]]) -> str:
    return "".join(
        f".o-{organ} {{ background: {bakgrund}; border-color: {kant}; }}"
        for organ, (bakgrund, kant) in farg.items()
    )
