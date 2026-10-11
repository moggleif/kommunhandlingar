"""Krav: K21 i docs/02-KRAV.md, ADR-0026. Test: tests/test_webbplats_sok.py."""

from html import escape

from kommunhandlingar.webbplats.mall import Mall, sida

SOKRUTA = """<div id="sok"></div>
<link rel="stylesheet" href="pagefind/pagefind-ui.css">
<script src="pagefind/pagefind-ui.js"></script>
<script>new PagefindUI({ element: "#sok", showSubResults: true });</script>
"""


# Pagefind indexerar bara det som står i elementet; det dolda stycket bär
# träffens titel och filtren utan att själv bli sökbart.
def sokbar(rubrik: str, falt: dict[str, str], organ: str, text: str) -> str:
    kvalitet = falt["kvalitet"]
    titel = rubrik + ("" if kvalitet == "full" else f" – kvalitet: {kvalitet}")
    poster = [
        ("meta", "title", titel),
        ("filter", "Organ", organ),
        ("filter", "År", falt["datum"][:4]),
        ("filter", "Typ", falt["typ"]),
        ("filter", "Kvalitet", kvalitet),
    ]
    dolt = "".join(
        f'<span data-pagefind-{slag}="{namn}">{escape(varde)}</span>'
        for slag, namn, varde in poster
    )
    return (
        f"<div data-pagefind-body><p hidden data-pagefind-ignore>{dolt}</p>{text}</div>"
    )


def soksida(mall: Mall) -> str:
    kommuner = ", ".join(
        f'<a href="{k.id}.html">{escape(k.namn)}</a>' for k in mall.kommuner
    )
    utan = (
        "<noscript><p>Sök kräver JavaScript. Utan det nås dokumenten från "
        f"kommunernas sidor: {kommuner}.</p></noscript>"
    )
    return sida(mall, "sok.html", "Sök i dokumenten", utan + SOKRUTA)
