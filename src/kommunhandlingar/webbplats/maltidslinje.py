"""Krav: K29 i docs/02-KRAV.md, ADR-0050 och ADR-0051. Test: tests/test_malkort.py.

Tidslinjen på sidan om ett organs mål och direktiv: en rad per rubrik i
varje spår, grupperad på slag, och en kolumn per år. Ett år med rubriken
är en del av ett band med årets status. Sist kommer nämndens uppföljningar
och dragningar om målen ur protokollen, med ett streck för år utan
protokoll med text.
"""

from html import escape

from kommunhandlingar.webbplats.mal import SLAG, Mal
from kommunhandlingar.webbplats.malspar import arets, egenskaper, forsta
from kommunhandlingar.webbplats.statusikon import teckenforklaring
from kommunhandlingar.webbplats.uppfoljningar import Uppfoljning

MARKERINGAR = {"uppföljning": "godkänd uppföljning", "dragning": "dragning om målen"}
KLASS = {"uppföljning": "godkand", "dragning": "dragning"}
MARKER = (
    '<p class="teckenforklaring"><span><span class="byte">↳</span> ny rubrik '
    'för samma mål</span> <span><span class="ny-formulering"></span> ny '
    "formulering under samma rubrik</span></p>"
)


def tidslinje(spar: list[list[Mal]], ar: range, luckor: set[int], namnden: str) -> str:
    med_mal = {m.ar for malen in spar for m in malen}
    huvud = "".join(arskolumn(a, a in luckor, a in med_mal) for a in ar)
    grupper = "".join(slagets(slag, spar, ar) for slag in SLAG)
    return (
        f'<h2 id="tidslinje">Tidslinje</h2>{teckenforklaring()}{MARKER}'
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
    slagets_rader = "".join(
        rader(nr, malen, ar) for nr, malen in enumerate(spar) if malen[-1].slag == slag
    )
    if not slagets_rader:
        return ""
    rubrik = f'<th scope="colgroup" colspan="{len(ar) + 1}">{slag.capitalize()}</th>'
    return f'<tbody><tr class="slag">{rubrik}</tr>{slagets_rader}</tbody>'


# Ett spår som bytt rubrik har en rad per rubrik, i den ordning de först
# står, så att det syns vad målet hette vilket år.
def rader(nr: int, malen: list[Mal], ar: range) -> str:
    return "".join(
        rad(nr, malen, [m for m in malen if m.namn == namn], ar)
        for namn in forsta(malen)
    )


def rad(nr: int, malen: list[Mal], rubrikens: list[Mal], ar: range) -> str:
    celler = "".join(cell(rubrikens, a) for a in ar)
    rubrik = rubrikcell(nr, malen, rubrikens[0])
    return f"<tr {egenskaper(nr, malen, ar)}>{rubrik}{celler}</tr>"


def rubrikcell(nr: int, malen: list[Mal], mal: Mal) -> str:
    lank = f'<a href="#mal-{nr}">{escape(mal.rubrik)}</a>'
    tolkad = " <small>tolkad</small>" * (mal.tolkad == "ja")
    slag = f" <small>{mal.slag}</small>" * (mal.slag != malen[-1].slag)
    if mal is malen[0]:
        return f'<th scope="row">{lank}{tolkad}{slag}</th>'
    byte = (
        '<span class="byte" aria-hidden="true">↳</span>'
        f'<span class="dold">Ny rubrik {mal.ar}: </span>'
    )
    return f'<th scope="row" class="ny">{byte}{lank}{tolkad}{slag}</th>'


def cell(malen: list[Mal], ar: int) -> str:
    finns = {m.ar for m in malen}
    if ar not in finns:
        return "<td></td>"
    klass = (
        "band" + (" start" * (ar - 1 not in finns)) + (" slut" * (ar + 1 not in finns))
    )
    ikon = arets([m for m in malen if m.ar == ar])
    return f'<td class="{klass}">{ny_formulering(malen, ar)}{ikon}</td>'


# Samma rubrik kan få en ny formulering; den markeras det år den först står.
def ny_formulering(malen: list[Mal], ar: int) -> str:
    tidigare = [m.formulering for m in malen if m.formulering and m.ar < ar]
    nu = [m.formulering for m in malen if m.formulering and m.ar == ar]
    if not nu or not tidigare or likadan(nu[0], tidigare[-1]):
        return ""
    text = escape(f"Ny formulering: {nu[0]}")
    return (
        f'<span class="ny-formulering" role="img" aria-label="{text}" '
        f'title="{text}"></span>'
    )


def likadan(en: str, annan: str) -> bool:
    return " ".join(en.split()).casefold() == " ".join(annan.split()).casefold()


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
