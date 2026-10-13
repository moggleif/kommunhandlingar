"""Krav: K26 och K27 i docs/02-KRAV.md, ADR-0044 och ADR-0045.
Test: tests/test_mal.py och tests/test_malgrupper.py.

Kontrollerna i målfilen utöver texten på källans sidor: uppföljning och
bedömning, `tolkad` utanför en grupp, samma mål två gånger ur samma
källa, en rubrik med två olika grupper, två rubriker i samma spår samma
år, en grupp som inte är en rubrik utan egen grupp, och samma mål ur både
protokollet och handlingarna från ett möte, där protokollet gäller.
"""

from typing import TYPE_CHECKING

from kommunhandlingar.webbplats.statusikon import IKONER

UPPFOLJNING = ("", "prognos", "utfall", "rapport")

if TYPE_CHECKING:
    from kommunhandlingar.webbplats.mal import Mal


class Kontroll:
    def __init__(self) -> None:
        self.sedda: set[tuple] = set()
        self.kopplingar: dict[tuple, tuple[str, str]] = {}
        self.moten: dict[tuple, bool] = {}
        self.ar: dict[tuple, tuple] = {}

    def prova(self, mal: "Mal") -> None:
        if mal.uppfoljning not in UPPFOLJNING:
            raise ValueError(f"uppföljningen {mal.uppfoljning!r} är okänd")
        tillaten = IKONER if mal.uppfoljning else {""}
        if mal.bedomning not in tillaten or (mal.status and not mal.uppfoljning):
            raise ValueError(
                f"bedömningen {mal.bedomning!r} passar inte uppföljningen "
                f"{mal.uppfoljning!r} med statusen {mal.status!r}"
            )
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
        if self.ar.setdefault((mal.spar, mal.ar), mal.namn) != mal.namn:
            raise ValueError("två rubriker i samma spår samma år")
        mote = (mal.spar, mal.ar, mal.mote)
        if self.moten.setdefault(mote, mal.fran_protokoll) != mal.fran_protokoll:
            raise ValueError(
                "målet står i både protokollet och handlingarna från samma "
                "möte; bara protokollets rad ska stå med"
            )

    # En grupp är en rubrik i filen som inte själv står i en grupp.
    def grupperna(self) -> None:
        egna = {(o, r): g for (o, _, r), (g, _) in self.kopplingar.items()}
        for (organ, _, _), (grupp, _) in self.kopplingar.items():
            if grupp and egna.get((organ, grupp.casefold()), "x") != "":
                raise ValueError(
                    f"gruppen {grupp!r} är ingen rubrik i filen utan egen grupp"
                )
