"""Krav: K7 och K14 i docs/02-KRAV.md. Test: tests/test_webbplats.py."""

from html import escape

from kommunhandlingar.kandidat import TYPORDNING
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.konvertering.kvalitet import KVALITETER
from kommunhandlingar.webbplats.luckavsnitt import luckavsnitt
from kommunhandlingar.webbplats.mall import Mall, sida
from kommunhandlingar.webbplats.rakning import Organrad, rakna

ARKITEKTUR = "/blob/main/docs/03-ARKITEKTUR.md"
INGET = '<td colspan="{}">inget hämtat än</td>'


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
        + dokumenttabell(rader, kommun.id)
        + "<h2>Kvalitet per organ</h2>"
        + f'<p>Nivåerna förklaras i <a href="{escape(mall.repo + ARKITEKTUR)}'
        '#konvertering-och-kvalitet">arkitekturen</a>.</p>'
        + kvalitetstabell(rader, kommun.id)
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


def dokumenttabell(rader: list[Organrad], kommun_id: str) -> str:
    kolumner = ["Sammanträden", *TYPORDNING, "Luckor"]
    return tabell(kolumner, [(rad, dokumenttal(rad)) for rad in rader], kommun_id)


def dokumenttal(rad: Organrad) -> list[int]:
    typer = [rad.typer[typ] for typ in TYPORDNING]
    return [rad.sammantraden, *typer, len(rad.luckor)]


def kvalitetstabell(rader: list[Organrad], kommun_id: str) -> str:
    kolumner = [*KVALITETER, "Sidor med obekräftade tal"]
    return tabell(
        kolumner,
        [
            (rad, [*(rad.kvaliteter[k] for k in KVALITETER), rad.obekraftade_sidor])
            for rad in rader
        ],
        kommun_id,
    )


def tabell(
    kolumner: list[str], rader: list[tuple[Organrad, list[int]]], kommun_id: str
) -> str:
    huvud = "".join(f'<th scope="col">{escape(k)}</th>' for k in ["Organ", *kolumner])
    kropp = "".join(
        f'<tr><th scope="row"><a href="{kommun_id}/{rad.id}.html">'
        f"{escape(rad.namn)}</a></th>{celler(rad, tal)}</tr>"
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
