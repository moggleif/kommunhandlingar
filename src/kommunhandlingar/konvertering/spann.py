"""Krav: K5 i docs/02-KRAV.md och ADR-0040. Test: tests/test_spann.py.

Rubrikens celler ovanför en tabell utan lodräta linjer: vilka kolumner en
rubrik står över, också när den spänner över flera, och hur en rubrik på
flera textrader fogas ihop
(docs/03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer).
"""

from dataclasses import dataclass
from math import inf

from kommunhandlingar.konvertering.falt import Falt
from kommunhandlingar.konvertering.rader import I_LINJE, Rad, mellanrum

# Första kolumnen (0 är etiketten) mot den sista kolumnen och texten.
Celler = dict[int, tuple[int, str]]


@dataclass(frozen=True)
class Fack:
    """Kolumnerna, var etiketterna slutar och sidans lodräta linjer
    (x, överkant, nederkant). Kolumn k:s fack går från föregående kolumns
    högerkant, eller etiketternas slut, till kolumnens egen högerkant."""

    kolumner: list[tuple[float, float]]
    etiketternas_slut: float
    linjer: list[tuple[float, float, float]]

    @property
    def granser(self) -> list[float]:
        return [self.etiketternas_slut] + [x1 for _, x1 in self.kolumner]


def rubrikceller(huvud: list[Rad], fack: Fack) -> list[list[str]] | None:
    """Rubrikraderna som celler; textrader som står tätare än en halv
    teckenhöjd är samma rad. None när rubriken inte går att läsa hel."""
    rader_: list[Celler | None] = []
    for ovre, undre in zip([None, *huvud], huvud, strict=False):
        celler = rubrikrad(undre, fack)
        if ovre and mellanrum(ovre, undre) < min(ovre.hojd, undre.hojd) / 2:
            rader_[-1] = foga(rader_[-1], celler)
        else:
            rader_.append(celler)
    n = len(fack.kolumner)
    if None in rader_ or not tackt(rader_[0], n):
        return None
    return [lista(c, n) for c in rader_]


def rubrikrad(r: Rad, fack: Fack) -> Celler | None:
    """Ett första fält före kolumnerna är etiketten; varje annat fält står
    över en eller flera kolumner, i ordning från vänster."""
    if not r.falt:
        return None
    falt_, celler, slut = r.falt, {}, 0
    if falt_[0].x0 < fack.etiketternas_slut and falt_[0].x1 < fack.kolumner[0][0]:
        celler[0], falt_ = (0, falt_[0].text), falt_[1:]
    for f in falt_:
        s = spann(f, r, fack)
        if s is None or s[0] <= slut:
            return None
        celler[s[0]], slut = (s[1], f.text), s[1]
    return celler if slut else None


def spann(f: Falt, r: Rad, fack: Fack) -> tuple[int, int] | None:
    """Kolumnen vars fack rymmer fältet, eller kolumnerna mellan de lodräta
    linjerna närmast fältet när det står över flera fack."""
    granser = fack.granser
    forsta = sum(1 for g in granser[:-1] if g < f.x0)
    sista = next((k for k, g in enumerate(granser) if k and f.x1 <= g + I_LINJE), None)
    if forsta == 0 or sista is None:
        return None
    return (forsta, forsta) if sista <= forsta else mellan_linjer(f, r, fack)


def mellan_linjer(f: Falt, r: Rad, fack: Fack) -> tuple[int, int] | None:
    """Tabellens kant räknas som linje där linje saknas; utan någon lodrät
    linje bredvid raden går det inte att avgöra."""
    overst = min(o["top"] for o in r.ord)
    nederst = max(o["bottom"] for o in r.ord)
    xs = [x for x, top, bottom in fack.linjer if top < nederst and bottom > overst]
    if not xs:
        return None
    vanster = max((x for x in xs if x <= f.x0), default=-inf)
    hoger = min((x for x in xs if x >= f.x1), default=inf)
    inom = [k for k, (_, x1) in enumerate(fack.kolumner, 1) if vanster < x1 <= hoger]
    return (inom[0], inom[-1]) if inom else None


def foga(ovre: Celler | None, undre: Celler | None) -> Celler | None:
    """Undre radens celler under den övres; en cell som står över andra
    kolumner än cellen ovanför den gör rubriken oläslig."""
    if ovre is None or undre is None:
        return None
    ut = dict(ovre)
    for borjan, (slut, text) in undre.items():
        if borjan in ut and ut[borjan][0] == slut:
            ut[borjan] = (slut, sammanfogad(ut[borjan][1], text))
        elif any(b <= slut and borjan <= s for b, (s, _) in ut.items()):
            return None
        else:
            ut[borjan] = (slut, text)
    return ut


def sammanfogad(ovre: str, undre: str) -> str:
    """`Netto-` och `anslag` blir `Nettoanslag`, `Budget` och `2025` blir
    `Budget 2025`."""
    if ovre.endswith("-") and undre[:1].islower():
        return ovre[:-1] + undre
    return f"{ovre} {undre}"


def tackt(celler: Celler, n: int) -> bool:
    tackta = {k for b, (s, _) in celler.items() if b for k in range(b, s + 1)}
    return tackta >= set(range(1, n + 1))


def lista(celler: Celler, n: int) -> list[str]:
    rad_ = [""] * (n + 1)
    for borjan, (_, text) in celler.items():
        rad_[borjan] = text
    return rad_
