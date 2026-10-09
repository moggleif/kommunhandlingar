"""Krav: K7 och K14 i docs/02-KRAV.md. Test: tests/test_webbplats.py."""

from dataclasses import dataclass
from datetime import datetime
from html import escape

from kommunhandlingar.kandidat import TYPORDNING
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.konvertering.kvalitet import KVALITETER
from kommunhandlingar.webbplats.luckavsnitt import luckavsnitt
from kommunhandlingar.webbplats.rakning import Organrad, rakna

STIL = """
body { font-family: system-ui, sans-serif; max-width: 72rem; margin: 0 auto;
       padding: 0 1rem; line-height: 1.5; color: #1a1a1a; background: #fff; }
nav ul { list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 1.5rem; }
nav a[aria-current] { font-weight: bold; text-decoration: none; }
.tabell { overflow-x: auto; }
table { border-collapse: collapse; margin-bottom: 2rem; }
th, td { border: 1px solid #999; padding: 0.25rem 0.6rem; }
th[scope="row"] { text-align: left; }
td.tal { text-align: right; font-variant-numeric: tabular-nums; }
footer { border-top: 1px solid #999; margin-top: 3rem; padding: 1rem 0; }
"""
ARKITEKTUR = "/blob/main/docs/03-ARKITEKTUR.md"
INGET = '<td colspan="{}">inget hämtat än</td>'


@dataclass(frozen=True)
class Mall:
    kommuner: list[Kommun]
    repo: str
    byggd: datetime


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
    poster = [("index.html", "Start")] + [
        (f"{k.id}.html", k.namn) for k in mall.kommuner
    ]
    lankar = "".join(
        menypost(adress, namn, adress == aktuell) for adress, namn in poster
    )
    return f'<nav aria-label="Webbplatsen"><ul>{lankar}</ul></nav>'


def menypost(adress: str, namn: str, aktuell: bool) -> str:
    markering = ' aria-current="page"' if aktuell else ""
    return f'<li><a href="{adress}"{markering}>{escape(namn)}</a></li>'


def sidfot(mall: Mall) -> str:
    repo = escape(mall.repo)
    tid = mall.byggd.strftime("%Y-%m-%d %H:%M UTC")
    return (
        f'<footer><p>Källkod och data: <a href="{repo}">{repo}</a>. '
        f"Sidan byggdes {tid}.</p></footer>"
    )


def startsida(mall: Mall) -> str:
    kommuner = "".join(
        f'<li><a href="{k.id}.html">{escape(k.namn)}</a></li>' for k in mall.kommuner
    )
    innehall = (
        f'<p>Vad poolen är och hur den byggs står i <a href="{escape(mall.repo)}'
        '#readme">README</a>.</p>'
        f"<h2>Vad poolen innehåller</h2><ul>{kommuner}</ul>"
    )
    return sida(mall, "index.html", "kommunhandlingar", innehall)


def statussida(mall: Mall, kommun: Kommun, dokument: list[dict[str, str]]) -> str:
    rader = rakna(kommun, dokument, mall.byggd.date())
    innehall = (
        sammanfattning(dokument)
        + "<h2>Dokument per organ</h2>"
        + dokumenttabell(rader)
        + "<h2>Kvalitet per organ</h2>"
        + f'<p>Nivåerna förklaras i <a href="{escape(mall.repo + ARKITEKTUR)}'
        '#konvertering-och-kvalitet">arkitekturen</a>.</p>'
        + kvalitetstabell(rader)
        + luckavsnitt(kommun, rader, mall.repo)
    )
    return sida(mall, f"{kommun.id}.html", kommun.namn, innehall)


def sammanfattning(dokument: list[dict[str, str]]) -> str:
    datum = sorted(d["datum"] for d in dokument) or ["–"]
    return (
        f"<p>Dokument: {len(dokument)}. "
        f"Äldsta sammanträde: {escape(datum[0])}. "
        f"Senaste sammanträde: {escape(datum[-1])}.</p>"
    )


def dokumenttabell(rader: list[Organrad]) -> str:
    kolumner = ["Sammanträden", *TYPORDNING, "Luckor"]
    return tabell(
        kolumner,
        [
            (
                rad,
                [
                    rad.sammantraden,
                    *(rad.typer[t] for t in TYPORDNING),
                    len(rad.luckor),
                ],
            )
            for rad in rader
        ],
    )


def kvalitetstabell(rader: list[Organrad]) -> str:
    kolumner = [*KVALITETER, "Sidor med obekräftade tal"]
    return tabell(
        kolumner,
        [
            (rad, [*(rad.kvaliteter[k] for k in KVALITETER), rad.obekraftade_sidor])
            for rad in rader
        ],
    )


def tabell(kolumner: list[str], rader: list[tuple[Organrad, list[int]]]) -> str:
    huvud = "".join(f'<th scope="col">{escape(k)}</th>' for k in ["Organ", *kolumner])
    kropp = "".join(
        f'<tr><th scope="row">{escape(rad.namn)}</th>{celler(rad, tal)}</tr>'
        for rad, tal in rader
    )
    return (
        f'<div class="tabell"><table><thead><tr>{huvud}</tr></thead>'
        f"<tbody>{kropp}</tbody></table></div>"
    )


def celler(rad: Organrad, tal: list[int]) -> str:
    if not rad.dokument:
        return INGET.format(len(tal))
    return "".join(f'<td class="tal">{t}</td>' for t in tal)
