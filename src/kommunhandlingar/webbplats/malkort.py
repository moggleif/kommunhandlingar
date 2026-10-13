"""Krav: K29 i docs/02-KRAV.md, ADR-0050. Test: tests/test_malkort.py.

Ett kort per spår på sidan om ett organs mål och direktiv, de som gäller
det senaste året först. Kortet har slaget, åren, den senaste rubriken och
de tidigare, den senaste formuleringen, en remsa med ett fält per år och
en hopfälld historik med varje rad, dess status och källa.
"""

from html import escape

from kommunhandlingar.webbplats.mal import Mal
from kommunhandlingar.webbplats.malspar import (
    arets,
    egenskaper,
    forsta,
    rubriken,
    slagen,
)
from kommunhandlingar.webbplats.statusikon import ikon


def korten(spar: list[list[Mal]], ar: range, luckor: set[int]) -> str:
    ordnade = sorted(enumerate(spar), key=lambda e: (-e[1][-1].ar, -e[1][0].ar, e[0]))
    return (
        '<h2 id="malen">Målen</h2><div class="malkort">'
        + "".join(kort(nr, malen, ar, luckor) for nr, malen in ordnade)
        + "</div>"
    )


def kort(nr: int, malen: list[Mal], ar: range, luckor: set[int]) -> str:
    borjan, slut = malen[0].ar, malen[-1].ar
    aren = str(borjan) if borjan == slut else f"{borjan}–{slut}"
    return (
        f'<article id="mal-{nr}" {egenskaper(nr, malen, ar)}>'
        f'<p class="markor"><span>{" och ".join(slagen(malen))}</span> '
        f"<span>{aren}</span></p>"
        f"<h3>{rubrik(rubriken(malen))}</h3>{tidigare(malen)}{formulering(malen)}"
        f"{remsa(malen, ar, luckor)}{historik(malen)}</article>"
    )


def rubrik(mal: Mal) -> str:
    return escape(mal.rubrik) + (" <small>tolkad</small>" if mal.tolkad else "")


def tidigare(malen: list[Mal]) -> str:
    andra = [rubrik(m) for m in forsta(malen).values() if m.namn != malen[-1].namn]
    return f'<p class="tidigare">Tidigare: {" → ".join(andra)}</p>' if andra else ""


def formulering(malen: list[Mal]) -> str:
    med = [m for m in malen if m.formulering]
    if not med:
        return ""
    return (
        f"<blockquote><q>{escape(med[-1].formulering)}</q> ({med[-1].ar})</blockquote>"
    )


def remsa(malen: list[Mal], ar: range, luckor: set[int]) -> str:
    falten = "".join(falt(malen, a, a in luckor) for a in ar)
    return f'<ol class="remsa" aria-label="År för år">{falten}</ol>'


def falt(malen: list[Mal], ar: int, lucka: bool) -> str:
    arets_rader = [m for m in malen if m.ar == ar]
    etikett = f'<small><span class="dold">{str(ar)[:2]}</span>{str(ar)[2:]}</small>'
    if arets_rader:
        return f'<li title="{ar}">{arets(arets_rader)}{etikett}</li>'
    if lucka:
        return f'<li class="lucka" title="{ar}: lucka i poolen">{etikett}</li>'
    return f'<li class="tom" title="{ar}">{etikett}</li>'


def historik(malen: list[Mal]) -> str:
    blandad = len(slagen(malen)) > 1
    poster = "".join(
        f"<li><b>{m.ar}</b> {rubrik(m)}{f' ({m.slag})' if blandad else ''}"
        f"<br>{post(m)}</li>"
        for m in reversed(malen)
    )
    antal = f"{len(malen)} rad" + ("er" if len(malen) > 1 else "")
    return (
        f"<details><summary>Hela historiken, {antal}</summary>"
        f"<ol>{poster}</ol></details>"
    )


def post(mal: Mal) -> str:
    delar = []
    if mal.formulering:
        delar.append(f"<q>{escape(mal.formulering)}</q>")
    if mal.uppfoljning:
        text = escape(mal.status) or "ingen bedömning i källan"
        prognos = " (prognos)" if mal.prognos else ""
        delar.append(
            f"Status: {ikon(mal.bedomning, mal.status, mal.prognos)} {text}{prognos}"
        )
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
