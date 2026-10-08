"""Krav: K5 i docs/02-KRAV.md, ADR-0016. Test: tests/test_olinjerade.py.

Ord på en rad delas i fält efter mellanrummen: högst en halv teckenhöjd
är samma fält, minst en hel ett nytt, och däremellan tvetydigt
(docs/03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer). Regeln gäller både
tabellerna utan lodräta linjer och cellerna i tabellerna med linjer.
"""

from dataclasses import dataclass
from itertools import pairwise

from pdfplumber.utils import cluster_objects

RADTOLERANS = 3
SAMMA_FALT = 0.5
NYTT_FALT = 1.0


@dataclass(frozen=True)
class Falt:
    text: str
    x0: float
    x1: float


def radvis(ord_: list[dict]) -> list[list[dict]]:
    """Orden grupperade efter överkanten, var rad sorterad från vänster."""
    grupper = cluster_objects(ord_, "top", RADTOLERANS)
    return [sorted(g, key=lambda o: o["x0"]) for g in grupper]


def falt(ord_: list[dict]) -> list[Falt] | None:
    """Radens fält, eller None när ett mellanrum är tvetydigt."""
    grupper = [[ord_[0]]]
    for vanster, hoger in pairwise(ord_):
        mellanrum = hoger["x0"] - vanster["x1"]
        hojd = max(o["bottom"] - o["top"] for o in (vanster, hoger))
        if mellanrum <= SAMMA_FALT * hojd:
            grupper[-1].append(hoger)
        elif mellanrum >= NYTT_FALT * hojd:
            grupper.append([hoger])
        else:
            return None
    return [
        Falt(" ".join(o["text"] for o in g), g[0]["x0"], g[-1]["x1"]) for g in grupper
    ]
