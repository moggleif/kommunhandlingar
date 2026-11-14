"""Krav: K48 i docs/02-KRAV.md, ADR-0071. Test: tests/test_paragrafer.py.

En paragrafs rubrik, raderna med diarienummer och beslutet, ur raderna
efter rubrikraden. Avsnitten är protokollens egna rubriker inne i en
paragraf; sidfoten börjar med `Justerare`.
"""

import re
from itertools import takewhile

SIDA = re.compile(r"^<!-- sida (\d+) -->$")
DNR_FORST = re.compile(r"^\s*(?:Dnr|Diarienr|Diarienummer)\b")
AVSNITT = {
    "Beslut",
    "Beslutsgång",
    "Beslutsmotivering",
    "Beslutsunderlag",
    "Bakgrund",
    "Beskrivning av ärendet",
    "Bedömning",
    "Expediering",
    "Förslag till beslut",
    "Förslag till beslut på sammanträdet",
    "Jäv",
    "Motivering",
    "Motivering till beslut",
    "Protokollsanteckning",
    "Reservation",
    "Sammanfattning",
    "Sammanfattning av ärendet",
    "Tjänsteutlåtande",
    "Upplysning",
    "Upplysningar",
    "Villkor",
    "Yrkande",
    "Yrkanden",
    "Överklagande",
}
SIDFOT = "Justerare"


def avsnitt(rad: str) -> bool:
    return " ".join(rad.split()).rstrip(":") in AVSNITT


def sidslut(rad: str) -> bool:
    return bool(SIDA.match(rad)) or rad.startswith(SIDFOT)


def dnr_rader(rader: list[str]) -> list[str]:
    """Raderna som börjar med `Dnr` före beslutet; ett nummer inne i
    rubriken är en annan myndighets."""
    huvud = []
    for rad in rader:
        if avsnitt(rad) or sidslut(rad):
            break
        huvud.append(rad)
    return [rad for rad in huvud if DNR_FORST.match(rad)]


def rubrik(rader: list[str]) -> str | None:
    for rad in rader:
        rad = rad.strip()
        if rad and not SIDA.match(rad) and not DNR_FORST.match(rad):
            return None if avsnitt(rad) or sidslut(rad) else rad
    return None


def beslut(rader: list[str]) -> str | None:
    """Från raden Beslut på paragrafens första sida till nästa rubrik. Står
    raden först efter sidans slut kan den höra till en paragraf som tappat
    sitt `§`, och når beslutet sidans slut kan det fortsätta; då blir det
    `null` hellre än fel eller kapat."""
    stripade = [r.strip() for r in rader]
    forsta_sidan = list(takewhile(lambda r: not sidslut(r), stripade))
    rubriker = [" ".join(r.split()).rstrip(":") for r in forsta_sidan]
    if "Beslut" not in rubriker:
        return None
    text = []
    for rad in stripade[rubriker.index("Beslut") + 1 :]:
        if sidslut(rad):
            return None
        if avsnitt(rad):
            break
        text.append(rad)
    return "\n".join(text).strip() or None
