"""Krav: K29 i docs/02-KRAV.md, ADR-0047. Test: tests/test_malkort.py.

Ett kort per spår på sidan om ett organs mål och direktiv, de som gäller
det senaste året först. Kortet har slaget, åren, den senaste rubriken och
de tidigare, den senaste formuleringen, en remsa med ett fält per år och
en hopfälld historik med varje rad, dess status och källa.
"""

from html import escape

from kommunhandlingar.webbplats.mal import Mal
from kommunhandlingar.webbplats.maltidslinje import arets, egenskaper, rubriken
from kommunhandlingar.webbplats.statusikon import ikon


def korten(spar: list[list[Mal]], ar: range, luckor: set[int]) -> str:
    ordnade = sorted(enumerate(spar), key=lambda e: (-e[1][-1].ar, -e[1][0].ar, e[0]))
    return (
        '<h2 id="malen">Målen</h2><div class="malkort">'
        + "".join(kort(nr, malen, ar, luckor) for nr, malen in ordnade)
        + "</div>"
    )


def kort(nr: int, malen: list[Mal], ar: range, luckor: set[int]) -> str:
    senaste = malen[-1]
    forsta, sista = malen[0].ar, senaste.ar
    aren = str(forsta) if forsta == sista else f"{forsta}–{sista}"
    return (
        f'<article id="mal-{nr}" {egenskaper(nr, malen, ar)}>'
        f'<p class="markor"><span>{senaste.slag}</span> <span>{aren}</span></p>'
        f"<h3>{rubrik(rubriken(malen))}</h3>{tidigare(malen)}{formulering(malen)}"
        f"{remsa(malen, ar, luckor)}{historik(malen)}</article>"
    )


def rubrik(mal: Mal) -> str:
    return escape(mal.rubrik) + (" <small>tolkad</small>" if mal.tolkad else "")


# Spårets andra rubriker, i den ordning de först står.
def tidigare(malen: list[Mal]) -> str:
    forsta: dict[tuple, Mal] = {}
    for mal in malen:
        forsta.setdefault(mal.namn, mal)
    andra = [rubrik(m) for m in forsta.values() if m.namn != malen[-1].namn]
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
    klass = "" if arets_rader else ' class="lucka"' if lucka else ' class="tom"'
    innehall = arets(arets_rader) if arets_rader else ""
    text = "lucka i poolen" if lucka and not arets_rader else ""
    return (
        f'<li{klass} title="{ar}{": " + text if text else ""}">{innehall}'
        f'<small><span class="dold">20</span>{str(ar)[2:]}</small></li>'
    )


def historik(malen: list[Mal]) -> str:
    poster = "".join(
        f"<li><b>{m.ar}</b> {rubrik(m)}<br>{post(m)}</li>" for m in reversed(malen)
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
