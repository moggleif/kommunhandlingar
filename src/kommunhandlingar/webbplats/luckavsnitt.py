"""Krav: K7 i docs/02-KRAV.md, ADR-0020 och ADR-0062. Test: tests/test_webbplats.py."""

from html import escape

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.luckor import JUSTERING, Lucka, motesnamn
from kommunhandlingar.webbplats.rakning import Organrad

ADR = "/blob/main/docs/decisions/0020-luckor-raknas-fram-lagras-inte.md"


def luckavsnitt(kommun: Kommun, rader: list[Organrad], repo: str) -> str:
    organ = "".join(
        organluckor(kommun, rad) for rad in rader if rad.luckor or rad.tomma_ar
    )
    return (
        "<h2>Luckor</h2>"
        "<p>Sammanträden före den dag sidan byggdes som saknar både kallelse och "
        "handlingar, eller protokoll, när organet har dem vid andra sammanträden. "
        f"Ett protokoll räknas som saknat först {JUSTERING.days} dagar efter mötet. "
        "Ett år utan något dokument mellan organets första och sista står för sig. "
        f'Hur luckorna räknas står i <a href="{escape(repo + ADR)}">ADR-0020</a>.</p>'
        + (organ or "<p>Inga luckor.</p>")
    )


def organluckor(kommun: Kommun, rad: Organrad) -> str:
    poster = "".join(f"<li>{escape(post(lucka))}</li>" for lucka in rad.luckor)
    return (
        f"<h3>{escape(rad.namn)}</h3>"
        f"<p>Källor: {kallor(kommun, rad.id)}.</p>"
        + tomma(rad.tomma_ar)
        + (f"<ul>{poster}</ul>" if poster else "")
    )


def tomma(ar: list[str]) -> str:
    return f"<p>År utan dokument: {escape(', '.join(ar))}.</p>" if ar else ""


def kallor(kommun: Kommun, organ_id: str) -> str:
    return ", ".join(
        f'<a href="{escape(kalla.sidor[organ_id])}">mötessidan</a>'
        + (" och Internet Archive" if organ_id in kalla.wayback else "")
        for kalla in kommun.kallor
        if organ_id in kalla.sidor
    )


def post(lucka: Lucka) -> str:
    mote = motesnamn(lucka.datum, lucka.lopnr)
    return f"{mote}: {', '.join(lucka.saknas)} saknas"
