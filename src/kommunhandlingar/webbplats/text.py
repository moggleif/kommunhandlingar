"""Krav: K17 i docs/02-KRAV.md, ADR-0021 och ADR-0023.
Test: tests/test_webbplats_dokument.py.
"""

import re
from html import escape

from markdown_it import MarkdownIt

from kommunhandlingar import frontmatter
from kommunhandlingar.frontmatter import lista

# HTML i källan är avslaget, så att inget ur poolen kan bli markup.
LASARE = MarkdownIt("commonmark", {"html": False}).enable(["table", "strikethrough"])
SIDA = re.compile(r"^<!-- sida (\d+) -->$", re.MULTILINE)
OSAKER = '<pre><code class="language-osaker-tabell">'
OSAKER_MARKERAD = (
    '<p class="markering">Osäker tabell, med uppställningen som på sidan:</p>' + OSAKER
)


def pdfsidor(text: str, falt: dict[str, str]) -> str:
    delar = SIDA.split(frontmatter.brodtext(text))
    kvalitet = lista(falt["kvalitet_per_sida"])
    obekraftade = set(lista(falt["tal_obekraftade"]))
    return "".join(
        pdfsida(nr, markdown, kvalitet[int(nr) - 1], nr in obekraftade)
        for nr, markdown in zip(delar[1::2], delar[2::2], strict=True)
    )


def pdfsida(nr: str, markdown: str, kvalitet: str, obekraftad: bool) -> str:
    markering = f"Kvalitet: {kvalitet}." + (
        " Talen på sidan är obekräftade." if obekraftad else ""
    )
    return (
        f'<section class="sida"><h2 id="sida-{nr}">Sida {nr}</h2>'
        f'<p class="markering">{escape(markering)}</p>{rendera(markdown)}</section>'
    )


def rendera(markdown: str) -> str:
    return LASARE.render(markdown).replace(OSAKER, OSAKER_MARKERAD)
