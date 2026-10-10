"""Krav: K19 i docs/02-KRAV.md, ADR-0024. Test: tests/test_skarvar.py.

Dokumentets säkra tabeller, där en tabell som fortsätter på nästa sida
slås ihop med fortsättningen (docs/03-ARKITEKTUR.md#tabeller-över-flera-sidor).
En upprepad rubrik tas bort; inga celler slås ihop.
"""

from dataclasses import dataclass, replace

from kommunhandlingar.konvertering.las_sida import Sida
from kommunhandlingar.konvertering.skarv import ar_marginal

KANT = 3


@dataclass(frozen=True)
class Tabell:
    sida: int
    sista_sida: int
    nr: int
    rader: list[list[str]]

    @property
    def namn(self) -> str:
        if self.sista_sida == self.sida:
            return f"{self.sida}-{self.nr}"
        return f"{self.sida}-{self.sista_sida}-{self.nr}"


def tabeller(sidor: list[Sida]) -> list[Tabell]:
    ut: list[Tabell] = []
    for nr, sida in enumerate(sidor, 1):
        egna = sida.tabeller
        if ut and ut[-1].sista_sida == nr - 1 and fortsatter(sidor[nr - 2], sida):
            ut[-1] = forlangd(ut[-1], nr, egna[0])
            egna = egna[1:]
        ut += [Tabell(nr, nr, t_nr, rader) for t_nr, rader in enumerate(egna, 1)]
    return ut


def forlangd(tabell: Tabell, sida: int, rader: list[list[str]]) -> Tabell:
    if rader[0] == tabell.rader[0]:
        rader = rader[1:]
    return replace(tabell, sista_sida=sida, rader=tabell.rader + rader)


def fortsatter(fore: Sida, efter: Sida) -> bool:
    a, b = fore.skarv, efter.skarv
    if a is None or b is None:
        return False
    return (
        len(fore.tabeller[-1][0]) == len(efter.tabeller[0][0])
        and all(abs(x - y) <= KANT for x, y in zip(a.sista, b.forsta, strict=True))
        and all(ar_marginal(rad, b) for rad in a.nedanfor)
        and all(ar_marginal(rad, a) for rad in b.ovanfor)
    )
