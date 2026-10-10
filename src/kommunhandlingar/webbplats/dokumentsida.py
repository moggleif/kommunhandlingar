"""Krav: K18 i docs/02-KRAV.md, ADR-0023. Test: tests/test_webbplats_dokument.py."""

from html import escape

from kommunhandlingar.frontmatter import FALT, lista
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.luckor import motesnamn
from kommunhandlingar.webbplats.mall import Mall, lank, rot, sida, stig
from kommunhandlingar.webbplats.organsida import dokumentrubrik
from kommunhandlingar.webbplats.text import pdfsidor


def dokumentsida(mall: Mall, kommun: Kommun, falt: dict[str, str], text: str) -> str:
    adress = f"{kommun.id}/{falt['adress']}"
    organ = next(o.namn[0] for o in kommun.organ if o.id == falt["organ"])
    mote = motesnamn(falt["datum"], falt["lopnr"])
    organsida = f"{rot(adress)}{kommun.id}/{falt['organ']}.html"
    vag = [(f"{rot(adress)}{kommun.id}.html", kommun.namn), (organsida, organ)]
    md = f"{mall.repo}/blob/main/data/{adress.removesuffix('.html')}.md"
    innehall = (
        stig([*vag, (f"{organsida}#{mote}", mote)])
        + harkomst(falt, md)
        + (pdfsidor(text, falt) or "<p>Dokumentet har ingen text.</p>")
    )
    rubrik = f"{organ} {mote}: {dokumentrubrik(falt)}"
    return sida(mall, adress, rubrik, innehall)


# Hela front matter, i schemats ordning, med fältens egna namn.
def harkomst(falt: dict[str, str], md: str) -> str:
    rader = [(namn, varde(namn, falt[namn])) for namn in FALT]
    rader.append(("I repot", lank(md, md)))
    poster = "".join(f"<dt>{escape(e)}</dt><dd>{v}</dd>" for e, v in rader)
    return f'<h2>Härkomst</h2><dl class="harkomst">{poster}</dl>'


def varde(namn: str, text: str) -> str:
    if namn == "kalla_url":
        return lank(text, text)
    if namn == "tal_obekraftade":
        sidnr = [escape(s) for s in lista(text)]
        return ", ".join(f'<a href="#sida-{s}">{s}</a>' for s in sidnr) or "[]"
    return escape(text)
