"""Krav: K5 i docs/02-KRAV.md och ADR-0040. Test: tests/test_spann.py.

Rubrikens celler ovanför en tabell utan lodräta linjer: vilka kolumner en
rubrik står över, också när den spänner över flera, och hur en rubrik på
flera textrader fogas ihop
(docs/03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer).
"""

from dataclasses import dataclass
from itertools import pairwise

from kommunhandlingar.konvertering.falt import Falt
from kommunhandlingar.konvertering.rader import I_LINJE, Rad, mellanrum

BINDEORD = {"och", "eller", "samt"}

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


def rubrikceller(huvud: list[tuple[Rad, Celler]], n: int) -> list[list[str]] | None:
    """Rubrikens textrader med sina celler som rubrikrader; textrader som
    står tätare än en halv teckenhöjd är samma rubrikrad. None när den
    översta textraden inte står över varje kolumn, så att rubriken aldrig
    blir halv, eller när cellerna inte går att foga ihop."""
    if not tackt(huvud[0][1], n):
        return None
    rubrikrader: list[Celler | None] = [huvud[0][1]]
    for (ovre, _), (undre, celler) in pairwise(huvud):
        if mellanrum(ovre, undre) < min(ovre.hojd, undre.hojd) / 2:
            rubrikrader[-1] = fogad(rubrikrader[-1], celler)
        else:
            rubrikrader.append(celler)
    if None in rubrikrader:
        return None
    return [som_lista(c, n) for c in rubrikrader]


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
    linjerna närmast på var sida om fältet när det står över flera fack."""
    granser = fack.granser
    forsta = sum(1 for g in granser[:-1] if g < f.x0)
    sista = next((k for k, g in enumerate(granser) if k and f.x1 <= g + I_LINJE), None)
    if forsta == 0 or sista is None:
        return None
    return (forsta, forsta) if sista <= forsta else mellan_linjer(f, r, fack)


def mellan_linjer(f: Falt, r: Rad, fack: Fack) -> tuple[int, int] | None:
    """Fältet ska stå mitt emellan två linjer som står mellan kolumnerna,
    som en centrerad rubrik i en sammanslagen cell; annars går det inte att
    avgöra."""
    overst = min(o["top"] for o in r.ord)
    nederst = max(o["bottom"] for o in r.ord)
    xs = [x for x, top, bottom in fack.linjer if top < nederst and bottom > overst]
    vanster = max((x for x in xs if x <= f.x0), default=None)
    hoger = min((x for x in xs if x >= f.x1), default=None)
    if (
        vanster is None
        or hoger is None
        or abs(vanster + hoger - f.x0 - f.x1) > 2 * I_LINJE
    ):
        return None
    efter, fore = mellanrummet(vanster, fack, r.hojd), mellanrummet(hoger, fack, r.hojd)
    return None if efter is None or fore is None else (efter + 1, fore)


def mellanrummet(x: float, fack: Fack, marginal: float) -> int | None:
    """k när x står i mellanrummet efter kolumn k (0 är etiketterna), före
    nästa kolumns tal; efter den sista kolumnen högst en teckenhöjd ut."""
    borjan = fack.granser
    slut = [x0 for x0, _ in fack.kolumner] + [borjan[-1] + marginal]
    mellanrum_ = enumerate(zip(borjan, slut, strict=True))
    return next((k for k, (a, b) in mellanrum_ if a < x <= b), None)


def fogad(ovre: Celler | None, undre: Celler) -> Celler | None:
    """Undre textradens celler under den övres; en cell som står över andra
    kolumner än cellen ovanför den gör rubriken oläslig."""
    if ovre is None:
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
    `Budget 2025` och `Kultur-` och `och fritid` blir `Kultur- och fritid`."""
    avstavat = ovre.endswith("-") and undre[:1].islower()
    if avstavat and undre.split()[0] not in BINDEORD:
        return ovre[:-1] + undre
    return f"{ovre} {undre}"


def tackt(celler: Celler, n: int) -> bool:
    tackta = {k for b, (s, _) in celler.items() if b for k in range(b, s + 1)}
    return tackta >= set(range(1, n + 1))


def som_lista(celler: Celler, n: int) -> list[str]:
    rad_ = [""] * (n + 1)
    for borjan, (_, text) in celler.items():
        rad_[borjan] = text
    return rad_
