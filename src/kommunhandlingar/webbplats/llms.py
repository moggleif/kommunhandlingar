"""Krav: K47 i docs/02-KRAV.md, ADR-0070. Test: tests/test_dokumentindex.py.

`llms.txt` i webbplatsens rot, enligt https://llmstxt.org/: ingången för
en AI, som säger hur poolen ska läsas och pekar på varje kommuns index,
sidor och filer skrivna för hand.
"""

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.sparslag import SLAGEN

INLEDNING = """# kommunhandlingar

> Kommunernas politiska handlingar – kallelser, handlingar och protokoll –
> konverterade från PDF till Markdown, med tabellerna som CSV och källan och
> kvaliteten i varje dokument.

Varje dokument börjar med front matter: varifrån det kom, när det hämtades
och hur väl konverteringen lyckades. Fälten förklaras i
[arkitekturen]({repo}/blob/main/docs/03-ARKITEKTUR.md#front-matter).
`kvalitet` säger hur texten lästes. Tal på sidorna i `tal_obekraftade` är
inte bekräftade och ska inte användas som data. Ett fält utan värde är
`null`; tomt är inte noll. Poolen återger källan och drar inga slutsatser.

Indexet har en rad per dokument i JSON Lines, med hela front matter.
`fil` är sökvägen i repot, och Markdown-filen finns på
`{repo}/raw/main/<fil>`. `sida` är dokumentets sida på den här webbplatsen,
och tabellerna i `tabeller` ligger bredvid den i
`<sida utan .html>.tabeller/`.
"""


def llms(mall: Mall) -> str:
    avsnitt = [INLEDNING.format(repo=mall.repo)]
    avsnitt += [kommunavsnitt(mall, kommun) for kommun in mall.kommuner]
    return "\n".join(avsnitt)


def kommunavsnitt(mall: Mall, kommun: Kommun) -> str:
    lankar = [
        f"[Index över dokumenten]({kommun.id}/index.jsonl)",
        f"[Översikt]({kommun.id}.html)",
    ]
    lankar += [f"[{o.namn[0]}]({kommun.id}/{o.id}.html)" for o in kommun.organ]
    lankar += [
        f"[{rubrik}]({mall.repo}/raw/main/{katalog}/{kommun.id}.csv): skriven för hand"
        for katalog, rubrik in handskrivna(mall, kommun.id)
    ]
    return f"## {kommun.namn}\n\n" + "".join(f"- {lank}\n" for lank in lankar)


def handskrivna(mall: Mall, kommun: str) -> list[tuple[str, str]]:
    filer = [
        ("kalender", "Kalendern", mall.kalendrar),
        ("mal", "Mål och direktiv", mall.malen),
        ("uppfoljningar", "Uppföljningar av målen", mall.uppfoljningar),
    ]
    filer += [(s.id, s.rubrik, mall.spar.get(s.id, {})) for s in SLAGEN]
    filer.append(("projekt", "Detaljplanernas projekt", mall.projekt))
    return [(katalog, rubrik) for katalog, rubrik, finns in filer if kommun in finns]
