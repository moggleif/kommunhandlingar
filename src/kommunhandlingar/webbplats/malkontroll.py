"""Krav: K26 och K27 i docs/02-KRAV.md, ADR-0044 och ADR-0045.
Test: tests/test_mal.py.

Kontrollerna i målfilen utöver texten på källans sidor: en status utan
ikon, `tolkad` utanför en grupp, samma mål två gånger ur samma källa, en
rubrik med två olika grupper, en grupp som inte är en rubrik, och samma
mål ur både protokollet och handlingarna från ett möte, där protokollet
gäller.
"""

from typing import TYPE_CHECKING

from kommunhandlingar.webbplats.statusikon import STATUS

if TYPE_CHECKING:
    from kommunhandlingar.webbplats.mal import Mal


class Kontroll:
    def __init__(self) -> None:
        self.sedda: set[tuple] = set()
        self.kopplingar: dict[tuple, tuple[str, str]] = {}
        self.moten: dict[tuple, bool] = {}

    def prova(self, mal: "Mal") -> None:
        if mal.status not in STATUS:
            raise ValueError(f"statusen {mal.status!r} har ingen ikon")
        if mal.tolkad not in ("", "ja") or (mal.tolkad and not mal.grupp):
            raise ValueError(f"tolkad {mal.tolkad!r} är varken tom eller ja i en grupp")
        self.mot_tidigare(mal)

    def mot_tidigare(self, mal: "Mal") -> None:
        if (mal.namn, mal.kalla) in self.sedda:
            raise ValueError("målet står redan med samma källa")
        self.sedda.add((mal.namn, mal.kalla))
        koppling = (mal.grupp, mal.tolkad)
        if self.kopplingar.setdefault(mal.namn, koppling) != koppling:
            raise ValueError("rubriken har en annan grupp eller tolkning tidigare")
        mote = (mal.spar, mal.ar, mal.mote)
        if self.moten.setdefault(mote, mal.fran_protokoll) != mal.fran_protokoll:
            raise ValueError(
                "målet står i både protokollet och handlingarna från samma "
                "möte; bara protokollets rad ska stå med"
            )

    def grupperna(self) -> None:
        rubriker = {(organ, rubrik) for organ, _, rubrik in self.kopplingar}
        for (organ, _, _), (grupp, _) in self.kopplingar.items():
            if grupp and (organ, grupp.casefold()) not in rubriker:
                raise ValueError(f"gruppen {grupp!r} är ingen rubrik i filen")
