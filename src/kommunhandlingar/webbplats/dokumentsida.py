"""Krav: K18 i docs/02-KRAV.md, ADR-0023. Test: tests/test_webbplats_dokument.py."""

from html import escape

from kommunhandlingar.frontmatter import FALT, adresser, lista
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.luckor import motesnamn
from kommunhandlingar.webbplats.mall import Mall, lank, rot, sida, stig
from kommunhandlingar.webbplats.meny import oversiktsnamn
from kommunhandlingar.webbplats.organsida import dokumentrubrik
from kommunhandlingar.webbplats.text import pdfsidor


def dokumentsida(mall: Mall, kommun: Kommun, falt: dict[str, str], text: str) -> str:
    adress = f"{kommun.id}/{falt['adress']}"
    organ = next(o.namn[0] for o in kommun.organ if o.id == falt["organ"])
    mote = motesnamn(falt["datum"], falt["lopnr"])
    organsida = f"{rot(adress)}{kommun.id}/{falt['organ']}.html"
    oversikten = (
        f"{rot(adress)}{kommun.id}.html",
        oversiktsnamn(mall.kommuner, kommun),
    )
    vag = [oversikten, (organsida, organ)]
    md = f"{mall.repo}/blob/main/data/{adress.removesuffix('.html')}.md"
    # En typ utanför kommunfilens `sidor_med_text` visar bara härkomsten, så
    # att en stor pool ryms under GitHub Pages gräns (K18, ADR-0080).
    med_text = kommun.sidor_med_text is None or falt["typ"] in kommun.sidor_med_text
    innehall = (
        stig([*vag, (f"{organsida}#{mote}", mote)])
        + harkomst(falt, md, med_text)
        + (texten(falt, text) if med_text else utan_text(md))
    )
    rubrik = f"{organ} {mote}: {dokumentrubrik(falt)}"
    return sida(mall, adress, rubrik, innehall)


def texten(falt: dict[str, str], text: str) -> str:
    return pdfsidor(text, falt) or "<p>Dokumentet har ingen text.</p>"


def utan_text(md: str) -> str:
    return f"<p>Texten står i {lank(md, 'Markdown-filen i repot')}.</p>"


# Hela front matter, i schemats ordning, med fältens egna namn. Sidorna med
# obekräftade tal länkar till sin rubrik när texten står på sidan.
def harkomst(falt: dict[str, str], md: str, med_text: bool) -> str:
    rader = [(namn, varde(namn, falt[namn], med_text)) for namn in FALT]
    rader.append(("I repot", lank(md, md)))
    poster = "".join(f"<dt>{escape(e)}</dt><dd>{v}</dd>" for e, v in rader)
    return f'<h2>Härkomst</h2><dl class="harkomst">{poster}</dl>'


def varde(namn: str, text: str, med_text: bool) -> str:
    if namn == "kalla_url":
        return ", ".join(lank(a, a) for a in adresser(text))
    if namn == "tal_obekraftade" and med_text:
        sidnr = [escape(s) for s in lista(text)]
        return ", ".join(f'<a href="#sida-{s}">{s}</a>' for s in sidnr) or "[]"
    return escape(text)
