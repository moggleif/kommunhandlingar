"""Krav: K2 i docs/02-KRAV.md, ADR-0011. Test: tests/test_sitevision.py.

Läser en Sitevision-mötessidas filer i sidans ordning, med rubriken för
mötet de står under. Filerna står som länkar i filportleten eller som JSON
i `AppRegistry.registerInitialState` (docs/kallor/kungsbacka.md).
"""

import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import unquote, urljoin

NEDLADDNING = re.compile(r"^/download/(18\.[0-9a-f]+)/")
TILLSTAND = "registerInitialState("


@dataclass(frozen=True)
class Forekomst:
    rubrik: str
    nodid: str
    adress: str
    filnamn: str


class Motessida(HTMLParser):
    def __init__(self, sidadress: str):
        super().__init__()
        self.sidadress = sidadress
        self.rubrik = ""
        self.i_rubrik = False
        self.forekomster: list[Forekomst] = []

    def handle_starttag(self, tagg, attribut):
        if tagg == "h3":
            self.i_rubrik, self.rubrik = True, ""
        if tagg == "a":
            self.fil(dict(attribut).get("href") or "")

    def handle_endtag(self, tagg):
        if tagg == "h3":
            self.i_rubrik, self.rubrik = False, " ".join(self.rubrik.split())

    def handle_data(self, data):
        if self.i_rubrik:
            self.rubrik += data
        for start in hitta_alla(data, TILLSTAND):
            for post in filposter(data, start):
                self.fil(post["uri"])

    def fil(self, uri: str):
        traff = NEDLADDNING.match(uri)
        if traff:
            filnamn = unquote(uri.rsplit("/", 1)[1])
            adress = urljoin(self.sidadress, uri)
            self.forekomster.append(Forekomst(self.rubrik, traff[1], adress, filnamn))


def hitta_alla(text: str, sokt: str) -> list[int]:
    return [traff.end() for traff in re.finditer(re.escape(sokt), text)]


def filposter(text: str, start: int) -> list[dict]:
    tillstand, _ = json.JSONDecoder().raw_decode(text, text.index("{", start))
    return tillstand.get("files", [])


def forekomster(html: str, sidadress: str) -> list[Forekomst]:
    sida = Motessida(sidadress)
    sida.feed(html)
    sida.close()
    return sida.forekomster
