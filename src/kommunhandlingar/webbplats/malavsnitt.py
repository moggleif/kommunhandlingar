"""Krav: K26 och K27 i docs/02-KRAV.md, ADR-0044 och ADR-0045.
Test: tests/test_mal.py.

Ett avsnitt per år på sidan om ett organs mål och direktiv, med varje
rubrik som står med det året och dess källor.
"""

from html import escape

from kommunhandlingar.webbplats.mal import Mal
from kommunhandlingar.webbplats.statusikon import ikon

LUCKA = "<p>Poolen har inga dokument från organet det här året.</p>"
UTAN_MAL = (
    "<p>Poolens dokument från året har inga av nämndens mål eller direktiv; "
    "nämndbudgeten och uppföljningarna kan saknas i poolen.</p>"
)


def arsavsnitt(ar: int, spar: list[list[Mal]], lucka: bool) -> str:
    artiklar = "".join(
        artikel(nr, arets)
        for nr, malen in enumerate(spar)
        for rader in namnen(malen)
        if (arets := [m for m in rader if m.ar == ar])
    )
    text = LUCKA if lucka else artiklar or UTAN_MAL
    return f'<section id="ar-{ar}"><h2>{ar}</h2>{text}</section>'


# Ett spårs rader per rubrik, i den ordning rubrikerna först står.
def namnen(malen: list[Mal]) -> list[list[Mal]]:
    namn: dict[tuple, list[Mal]] = {}
    for mal in malen:
        namn.setdefault(mal.namn, []).append(mal)
    return list(namn.values())


def artikel(nr: int, arets: list[Mal]) -> str:
    forsta = arets[0]
    poster = "".join(f"<li>{post(m)}</li>" for m in arets)
    return (
        f'<article data-slag="{forsta.slag}" data-spar="{nr}">'
        f"<h3>{escape(forsta.rubrik)}</h3><p>{forsta.slag.capitalize()}"
        f"{sparet(forsta)}</p><ul>{poster}</ul></article>"
    )


def sparet(mal: Mal) -> str:
    if not mal.grupp or mal.grupp.casefold() == mal.rubrik.casefold():
        return ""
    tolkad = ", tolkad" if mal.tolkad else ""
    return f". Samma spår som {escape(mal.grupp)}{tolkad}"


def post(mal: Mal) -> str:
    delar = []
    if mal.formulering:
        delar.append(f"<q>{escape(mal.formulering)}</q>")
    if mal.uppfoljning:
        text = escape(mal.status) or "ingen bedömning i källan"
        prognos = " (prognos)" if mal.prognos else ""
        delar.append(f"Status: {ikon(mal.status, mal.prognos)} {text}{prognos}")
    return "<br>".join([*delar, f"Källa: {kallank(mal.kalla)}"])


# Sidan ligger i organets katalog, bredvid årens kataloger, och länken går
# till den första av källans sidor.
def kallank(kalla: str) -> str:
    dokument, sidor = kalla.split("#sida-")
    _, _, datum, fil = dokument.split("/")
    forsta = sidor.split("-")[0]
    lank = dokument.split("/", 1)[1].removesuffix(".md") + f".html#sida-{forsta}"
    text = f"{fil.removesuffix('.md')} {datum}, sida {sidor.replace('-', '–')}"
    return f'<a href="{escape(lank)}">{escape(text)}</a>'
