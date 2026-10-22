"""Krav: K26, K27 och K35 i docs/02-KRAV.md, ADR-0044, ADR-0045 och ADR-0056.
Test: tests/test_mal.py, tests/test_malgrupper.py och tests/test_fokusomraden.py.

Kontrollerna i målfilen utöver texten på källans sidor: uppföljning och
bedömning, `tolkad` utanför en grupp, samma mål två gånger ur samma
källa, en rubrik med två olika grupper eller huvudmål, två rubriker i
samma spår samma år i samma dokument, en grupp som inte är en rubrik utan
egen grupp, ett huvudmål som inte är ett kommunmål utan egen grupp, och
samma mål ur både protokollet och handlingarna från ett möte, där
protokollet gäller.
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
        koppling = (mal.grupp, mal.tolkad, mal.huvudmal)
        if self.kopplingar.setdefault(mal.namn, koppling) != koppling:
            raise ValueError(
                "rubriken har en annan grupp, tolkning eller huvudmål tidigare"
            )
        # Budgeten och uppföljningen kan skriva samma mål på olika sätt.
        if self.ar.setdefault((mal.spar, mal.ar, mal.dokument), mal.namn) != mal.namn:
            raise ValueError("två rubriker i samma spår samma år i samma dokument")
        mote = (mal.spar, mal.ar, mal.mote)
        if self.moten.setdefault(mote, mal.fran_protokoll) != mal.fran_protokoll:
            raise ValueError(
                "målet står i både protokollet och handlingarna från samma "
                "möte; bara protokollets rad ska stå med"
            )

    # En grupp är en rubrik i filen som inte själv står i en grupp, och ett
    # huvudmål ett kommunmål utan grupp.
    def grupperna(self) -> None:
        egna = {(o, r): g for (o, _, r), (g, _, _) in self.kopplingar.items()}
        kommunmal = {
            (o, r)
            for (o, s, r), (g, _, _) in self.kopplingar.items()
            if s == "kommunmål" and not g
        }
        for (organ, _, _), (grupp, _, huvudmal) in self.kopplingar.items():
            if grupp and egna.get((organ, grupp.casefold()), "x") != "":
                raise ValueError(
                    f"gruppen {grupp!r} är ingen rubrik i filen utan egen grupp"
                )
            if huvudmal and (organ, huvudmal.casefold()) not in kommunmal:
                raise ValueError(
                    f"huvudmålet {huvudmal!r} är inget kommunmål i filen utan grupp"
                )
