"""Krav: K62 i docs/02-KRAV.md, ADR-0089. Test: tests/test_sokindex.py.

Webbplatsens sökindex `sok.json` i roten, i det format som sökningen i
projektets gemensamma sajtrad läser (Giffås beslut 0018): en grupp per
kommun med protokollens paragrafer, nyast först. Varje post har det som
visas – rubriken, paragrafens sida och organ, datum, paragraf och
diarienummer – och det som söks i, i små bokstäver: rubriken och
diarienumren som träff, organet som text, så att ett ord som också är ett
organs namn ger paragraferna med ordet i rubriken först.
"""

import json
from datetime import date
from pathlib import Path

from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.kalendervyer import MANADER
from kommunhandlingar.webbplats.kortkoppling import organnamn


def grupp(kommun: Kommun, paragraferna: list[dict]) -> dict:
    namn = organnamn(kommun)
    ordnade = sorted(paragraferna, key=nyast_forst, reverse=True)
    return {
        "rubrik": f"Protokollen i {kommun.namn}",
        "poster": [post(p, namn.get(p["organ"], p["organ"])) for p in ordnade],
    }


def nyast_forst(paragraf: dict) -> tuple[str, int]:
    return paragraf["datum"], -paragraf["paragraf"]


def post(paragraf: dict, organ: str) -> dict:
    rubrik = " ".join(paragraf["rubrik"].split()) or f"§ {paragraf['paragraf']}"
    numren = paragraf["diarienummer"]
    return {
        "rubrik": rubrik,
        "adress": paragraf["sida"],
        "om": [organ, klartext(paragraf["datum"]), f"§ {paragraf['paragraf']}"]
        + [f"Dnr {n}" for n in numren],
        "traff": " ".join([rubrik, *numren]).lower(),
        "text": organ.lower(),
    }


def klartext(datum: str) -> str:
    dag = date.fromisoformat(datum)
    return f"{dag.day} {MANADER[dag.month - 1]} {dag.year}"


def skriv(ut: Path, grupper: list[dict]) -> None:
    text = json.dumps({"grupper": grupper}, ensure_ascii=False, separators=(",", ":"))
    (ut / "sok.json").write_text(text, encoding="utf-8")
