"""Krav: K14, K18, K26, K27, K28 och K36 i docs/02-KRAV.md.
Test: tests/test_webbplats.py."""

from dataclasses import dataclass, field
from datetime import datetime
from html import escape

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats import avvikelser
from kommunhandlingar.webbplats.lokalbehov import Steg
from kommunhandlingar.webbplats.mal import Mal
from kommunhandlingar.webbplats.uppfoljningar import Uppfoljning

STIL = """
body { font-family: system-ui, sans-serif; max-width: 72rem; margin: 0 auto;
       padding: 0 1rem; line-height: 1.5; color: #1a1a1a; background: #fff; }
nav ul { list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 1.5rem; }
nav a[aria-current] { font-weight: bold; text-decoration: none; }
.tabell, .sida { overflow-x: auto; }
table { border-collapse: collapse; margin-bottom: 2rem; }
th, td { border: 1px solid #999; padding: 0.25rem 0.6rem; vertical-align: top; }
th[scope="row"] { text-align: left; }
td.tal { text-align: right; font-variant-numeric: tabular-nums; }
dl.harkomst { display: grid; grid-template-columns: max-content 1fr; gap: 0 1rem; }
dl.harkomst dd { margin: 0; overflow-wrap: anywhere; }
.sida { border-top: 1px solid #999; margin-top: 2rem; }
.sida p { white-space: pre-wrap; }
.markering { font-weight: bold; }
pre { background: #f2f2f2; padding: 0.5rem; overflow-x: auto; }
.status { display: inline-block; padding: 0.1em; line-height: 0;
          border: 1px solid transparent; border-radius: 0.3em; cursor: help; }
.status.prognos { border: 1px dashed currentColor; }
.status.uppnatt { color: #1a6b2a; } .status.delvis { color: #8a5a00; }
.status.ej { color: #b00020; }
.status.ingen, .status.beslutat { color: #555; }
footer { border-top: 1px solid #999; margin-top: 3rem; padding: 1rem 0; }
"""


@dataclass(frozen=True)
class Mall:
    kommuner: list[Kommun]
    repo: str
    byggd: datetime
    kalendrar: frozenset[str] = frozenset()
    malen: dict[str, list[Mal]] = field(default_factory=dict)
    uppfoljningar: dict[str, list[Uppfoljning]] = field(default_factory=dict)
    lokalbehov: dict[str, list[Steg]] = field(default_factory=dict)


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
</head>
<body>
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
    poster = (
        [("index.html", "Start")]
        + [(f"{k.id}.html", k.namn) for k in mall.kommuner]
        + [(avvikelser.ADRESS, "Avvikelser")]
    )
    lankar = "".join(
        menypost(rot(aktuell) + adress, namn, adress == aktuell)
        for adress, namn in poster
    )
    return f'<nav aria-label="Webbplatsen"><ul>{lankar}</ul></nav>'


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
