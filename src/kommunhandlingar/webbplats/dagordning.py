"""Krav: K54 i docs/02-KRAV.md, ADR-0078. Test: tests/test_dagordning.py.

Kallelsens dagordning: tabellraderna som börjar med punktens nummer, med
ärendet, beteckningen och förslaget. En rad som konverteringen skrev som
löptext ger numret och diarienumret, men varken rubrik eller förslag.
"""

import re
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import takewhile

TABELLRAD = re.compile(r"^\| (\d+)\. \| (.*?) \| (.*?) \| (.*?) \|$", re.MULTILINE)
LOPTEXT = re.compile(r"^(\d+)\\\. .+? (\d{4}-\d+) ", re.MULTILINE)
# Föredragningens tid och föredragandena står efter rubriken i samma cell.
TIDPUNKT = re.compile(r"\d{1,2}\.\d{2}\s*[–-]")
FORSLAG = "Förslag till beslut"


@dataclass(frozen=True)
class Punkt:
    nummer: int
    rubrik: str
    diarienummer: str
    # Förslagets stycken: tomt när kallelsen inte har något, `None` när det
    # inte gick att läsa.
    forslag: tuple[str, ...] | None


def dagordning(kallelse: str) -> list[Punkt]:
    punkter = {}
    for nummer, arende, beteckning, forslag in TABELLRAD.findall(kallelse):
        punkter[int(nummer)] = Punkt(
            int(nummer), rubrik(arende), beteckning.strip(), stycken(forslag)
        )
    for nummer, beteckning in LOPTEXT.findall(kallelse):
        punkter.setdefault(int(nummer), Punkt(int(nummer), "", beteckning, None))
    return [punkter[n] for n in sorted(punkter)]


def rubrik(cell: str) -> str:
    return fogat(takewhile(lambda r: not TIDPUNKT.match(r), cell.split("<br>")))


# Raderna blir en text och Markdowns escapning tas bort. En rad som slutar
# med bindestreck fogas till nästa utan mellanslag; bindestrecket står
# kvar, eftersom det lika gärna kan höra till ett sammansatt ord.
def fogat(rader: Iterable[str]) -> str:
    text = ""
    for rad in (r.strip() for r in rader):
        text += rad if text.endswith("-") or not text else " " + rad
    return re.sub(r"\\(.)", r"\1", text)


# En ny rubrik "Förslag till beslut …" och en rad som slutar med punkt
# eller kolon avslutar ett stycke.
def stycken(cell: str) -> tuple[str, ...]:
    resultat, aktuellt = [], []
    for rad in (r.strip() for r in cell.split("<br>") if r.strip()):
        if rad.startswith(FORSLAG) and aktuellt:
            resultat.append(fogat(aktuellt))
            aktuellt = []
        aktuellt.append(rad)
        if rad.startswith(FORSLAG) or rad.endswith((".", ":")):
            resultat.append(fogat(aktuellt))
            aktuellt = []
    return tuple(resultat + ([fogat(aktuellt)] if aktuellt else []))
