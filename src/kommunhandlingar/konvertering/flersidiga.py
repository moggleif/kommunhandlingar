"""Krav: K19 i docs/02-KRAV.md, ADR-0024. Test: tests/test_skarvar.py.

Dokumentets säkra tabeller, där en tabell som fortsätter på nästa sida
slås ihop med fortsättningen (docs/03-ARKITEKTUR.md#tabeller-över-flera-sidor).
En upprepad rubrik tas bort; inga celler slås ihop. En sida som lästs med
OCR har ingen skarv och slås aldrig ihop.
"""

from collections import Counter
from dataclasses import dataclass, replace

from kommunhandlingar.konvertering.las_sida import Sida
from kommunhandlingar.konvertering.skarv import Rad, Skarv

KANT = 3
MARGINALENS_SIDOR = 3


@dataclass(frozen=True)
class Sammanslagen:
    sida: int
    sista_sida: int
    nr: int
    rader: list[list[str]]

    @property
    def namn(self) -> str:
        if self.sista_sida == self.sida:
            return f"{self.sida}-{self.nr}"
        return f"{self.sida}-{self.sista_sida}-{self.nr}"


def tabeller(sidor: list[Sida]) -> list[Sammanslagen]:
    marginal = marginalen(sidor)
    ut: list[Sammanslagen] = []
    for nr, sida in enumerate(sidor, 1):
        egna = sida.tabeller
        if nr > 1 and hor_ihop(sidor[nr - 2], sida, marginal):
            ut[-1] = forlangd(ut[-1], nr, egna[0])
            egna = egna[1:]
        ut += [Sammanslagen(nr, nr, t_nr, rader) for t_nr, rader in enumerate(egna, 1)]
    return ut


def marginalen(sidor: list[Sida]) -> set[Rad]:
    """Rader i marginalen som står på samma höjd på minst tre sidor: sidhuvud
    och sidfot."""
    antal = Counter(r for s in sidor if s.skarv for r in s.skarv.marginalen)
    return {r for r, n in antal.items() if n >= MARGINALENS_SIDOR}


def forlangd(tabell: Sammanslagen, sida: int, rader: list[list[str]]) -> Sammanslagen:
    if rader[0] == tabell.rader[0]:
        rader = rader[1:]
    return replace(tabell, sista_sida=sida, rader=tabell.rader + rader)


def hor_ihop(fore: Sida, efter: Sida, marginal: set[Rad]) -> bool:
    """Talen i en tabell ska vara bekräftade på alla sidor eller på ingen."""
    samma_markning = fore.tal_obekraftade == efter.tal_obekraftade
    return samma_markning and fortsatter(fore.skarv, efter.skarv, marginal)


def fortsatter(fore: Skarv | None, efter: Skarv | None, marginal: set[Rad]) -> bool:
    if fore is None or efter is None or not fore.sista_nederst or not efter.forsta:
        return False
    return samma_kolumner(fore.sista, efter.forsta) and marginal.issuperset(
        fore.nedanfor + efter.ovanfor
    )


def samma_kolumner(a: tuple[float, ...], b: tuple[float, ...]) -> bool:
    return len(a) == len(b) and all(
        abs(x - y) <= KANT for x, y in zip(a, b, strict=True)
    )
