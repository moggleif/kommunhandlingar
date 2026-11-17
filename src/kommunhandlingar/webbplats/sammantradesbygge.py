"""Krav: K54 i docs/02-KRAV.md, ADR-0078. Test: tests/test_sammantradessida.py.

Bygget av sammanträdenas sidor: kommunens paragrafer och kort per
diarienummer, och för varje sammanträde med en sida kallelsen och
handlingarna ur poolen.
"""

import json
from pathlib import Path

from kommunhandlingar import frontmatter
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats import sammantrade
from kommunhandlingar.webbplats.kortkoppling import kortlankar, sidindex
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.punktsidor import sidor
from kommunhandlingar.webbplats.sammantrade import Mote, Underlag, per_nummer
from kommunhandlingar.webbplats.sammantradessida import sammantradessida
from kommunhandlingar.webbplats.slagen import SLAGEN


# `lasta` är kommunens dokument och paragrafernas rader, som bygget läst.
def underlag(
    mall: Mall, katalog: Path, kommun: Kommun, lasta: tuple[list[dict], list[str]]
) -> Underlag:
    dokument, rader = lasta
    paragraferna = [json.loads(rad) for rad in rader]
    sparen = [(s, mall.spar[s.id].get(kommun.id, [])) for s in SLAGEN]
    kort = kortlankar(kommun, sparen, sidindex(paragraferna))
    return Underlag(
        kommun, katalog, dokument, paragraferna, per_nummer(paragraferna), kort
    )


def bygg(ut: Path, mall: Mall, underlag: Underlag) -> None:
    for dokumenten in sammantrade.moten(underlag):
        mote = Mote(
            underlag.kommun,
            dokumenten,
            forsta_text(underlag.katalog, dokumenten, "kallelse"),
            sidor(forsta_text(underlag.katalog, dokumenten, "handlingar")),
            sammantrade.egna(underlag, dokumenten),
        )
        html = sammantradessida(mall, mote, sammantrade.arenden(mote, underlag))
        sidfil = ut / underlag.kommun.id / sammantrade.adress(dokumenten)
        sidfil.write_text(html, encoding="utf-8")


def forsta_text(katalog: Path, dokumenten: list[dict], typ: str) -> str:
    funna = [d for d in sammantrade.ordnade(dokumenten) if d["typ"] == typ]
    if not funna:
        return ""
    fil = (katalog / funna[0]["adress"]).with_suffix(".md")
    return frontmatter.brodtext(fil.read_text(encoding="utf-8"))
