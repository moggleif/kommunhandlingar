"""Krav: K21 i docs/02-KRAV.md, ADR-0026. Test: tests/test_webbplats_sok.py."""

from html import escape

from kommunhandlingar.webbplats.mall import Mall, sida


# Står först i elementet med data-pagefind-body och bär träffens titel och
# filtren utan att själv bli sökbart.
def sokuppgifter(rubrik: str, falt: dict[str, str], organ: str) -> str:
    kvalitet = falt["kvalitet"]
    titel = rubrik + ("" if kvalitet == "full" else f" – kvalitet: {kvalitet}")
    poster = [
        ("meta", "title", titel),
        ("filter", "Organ", organ),
        ("filter", "År", falt["datum"][:4]),
        ("filter", "Typ", falt["typ"]),
        ("filter", "Kvalitet", kvalitet),
    ]
    spann = "".join(
        f'<span data-pagefind-{slag}="{namn}">{escape(varde)}</span>'
        for slag, namn, varde in poster
    )
    return f"<p hidden data-pagefind-ignore>{spann}</p>"


def soksida(mall: Mall) -> str:
    kommuner = ", ".join(
        f'<a href="{k.id}.html">{escape(k.namn)}</a>' for k in mall.kommuner
    )
    innehall = (
        "<noscript><p>Sök kräver JavaScript. Utan det nås dokumenten från "
        f"kommunernas sidor: {kommuner}.</p></noscript>"
        '<div id="sok"></div>'
        '<link rel="stylesheet" href="pagefind/pagefind-ui.css">'
        '<script src="pagefind/pagefind-ui.js"></script>'
        '<script>new PagefindUI({ element: "#sok", showSubResults: true });</script>'
    )
    return sida(mall, "sok.html", "Sök i dokumenten", innehall)
