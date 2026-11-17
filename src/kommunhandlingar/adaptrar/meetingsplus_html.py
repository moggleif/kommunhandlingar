"""Krav: K57 i docs/02-KRAV.md, ADR-0080. Test: tests/test_meetingsplus.py.

Läser Meetings Plus sidor: organets sida med alla dess möten, och mötets
sida med dess filer. Mötets egna filer, kallelsen och protokollet, ligger
under mötessidans adress; bilagorna under ärendepunkterna ligger under en
annan. Varje fil har en länk som öppnar den och en som laddar ner den,
och bara den första läses.
"""

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import unquote, urljoin, urlsplit

OPPNA = "downloadMode=open"
FILSOKVAG = re.compile(r"/(?P<flik>agenda|protocol)/(?P<fil>[^/]+)$")
# Länktexten är filnamnet, utom på knappar som "Öppna protokoll".
FILNAMN = re.compile(r"\.\w{2,5}$")
MOTESDATUM = re.compile(r"(?P<ar>\d{4})-(?P<manad>\d{2})-(?P<dag>\d{2})")


@dataclass(frozen=True)
class Fil:
    adress: str
    sokvag: str
    filnamn: str
    # kallelse, protokoll, bilaga eller protokollets bilaga
    del_: str


class Lankar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lankar: list[tuple[str, str]] = []
        self.adress: str | None = None
        self.text = ""

    def handle_starttag(self, tagg, attribut):
        if tagg == "a":
            self.adress, self.text = dict(attribut).get("href"), ""

    def handle_endtag(self, tagg):
        if tagg == "a" and self.adress is not None:
            self.lankar.append((self.adress, " ".join(self.text.split())))
            self.adress = None

    def handle_data(self, data):
        if self.adress is not None:
            self.text += data


def lankar(html: str, sidadress: str) -> list[tuple[str, str]]:
    tolk = Lankar()
    tolk.feed(html)
    tolk.close()
    return [(urljoin(sidadress, a), t) for a, t in tolk.lankar]


def moten(html: str, organsida: str) -> list[str]:
    """Mötessidorna i sidans ordning: adresser direkt under en organsida,
    med ett datum i sista delen. Ett organ som bytt namn har en del av
    mötena under en annan organsida än sin egen (ADR-0080)."""
    funna: dict[str, None] = {}
    for adress, _ in lankar(html, organsida):
        delar = urlsplit(adress)
        utan_fraga = f"{delar.scheme}://{delar.netloc}{delar.path}"
        if under_en_organsida(utan_fraga, organsida) and not delar.query:
            funna[utan_fraga] = None
    return list(funna)


def under_en_organsida(motessida: str, organsida: str) -> bool:
    """Mötessidan har ett datum i sista delen och ligger direkt under en
    sida i samma katalog som organsidan."""
    forald, _, sista = motessida.rstrip("/").rpartition("/")
    organkatalog = organsida.rstrip("/").rpartition("/")[0]
    return forald.rpartition("/")[0] == organkatalog and bool(MOTESDATUM.search(sista))


def filer(html: str, motessida: str) -> list[Fil]:
    mote = urlsplit(motessida).path.rstrip("/")
    funna: dict[str, Fil] = {}
    for adress, text in lankar(html, motessida):
        sokvag = urlsplit(adress).path
        traff = FILSOKVAG.search(sokvag)
        if OPPNA in adress and traff and sokvag not in funna:
            namn = text if FILNAMN.search(text) else unquote(traff["fil"])
            funna[sokvag] = Fil(adress, sokvag, namn, del_(sokvag, mote, traff["flik"]))
    return list(funna.values())


def del_(sokvag: str, mote: str, flik: str) -> str:
    if sokvag.startswith(f"{mote}/"):
        return "kallelse" if flik == "agenda" else "protokoll"
    return "bilaga" if flik == "agenda" else "protokollets bilaga"
