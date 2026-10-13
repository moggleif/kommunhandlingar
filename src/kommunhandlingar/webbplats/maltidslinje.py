"""Krav: K29 i docs/02-KRAV.md, ADR-0050. Test: tests/test_malkort.py.

Tidslinjen på sidan om ett organs mål och direktiv: en rad per spår,
grupperad på slag, och en kolumn per år. Ett år med spåret är en del av
ett band med årets status, och ett år då spåret får en ny rubrik är
markerat. Sist kommer nämndens uppföljningar och dragningar om målen ur
protokollen, med ett streck för år utan protokoll med text.
"""

from html import escape

from kommunhandlingar.webbplats.mal import SLAG, Mal
from kommunhandlingar.webbplats.malspar import (
    arets,
    egenskaper,
    forsta,
    rubriken,
    slagen,
)
from kommunhandlingar.webbplats.statusikon import teckenforklaring
from kommunhandlingar.webbplats.uppfoljningar import Uppfoljning

MARKERINGAR = {"uppföljning": "godkänd uppföljning", "dragning": "dragning om målen"}
KLASS = {"uppföljning": "godkand", "dragning": "dragning"}


def tidslinje(spar: list[list[Mal]], ar: range, luckor: set[int], namnden: str) -> str:
    med_mal = {m.ar for malen in spar for m in malen}
    huvud = "".join(arskolumn(a, a in luckor, a in med_mal) for a in ar)
    grupper = "".join(slagets(slag, spar, ar) for slag in SLAG)
    return (
        f'<h2 id="tidslinje">Tidslinje</h2>{teckenforklaring()}<div class="tabell">'
        '<table class="tidslinje"><thead><tr><th scope="col">Mål eller direktiv'
        f"</th>{huvud}</tr></thead>{grupper}{namnden}</table></div>"
    )


# Ett år utan mål är antingen en lucka i poolen eller ett år då poolens
# dokument inte har några mål.
def arskolumn(ar: int, lucka: bool, med_mal: bool) -> str:
    if lucka:
        return f'<th scope="col" class="lucka">{ar}<br><small>lucka</small></th>'
    if not med_mal:
        return f'<th scope="col">{ar}<br><small>inga mål</small></th>'
    return f'<th scope="col">{ar}</th>'


def slagets(slag: str, spar: list[list[Mal]], ar: range) -> str:
    rader = "".join(
        rad(nr, malen, ar) for nr, malen in enumerate(spar) if malen[-1].slag == slag
    )
    if not rader:
        return ""
    rubrik = f'<th scope="colgroup" colspan="{len(ar) + 1}">{slag.capitalize()}</th>'
    return f'<tbody><tr class="slag">{rubrik}</tr>{rader}</tbody>'


def rad(nr: int, malen: list[Mal], ar: range) -> str:
    rubrik = f'<a href="#mal-{nr}">{escape(rubriken(malen).rubrik)}</a>'
    if len(slagen(malen)) > 1:
        rubrik += f" <small>också {slagen(malen)[0]}</small>"
    celler = "".join(cell(malen, a) for a in ar)
    return f'<tr {egenskaper(nr, malen, ar)}><th scope="row">{rubrik}</th>{celler}</tr>'


def cell(malen: list[Mal], ar: int) -> str:
    finns = {m.ar for m in malen}
    if ar not in finns:
        return "<td></td>"
    klass = (
        "band" + (" start" * (ar - 1 not in finns)) + (" slut" * (ar + 1 not in finns))
    )
    ikon = arets([m for m in malen if m.ar == ar])
    return f'<td class="{klass}">{ny_rubrik(malen, ar)}{ikon}</td>'


def ny_rubrik(malen: list[Mal], ar: int) -> str:
    nya = [m for m in forsta(malen).values() if m.ar == ar and m.ar != malen[0].ar]
    return "".join(
        f'<span class="ny-rubrik" role="img" aria-label="Ny rubrik: '
        f'{escape(m.rubrik)}" title="Ny rubrik: {escape(m.rubrik)}"></span>'
        for m in nya
    )


def namnden_rad(uppfoljda: list[Uppfoljning], protokollar: set[int], ar: range) -> str:
    if not uppfoljda:
        return ""
    celler = "".join(i_namnden(uppfoljda, a, a in protokollar) for a in ar)
    return (
        '<tbody class="namnden"><tr><th scope="row">Nämnden om målen'
        f"{forklaring()}</th>{celler}</tr></tbody>"
    )


def i_namnden(uppfoljda: list[Uppfoljning], ar: int, protokoll: bool) -> str:
    if not protokoll:
        return '<td class="saknas" title="Inga protokoll med text i poolen">–</td>'
    markeringar = " ".join(
        markering(u.slag, f"{u.datum} § {u.paragraf}: {u.rubrik}")
        for u in uppfoljda
        if u.ar == ar
    )
    return f"<td>{markeringar}</td>"


def markering(slag: str, text: str) -> str:
    return (
        f'<span class="{KLASS[slag]}" role="img" aria-label="{escape(text)}" '
        f'title="{escape(text)}"></span>'
    )


def forklaring() -> str:
    return "".join(
        f'<br><small><span class="{KLASS[slag]}"></span> {text}</small>'
        for slag, text in MARKERINGAR.items()
    )
