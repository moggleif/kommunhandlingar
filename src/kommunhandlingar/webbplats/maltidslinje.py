"""Krav: K29 i docs/02-KRAV.md, ADR-0050 och ADR-0051. Test: tests/test_malkort.py.

Tidslinjen på sidan om ett organs mål och direktiv: en rad per rubrik i
varje spår, grupperad på slag, och en kolumn per år. Ett år med rubriken
är en del av ett band med årets status. Sist kommer nämndens uppföljningar
och dragningar om målen ur protokollen, med ett streck för år utan
protokoll med text.
"""

from html import escape

from kommunhandlingar.webbplats.mal import SLAG, Mal, jamforbar
from kommunhandlingar.webbplats.malspar import arets, egenskaper
from kommunhandlingar.webbplats.statusikon import teckenforklaring
from kommunhandlingar.webbplats.uppfoljningar import Uppfoljning

MARKERINGAR = {"uppföljning": "godkänd uppföljning", "dragning": "dragning om målen"}
KLASS = {"uppföljning": "godkand", "dragning": "dragning"}
BYTEN = (
    '<p class="byten"><span><span aria-hidden="true">↳</span> ny rubrik för '
    'samma mål</span> <span><span class="ny-formulering"></span> ny '
    "formulering under samma rubrik</span></p>"
)


def tidslinje(spar: list[list[Mal]], ar: range, luckor: set[int], namnden: str) -> str:
    med_mal = {m.ar for malen in spar for m in malen}
    huvud = "".join(arskolumn(a, a in luckor, a in med_mal) for a in ar)
    grupper = "".join(slagets(slag, spar, ar) for slag in SLAG)
    return (
        f'<h2 id="tidslinje">Tidslinje</h2>{teckenforklaring()}{BYTEN}'
        '<div class="tabell">'
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
    spar_rader = "".join(
        rader(nr, malen, ar) for nr, malen in enumerate(spar) if malen[-1].slag == slag
    )
    if not spar_rader:
        return ""
    rubrik = f'<th scope="colgroup" colspan="{len(ar) + 1}">{slag.capitalize()}</th>'
    return f'<tbody><tr class="slag">{rubrik}</tr>{spar_rader}</tbody>'


def rader(nr: int, malen: list[Mal], ar: range) -> str:
    egenskap = egenskaper(nr, malen, ar)
    return "".join(
        f"<tr {egenskap}>{rubrikcell(nr, malen, rubrikens[0])}"
        f"{''.join(cell(rubrikens, a) for a in ar)}</tr>"
        for rubrikens in per_rubrik(malen)
    )


# Ett slagbyte med samma rubrik är ingen ny rubrik.
def per_rubrik(malen: list[Mal]) -> list[list[Mal]]:
    rubriker = dict.fromkeys(m.rubrik.casefold() for m in malen)
    return [[m for m in malen if m.rubrik.casefold() == r] for r in rubriker]


def rubrikcell(nr: int, malen: list[Mal], mal: Mal) -> str:
    lank = f'<a href="#mal-{nr}">{escape(mal.rubrik)}</a>'
    tolkad = " <small>tolkad</small>" * (mal.tolkad == "ja")
    slag = f" <small>{mal.slag}</small>" * (mal.slag != malen[-1].slag)
    byte = (
        '<span class="byte" aria-hidden="true">↳</span>'
        f'<span class="dold">Ny rubrik {mal.ar}: </span>'
    ) * (mal is not malen[0])
    return f'<th scope="row">{byte}{lank}{tolkad}{slag}</th>'


def cell(malen: list[Mal], ar: int) -> str:
    finns = {m.ar for m in malen}
    if ar not in finns:
        return "<td></td>"
    klass = (
        "band" + (" start" * (ar - 1 not in finns)) + (" slut" * (ar + 1 not in finns))
    )
    ikon = arets([m for m in malen if m.ar == ar])
    return f'<td class="{klass}">{ny_formulering(malen, ar)}{ikon}</td>'


# En formulering är ny när ingen av årets står året innan med formulering.
def ny_formulering(malen: list[Mal], ar: int) -> str:
    tidigare = [m for m in malen if m.formulering and m.ar < ar]
    nu = [m.formulering for m in malen if m.formulering and m.ar == ar]
    if not nu or not tidigare:
        return ""
    forra = {lik(m.formulering) for m in tidigare if m.ar == tidigare[-1].ar}
    if forra & {lik(f) for f in nu}:
        return ""
    text = escape(f"Ny formulering: {nu[0]}")
    return (
        f'<span class="ny-formulering" role="img" aria-label="{text}" '
        f'title="{text}"></span>'
    )


def lik(formulering: str) -> str:
    return jamforbar(formulering).casefold()


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
