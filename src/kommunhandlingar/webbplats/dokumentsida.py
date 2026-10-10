"""Krav: K17 i docs/02-KRAV.md, ADR-0022. Test: tests/test_webbplats_dokument.py."""

from html import escape

from kommunhandlingar.frontmatter import lista
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.mall import Mall, rot, sida, stig
from kommunhandlingar.webbplats.organsida import motesnamn
from kommunhandlingar.webbplats.text import sidor

HARKOMST = (
    ("kalla_url", "Källa"),
    ("hamtad", "Hämtad"),
    ("konverterad", "Konverterad"),
    ("sidor", "Sidor"),
    ("kvalitet", "Kvalitet"),
    ("fel", "Fel"),
    ("tal_obekraftade", "Sidor med obekräftade tal"),
    ("arenden", "Ärenden"),
    ("kallnyckel", "Källnyckel"),
    ("sha256", "sha256"),
    ("pipeline", "Pipeline"),
)


def dokumentsida(mall: Mall, kommun: Kommun, falt: dict[str, str], text: str) -> str:
    adress = f"{kommun.id}/{falt['adress']}"
    organ = next(o.namn[0] for o in kommun.organ if o.id == falt["organ"])
    mote = motesnamn((falt["datum"], falt["lopnr"]))
    organsida = f"{rot(adress)}{kommun.id}/{falt['organ']}.html"
    vag = [(f"{rot(adress)}{kommun.id}.html", kommun.namn), (organsida, organ)]
    md = f"{mall.repo}/blob/main/data/{adress.removesuffix('.html')}.md"
    innehall = (
        stig([*vag, (f"{organsida}#{mote}", mote)])
        + harkomst(falt, md)
        + (sidor(text, falt) or "<p>Dokumentet har ingen text.</p>")
    )
    rubrik = falt["typ"] + ("" if falt["namn"] == "null" else f" – {falt['namn']}")
    return sida(mall, adress, f"{organ} {mote}: {rubrik}", innehall)


def harkomst(falt: dict[str, str], md: str) -> str:
    rader = [(etikett, varde(namn, falt[namn])) for namn, etikett in HARKOMST]
    rader.append(("I repot", lank(md)))
    poster = "".join(f"<dt>{escape(e)}</dt><dd>{v}</dd>" for e, v in rader)
    return f'<h2>Härkomst</h2><dl class="harkomst">{poster}</dl>'


def varde(namn: str, varde_: str) -> str:
    if varde_ == "null":
        return "–"
    if namn == "kalla_url":
        return lank(varde_)
    if namn == "tal_obekraftade":
        sidnr = lista(varde_)
        return (
            ", ".join(f'<a href="#sida-{escape(s)}">{escape(s)}</a>' for s in sidnr)
            or "inga"
        )
    return escape(varde_)


def lank(adress: str) -> str:
    if not adress.startswith(("https://", "http://")):
        return escape(adress)
    return f'<a href="{escape(adress)}">{escape(adress)}</a>'
