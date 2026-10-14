"""Krav: K33 i docs/02-KRAV.md, ADR-0054. Test: tests/test_avvikelser.py.

Läser avvikelserna i källan: de öppna issuen med etiketten `avvikelse`,
som webbplatsens arbetsflöde hämtar till en fil med ett issue per rad.
Fälten och statusraden följer mallen `.github/ISSUE_TEMPLATE/avvikelse.md`
och statusflödet i docs/01-BIDRA.md (ADR-0041).
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path

OKANT = "Utan läsbar status"
LAGEN = {
    "undersökt – fel hos kommunen": "Ska meddelas kommunen",
    "e-post skickad": "Väntar på kommunen",
    "att undersöka": "Att undersöka",
}
ORDNING = (*LAGEN.values(), OKANT)
STEG = re.compile(r"(.+?)\s+\d{4}-\d{2}-\d{2}")
KOMMENTAR = re.compile(r"<!--.*?-->", re.DOTALL)


@dataclass(frozen=True)
class Avvikelse:
    nummer: int
    rubrik: str
    adress: str
    kommun: str
    mote: str
    lage: str
    beskrivning: str


def las(fil: Path) -> list[Avvikelse]:
    rader = fil.read_text(encoding="utf-8").splitlines()
    return [tolka(json.loads(rad)) for rad in rader if rad.strip()]


def tolka(issue: dict) -> Avvikelse:
    text = KOMMENTAR.sub("", (issue["body"] or "").replace("\r\n", "\n"))
    return Avvikelse(
        nummer=issue["number"],
        rubrik=issue["title"].removeprefix("Avvikelse: "),
        adress=issue["html_url"],
        kommun=falt(text, "Kommun"),
        mote=falt(text, "Organ och möte"),
        lage=lage(falt(text, "Status")),
        beskrivning=avsnitt(text, "Vad som skiljer sig") + avsnitt(text, "Belägg"),
    )


def falt(text: str, namn: str) -> str:
    traff = re.search(rf"^\*\*{namn}:\*\*[ \t]*(.*)$", text, re.MULTILINE)
    return traff[1].strip() if traff else ""


def lage(status: str) -> str:
    """Det senaste steget på statusraden, där varje steg har sitt datum."""
    traff = STEG.fullmatch(status.split(",")[-1].strip())
    return LAGEN.get(traff[1], OKANT) if traff else OKANT


def avsnitt(text: str, rubrik: str) -> str:
    """Avsnittet med sin rubrik, två nivåer ned så att den hamnar under
    avvikelsens egen rubrik på sidan."""
    traff = re.search(
        rf"^## {rubrik}[ \t]*\n.*?(?=^## |\Z)", text, re.MULTILINE | re.DOTALL
    )
    return "##" + traff[0] + "\n" if traff else ""
