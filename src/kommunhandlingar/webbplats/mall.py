"""Krav: K14, K18, K22, K26, K27, K28, K36, K37 och K39 i docs/02-KRAV.md.
Test: tests/test_webbplats.py."""

from dataclasses import dataclass, field
from datetime import datetime
from html import escape
from pathlib import Path

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats import avvikelser
from kommunhandlingar.webbplats.mal import Mal
from kommunhandlingar.webbplats.projekt import Projekt
from kommunhandlingar.webbplats.spar import Steg
from kommunhandlingar.webbplats.uppfoljningar import Uppfoljning

TEMA = Path(__file__).with_name("tema.js")
# Varje färg har ett ljust och ett mörkt värde (ADR-0074).
STIL = """
:root { color-scheme: light dark;
  --text: light-dark(#1a1a1a, #e4e6ea); --bakgrund: light-dark(#fff, #15171b);
  --kant: light-dark(#999, #5f6672); --yta: light-dark(#f5f6f8, #22262d);
  --linje: light-dark(#d9dde5, #3a404b); --dampad: light-dark(#5b6475, #a8b0bd);
  --accent: light-dark(#1d5d73, #7cc4dc); --band: light-dark(#e3eef2, #1e3942);
  --uppnatt: light-dark(#1a6b2a, #72d083); --delvis: light-dark(#8a5a00, #e6b552);
  --ej: light-dark(#b00020, #ff8a94); }
:root[data-tema="ljust"] { color-scheme: light; }
:root[data-tema="morkt"] { color-scheme: dark; }
.tema { position: fixed; top: 0.5rem; right: 0.5rem; z-index: 1; font: inherit;
        padding: 0.2rem 0.8rem; border: 1px solid var(--kant); border-radius: 999px;
        background: var(--bakgrund); color: var(--text); cursor: pointer; }
.tema[aria-pressed="true"] { border-color: var(--accent); color: var(--accent); }
nav[aria-label="Webbplatsen"] ul { padding-right: 9rem; }
body { font-family: system-ui, sans-serif; max-width: 72rem; margin: 0 auto;
       padding: 0 1rem; line-height: 1.5; color: var(--text);
       background: var(--bakgrund); }
nav ul { list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 1.5rem; }
nav a[aria-current] { font-weight: bold; text-decoration: none; }
.tabell, .sida { overflow-x: auto; }
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
.flikar ul { gap: 0.25rem; border-bottom: 2px solid var(--text); margin: 0 0 1.5rem; }
.flikar a { display: block; padding: 0.35rem 0.8rem; border: 1px solid var(--kant);
            border-bottom: none; border-radius: 0.4rem 0.4rem 0 0;
            background: var(--yta); }
.flikar a[aria-current] { background: var(--text); color: var(--bakgrund);
                          border-color: var(--text); }
.oversikt td { text-align: center; }
.dold { position: absolute; width: 1px; height: 1px; overflow: hidden; }
.oversikt tr.grupp th { background: var(--yta); text-align: left; }
.oversikt th.utskott { padding-left: 1.8rem; font-weight: normal; }
footer { border-top: 1px solid var(--kant); margin-top: 3rem; padding: 1rem 0; }
"""


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


def rot(adress: str) -> str:
    return "../" * adress.count("/")


def sida(mall: Mall, adress: str, rubrik: str, innehall: str) -> str:
    return f"""<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(rubrik)} – kommunhandlingar</title>
<style>{STIL}</style>
<script>{TEMA.read_text(encoding="utf-8")}</script>
</head>
<body>
<button type="button" class="tema" hidden>Mörkt tema</button>
{meny(mall, adress)}
<main>
<h1>{escape(rubrik)}</h1>
{innehall}
</main>
{sidfot(mall)}
</body>
</html>
"""


def meny(mall: Mall, aktuell: str) -> str:
    poster = [("index.html", "Start")]
    for k in mall.kommuner:
        poster.append((f"{k.id}.html", k.namn))
        if k.id in mall.kalendrar:
            poster.append((f"{k.id}/kalender.html", "Kalender"))
        poster.append((statusadress(k.id), "Poolens status"))
    poster.append((avvikelser.ADRESS, "Avvikelser"))
    lankar = "".join(
        menypost(rot(aktuell) + adress, namn, adress == aktuell)
        for adress, namn in poster
    )
    return f'<nav aria-label="Webbplatsen"><ul>{lankar}</ul></nav>'


def statusadress(kommun_id: str) -> str:
    return f"{kommun_id}/status.html"


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
    repo = escape(mall.repo)
    tid = mall.byggd.strftime("%Y-%m-%d %H:%M UTC")
    return (
        f'<footer><p>Källkod och data: <a href="{repo}">{repo}</a>. '
        f"Sidan byggdes {tid}.</p></footer>"
    )
