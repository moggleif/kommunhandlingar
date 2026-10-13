"""Krav: K29 i docs/02-KRAV.md, ADR-0050. Test: tests/test_malkort.py.

Det tidslinjen och korten båda behöver veta om ett spår: dess rubriker,
slag och egenskaper för urvalet, och vad som visas för ett år.
"""

from kommunhandlingar.webbplats.mal import SLAG, Mal
from kommunhandlingar.webbplats.statusikon import bild, ikon

FORETRADE = ("utfall", "rapport", "prognos", "")


def arets(rader: list[Mal]) -> str:
    mal = min(rader, key=lambda m: FORETRADE.index(m.uppfoljning))
    if not mal.uppfoljning:
        return bild("beslutat", "beslutat, utan uppföljning", False)
    return ikon(mal.bedomning, mal.status, mal.prognos)


# Spårets rubriker, med den första raden för varje, i den ordning de först
# står.
def forsta(malen: list[Mal]) -> dict[tuple, Mal]:
    rubriker: dict[tuple, Mal] = {}
    for mal in malen:
        rubriker.setdefault(mal.namn, mal)
    return rubriker


def rubriken(malen: list[Mal]) -> Mal:
    return forsta(malen)[malen[-1].namn]


# Ett spår kan ha varit båda slagen; det senaste står sist.
def slagen(malen: list[Mal]) -> list[str]:
    andra = [s for s in SLAG if s != malen[-1].slag and any(m.slag == s for m in malen)]
    return [*andra, malen[-1].slag]


def egenskaper(nr: int, malen: list[Mal], ar: range) -> str:
    aktiv = "ja" if malen[-1].ar == ar[-1] else "nej"
    bytt = "ja" if len(forsta(malen)) > 1 else "nej"
    return (
        f'data-mal="{nr}" data-slag="{" ".join(slagen(malen))}" '
        f'data-aktiv="{aktiv}" data-bytt="{bytt}"'
    )
