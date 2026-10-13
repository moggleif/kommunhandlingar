"""Krav: K5 i docs/02-KRAV.md, ADR-0016, ADR-0035 och ADR-0037. Test:
tests/test_olinjerade.py, tests/test_mellanrader.py och
tests/test_rubrikrader.py.

Följderna av rader med tal som kan bli en tabell utan lodräta linjer: var
en tabell börjar och slutar, vilka etikettrader den går över, och vilka
rader med årtal som är nästa tabells rubrik
(docs/03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer).
"""

from itertools import pairwise

from kommunhandlingar.konvertering.rader import (
    Rad,
    artalsrad,
    bara_artal,
    etikettrad,
    har_tal,
    mellanrum,
    nara,
    till_vanster,
    uppdela,
)


def foljder(rader_: list[Rad], mest: int) -> list[tuple[int, int]]:
    """Rader med tal i följd, också över högst `mest` etikettrader mellan
    två tabellrader. En rad med bara årtal börjar ingen följd."""
    ut: list[tuple[int, int]] = []
    for i, r in enumerate(rader_):
        if not har_tal(r) or rubrik_till_nasta(rader_, i):
            continue
        if ut and fortsatter(
            rader_[slice(*ut[-1])], rader_[ut[-1][1] - 1 : i + 1], mest
        ):
            ut[-1] = (ut[-1][0], i + 1)
        elif not artalsrad(r):
            ut.append((i, i + 1))
    return ut


def fortsatter(foljden: list[Rad], emellan: list[Rad], mest: int) -> bool:
    """Raden sist i `emellan` fortsätter följden: den når dit över högst
    `mest` etikettrader, och dess etikett står till vänster om talen."""
    return bro(emellan, mest) and till_vanster(foljden, emellan[-1])


def rubrik_till_nasta(rader_: list[Rad], i: int) -> bool:
    """En rad där varje tal är ett årtal och som står närmare raden med tal
    under sig än raden ovanför är nästa tabells rubrikrad."""
    rad_, under = rader_[i], rader_[i + 1 : i + 2]
    if not bara_artal(rad_) or not under or bara_artal(under[0]):
        return False
    narmast = i == 0 or mellanrum(rad_, under[0]) < mellanrum(rader_[i - 1], rad_)
    return har_tal(under[0]) and nara(rad_, under[0]) and narmast


def bro(rader_: list[Rad], mest: int) -> bool:
    ovre, *mellan, undre = rader_
    if len(mellan) > mest or not all(map(etikettrad, mellan)):
        return False
    if mellan and not (uppdela(ovre.falt) and uppdela(undre.falt)):
        return False
    return all(nara(a, b) for a, b in pairwise(rader_))
