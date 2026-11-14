"""Krav: K50 i docs/02-KRAV.md, ADR-0073. Test: tests/test_malar.py.

Ett år i taget på sidan om ett organs mål och direktiv: en knapp per år och
ett avsnitt per år, nyast först. Avsnittet har årets antal, ett kort per
spår med årets rader, vad som är nytt och vad som försvann sedan året innan,
och protokollens uppföljningar och dragningar det året. Efter en lucka går
det inte att veta vad som är nytt, så då jämförs inte.
"""

from dataclasses import dataclass
from html import escape

from kommunhandlingar.webbplats.mal import SLAG, Mal
from kommunhandlingar.webbplats.malkort import kallank, rubrik, status
from kommunhandlingar.webbplats.malspar import (
    egenskaper,
    forsta,
    fristaende,
    slagen,
    under,
)
from kommunhandlingar.webbplats.malstatistik import arets_ruta
from kommunhandlingar.webbplats.uppfoljningar import Uppfoljning


@dataclass(frozen=True)
class Underlag:
    spar: list[list[Mal]]
    ar: range
    luckor: set[int]
    uppfoljda: list[Uppfoljning]
    protokollar: set[int]


def aren(underlag: Underlag) -> str:
    knappar = "".join(
        f'<button type="button" data-ar="{a}">{a}</button>' for a in underlag.ar
    )
    avsnitt = "".join(arsavsnitt(underlag, a) for a in reversed(underlag.ar))
    return (
        '<h2 id="aren">Ett år i taget</h2>'
        f'<div class="arval" role="group" aria-label="År" hidden>{knappar}</div>'
        + avsnitt
    )


def arsavsnitt(underlag: Underlag, ar: int) -> str:
    return f'<section class="aret" data-ar="{ar}">{innehall(underlag, ar)}</section>'


def innehall(underlag: Underlag, ar: int) -> str:
    if ar in underlag.luckor:
        return f"<h3>{ar}</h3><p>Lucka i poolen: inga dokument från organet {ar}.</p>"
    if not pa_aret(underlag.spar, ar):
        return f"<h3>{ar}</h3><p>Poolens dokument från organet {ar} har inga mål.</p>"
    malen = [m for spar in underlag.spar for m in spar]
    nya = nytt(underlag, ar)
    return (
        arets_ruta(malen, underlag.uppfoljda, underlag.protokollar, ar)
        + jamforelse(underlag, ar)
        + '<div class="malkort">'
        + "".join(arskort(underlag, nr, ar, nya) for nr in ordnade(underlag, ar))
        + "</div>"
        + protokollen(underlag, ar)
    )


def pa_aret(spar: list[list[Mal]], ar: int) -> set[int]:
    return {nr for nr, malen in enumerate(spar) if any(m.ar == ar for m in malen)}


# Bara året efter ett år som går att jämföra med har något nytt.
def nytt(underlag: Underlag, ar: int) -> set[int]:
    if ar == underlag.ar[0] or ar - 1 in underlag.luckor:
        return set()
    return pa_aret(underlag.spar, ar) - pa_aret(underlag.spar, ar - 1)


def jamforelse(underlag: Underlag, ar: int) -> str:
    if ar == underlag.ar[0]:
        return "<p>Det första året med mål på sidan.</p>"
    if ar - 1 in underlag.luckor:
        return (
            "<p>Året innan är en lucka i poolen, så det går inte att säga vad "
            "som är nytt eller försvann.</p>"
        )
    borta = pa_aret(underlag.spar, ar - 1) - pa_aret(underlag.spar, ar)
    if not borta:
        return f"<p>Inget mål försvann sedan {ar - 1}.</p>"
    lankar = ", ".join(
        f'<a href="#mal-{nr}">{rubrik(arets_rubrik(underlag.spar[nr], ar - 1))}</a>'
        for nr in sorted(borta)
    )
    return f"<p>Försvann sedan {ar - 1}: {lankar}.</p>"


# Fokusområdena står i sitt kommunmåls kort och inte för sig.
def ordnade(underlag: Underlag, ar: int) -> list[int]:
    aret = pa_aret(underlag.spar, ar)
    nummer = [nr for nr, _ in fristaende(underlag.spar) if nr in aret]
    return sorted(nummer, key=lambda nr: nyckel(underlag.spar[nr], ar))


def nyckel(malen: list[Mal], ar: int) -> tuple[int, str]:
    sista = [m for m in malen if m.ar == ar][-1]
    return SLAG.index(sista.slag), sista.rubrik.casefold()


def arskort(underlag: Underlag, nr: int, ar: int, nya: set[int]) -> str:
    malen = underlag.spar[nr]
    arets = [m for m in malen if m.ar == ar]
    markor = [*slagen(arets), *(["nytt"] if nr in nya else [])]
    return (
        f"<article {egenskaper(nr, malen, underlag.ar)}>"
        f'<p class="markor">{" ".join(f"<span>{m}</span>" for m in markor)}</p>'
        f"<h4>{rubrik(arets_rubrik(malen, ar))}</h4>{rader(arets)}"
        f"{fokusomraden(underlag, nr, ar, nya)}</article>"
    )


# Varje formulering står en gång i kortet; varje rad har sin status och källa.
def rader(arets: list[Mal]) -> str:
    formuleringar = dict.fromkeys(m.formulering for m in arets if m.formulering)
    citat = "".join(
        f"<blockquote><q>{escape(f)}</q></blockquote>" for f in formuleringar
    )
    poster = "".join(f"<li>{rad(m)}</li>" for m in arets)
    return f'{citat}<ol class="rader">{poster}</ol>'


def rad(mal: Mal) -> str:
    besked = status(mal) if mal.uppfoljning else "Beslutat"
    return f"{besked}<br>Källa: {kallank(mal.kalla)}"


def fokusomraden(underlag: Underlag, nr: int, ar: int, nya: set[int]) -> str:
    fokus = "".join(
        arskort(underlag, n, ar, nya)
        for n, m in under(underlag.spar, underlag.spar[nr])
        if any(f.ar == ar for f in m)
    )
    if not fokus:
        return ""
    return f'<div class="fokusomraden"><h4>Fokusområden</h4>{fokus}</div>'


# Rubriken som den först står, som i tidslinjen.
def arets_rubrik(malen: list[Mal], ar: int) -> Mal:
    return forsta(malen)[[m for m in malen if m.ar == ar][-1].namn]


def protokollen(underlag: Underlag, ar: int) -> str:
    if not underlag.uppfoljda:
        return ""
    if ar not in underlag.protokollar:
        return f"<p>Inga protokoll med text i poolen {ar}.</p>"
    arets = [u for u in underlag.uppfoljda if u.ar == ar]
    if not arets:
        return f"<p>Protokollen {ar} tar inte upp målen.</p>"
    poster = "".join(
        f"<li>{u.datum} § {u.paragraf}, {u.slag}: {escape(u.rubrik)} "
        f"({kallank(u.kalla)})</li>"
        for u in arets
    )
    return f"<h4>Protokollen om målen {ar}</h4><ul>{poster}</ul>"
