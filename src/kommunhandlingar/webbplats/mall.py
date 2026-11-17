"""Krav: K14, K18, K22, K26, K27, K28, K36, K37, K39, K51 och K60 i docs/02-KRAV.md,
ADR-0074 och ADR-0083 för temat. Test: tests/test_webbplats.py och
tests/test_tema.py."""

from dataclasses import dataclass, field
from datetime import datetime
from html import escape

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.mal import Mal
from kommunhandlingar.webbplats.meny import GEMENSAM, meny, sajtnamn
from kommunhandlingar.webbplats.projekt import Projekt
from kommunhandlingar.webbplats.spar import Steg
from kommunhandlingar.webbplats.uppfoljningar import Uppfoljning

# Varje färg har ett ljust och ett mörkt värde (ADR-0074). En webbläsare utan
# light-dark() får de ljusa värdena. Knappen och det valda temat kommer från
# Giffås gemensamma meny (ADR-0083).
STIL = """
:root { color-scheme: light dark;
  --text: light-dark(#1a1a1a, #e4e6ea); --bakgrund: light-dark(#fff, #15171b);
  --kant: light-dark(#999, #5f6672); --yta: light-dark(#f5f6f8, #22262d);
  --linje: light-dark(#d9dde5, #3a404b); --dampad: light-dark(#5b6475, #a8b0bd);
  --accent: light-dark(#1d5d73, #7cc4dc); --band: light-dark(#e3eef2, #1e3942);
  --uppnatt: light-dark(#1a6b2a, #72d083); --delvis: light-dark(#8a5a00, #e6b552);
  --ej: light-dark(#b00020, #ff8a94); }
@supports not (color: light-dark(black, white)) {
  :root { color-scheme: light; --text: #1a1a1a; --bakgrund: #fff; --kant: #999;
    --yta: #f5f6f8; --linje: #d9dde5; --dampad: #5b6475; --accent: #1d5d73;
    --band: #e3eef2; --uppnatt: #1a6b2a; --delvis: #8a5a00; --ej: #b00020; } }
:root { --sajtaccent: var(--accent); --sajtyta: var(--bakgrund); --sajtkant: 0; }
body { font-family: system-ui, sans-serif; max-width: 72rem; margin: 0 auto;
       padding: 0 1rem; line-height: 1.5; color: var(--text);
       background: var(--bakgrund); }
/* En bred tabell rullar i sin egen ruta, aldrig hela sidan; det som ligger
   absolut i tabellen stannar i rutan (K14). */
.tabell, .sida { overflow-x: auto; position: relative; }
table { border-collapse: collapse; margin-bottom: 2rem; }
th, td { border: 1px solid var(--kant); padding: 0.25rem 0.6rem; vertical-align: top; }
th[scope="row"] { text-align: left; }
td.tal { text-align: right; font-variant-numeric: tabular-nums; }
dl.harkomst { display: grid; grid-template-columns: max-content 1fr; gap: 0 1rem; }
dl.harkomst dd { margin: 0; overflow-wrap: anywhere; }
.sida { border-top: 1px solid var(--kant); margin-top: 2rem; }
.sida p { white-space: pre-wrap; }
.markering { font-weight: bold; }
pre { background: var(--yta); padding: 0.5rem; overflow-x: auto; }
.status { display: inline-block; padding: 0.1em; line-height: 0;
          border: 1px solid transparent; border-radius: 0.3em; cursor: help; }
.status.prognos { border: 1px dashed currentColor; }
.status.uppnatt { color: var(--uppnatt); } .status.delvis { color: var(--delvis); }
.status.ej { color: var(--ej); }
.status.ingen, .status.beslutat { color: var(--dampad); }
.flikar ul { list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 0.25rem;
             border-bottom: 2px solid var(--text); margin: 0 0 1.5rem; }
.flikar a { display: block; padding: 0.35rem 0.8rem; border: 1px solid var(--kant);
            border-bottom: none; border-radius: 0.4rem 0.4rem 0 0;
            background: var(--yta); }
.flikar a[aria-current] { background: var(--text); color: var(--bakgrund);
                          border-color: var(--text); }
.oversikt td { text-align: center; }
.dold { position: absolute; width: 1px; height: 1px; overflow: hidden;
        clip-path: inset(50%); white-space: nowrap; }
.oversikt tr.grupp th { background: var(--yta); text-align: left; }
.oversikt th.utskott { padding-left: 1.8rem; font-weight: normal; }
footer { border-top: 1px solid var(--kant); margin-top: 3rem; padding: 1rem 0;
         overflow-wrap: anywhere; }
h1, h2 { overflow-wrap: break-word; hyphens: auto; }
"""


# Dokumentationen bor med koden, också när poolen ligger i ett eget datarepo,
# som regionens (K14).
KALLKOD = "https://github.com/moggleif/kungsbackakommun"


@dataclass(frozen=True)
class Mall:
    kommuner: list[Kommun]
    repo: str
    byggd: datetime
    kalendrar: frozenset[str] = frozenset()
    malen: dict[str, list[Mal]] = field(default_factory=dict)
    uppfoljningar: dict[str, list[Uppfoljning]] = field(default_factory=dict)
    # Stegen per spårslag och kommun, som `spar["lokalbehov"]["kungsbacka"]`.
    spar: dict[str, dict[str, list[Steg]]] = field(default_factory=dict)
    # Detaljplanernas projekt per kommun och plan (K46).
    projekt: dict[str, dict[str, Projekt]] = field(default_factory=dict)
    # Åren som sidorna över tid visar, per kommun (K60).
    aren: dict[str, range] = field(default_factory=dict)

    @property
    def en_kommun(self) -> bool:
        return len(self.kommuner) == 1


def rot(adress: str) -> str:
    return "../" * adress.count("/")


def sida(mall: Mall, adress: str, rubrik: str, innehall: str) -> str:
    namn = sajtnamn(mall.kommuner)
    titel = namn if rubrik == namn else f"{rubrik} – {namn}"
    return f"""<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titel)}</title>
{GEMENSAM}
<style>{STIL}</style>
</head>
<body>
{meny(mall.kommuner, mall.kalendrar, adress)}
<main>
<h1>{escape(rubrik)}</h1>
{innehall}
</main>
{sidfot(mall)}
</body>
</html>
"""


def menypost(adress: str, namn: str, aktuell: bool) -> str:
    markering = ' aria-current="page"' if aktuell else ""
    return f'<li><a href="{adress}"{markering}>{escape(namn)}</a></li>'


def stig(lankar: list[tuple[str, str]]) -> str:
    poster = " › ".join(
        f'<a href="{escape(adress)}">{escape(namn)}</a>' for adress, namn in lankar
    )
    return f'<nav aria-label="Här är du"><p>{poster}</p></nav>'


def lank(adress: str, text: str) -> str:
    if not adress.startswith(("https://", "http://")):
        return escape(text)
    return f'<a href="{escape(adress)}">{escape(text)}</a>'


def sidfot(mall: Mall) -> str:
    repo, kod = escape(mall.repo), escape(KALLKOD)
    tid = mall.byggd.strftime("%Y-%m-%d %H:%M UTC")
    lankar = (
        f'Källkod och data: <a href="{repo}">{repo}</a>'
        if mall.repo == KALLKOD
        else f'Data: <a href="{repo}">{repo}</a>. Källkod: <a href="{kod}">{kod}</a>'
    )
    return f"<footer><p>{lankar}. Sidan byggdes {tid}.</p></footer>"
