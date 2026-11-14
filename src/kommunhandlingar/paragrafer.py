"""Krav: K48 i docs/02-KRAV.md, ADR-0071. Test: tests/test_paragrafer.py.

Ett protokolls text delas vid raderna som inleder en paragraf, `§ 121`,
`BN § 1` eller `§ 121 Dnr GA-2026-00004`. Innehållsförteckningen och
närvarolistan upprepar numren före paragraferna, så det sista avsnittet
med ett nummer gäller, och en fortsättning (`§ 270, forts`) direkt efter
hör till samma paragraf.
"""

import re
from dataclasses import dataclass

from kommunhandlingar.diarienummer import i_huvudet

RUBRIKRAD = re.compile(r"^\s*(?:[A-ZÅÄÖ]{2,4}\s*)?§\s*(\d+)(.*)$")
FORTS = re.compile(r"^[\s,./]*forts", re.IGNORECASE)
SIDA = re.compile(r"^<!-- sida (\d+) -->$")
DATUM = re.compile(r"\d{4}-\d{2}-\d{2}")
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
SIDFOT = ("Justerare", "Det här dokumentet är digitalt signerat")


@dataclass(frozen=True)
class Paragraf:
    nummer: int
    rubrik: str | None
    diarienummer: list[str]
    beslut: str | None
    sida: int | None


def paragrafer(text: str) -> list[Paragraf]:
    rader = text.splitlines()
    avsnitt = {}
    for nummer, start, slut in avsnitten(rader):
        tidigare = avsnitt.get(nummer)
        if tidigare and tidigare[1] == start and fortsattning(rader[start]):
            start = tidigare[0]
        avsnitt[nummer] = (start, slut)
    ordning = sorted(avsnitt.items(), key=lambda par: par[1][0])
    return [paragraf(n, rader, s, e) for n, (s, e) in ordning]


def avsnitten(rader: list[str]) -> list[tuple[int, int, int]]:
    starter = [(i, int(m[1])) for i, m in rubriker(rader)]
    slut = [i for i, _ in starter[1:]] + [len(rader)]
    return [(n, i, e) for (i, n), e in zip(starter, slut, strict=False)]


def rubriker(rader: list[str]):
    for i, rad in enumerate(rader):
        if (m := RUBRIKRAD.match(rad)) and inleder(m[2], rader[i - 1] if i else ""):
            yield i, m


def inleder(rest: str, forra: str) -> bool:
    """Ett ensamt `§ 4` efter en rad text hör till närvarolistan eller texten."""
    rest = rest.strip()
    if not rest:
        forra = forra.strip()
        return not forra or bool(SIDA.match(forra) or DATUM.fullmatch(forra))
    return bool(FORTS.match(rest)) or bool(i_huvudet(rest, ensam=True))


def fortsattning(rad: str) -> bool:
    return bool(FORTS.match(RUBRIKRAD.match(rad)[2]))


def paragraf(nummer: int, rader: list[str], start: int, slut: int) -> Paragraf:
    rest = rader[start + 1 : slut]
    numren = i_huvudet(RUBRIKRAD.match(rader[start])[2], ensam=True)
    numren += i_huvudet("\n".join(innan_beslut(rest)))
    return Paragraf(
        nummer=nummer,
        rubrik=rubrik(rest),
        diarienummer=list(dict.fromkeys(numren)),
        beslut=beslut(rest),
        sida=sida(rader, start),
    )


def avsnitt(rad: str) -> bool:
    return " ".join(rad.split()).rstrip(":") in AVSNITT


def sidslut(rad: str) -> bool:
    return bool(SIDA.match(rad)) or rad.startswith(SIDFOT)


def innan_beslut(rader: list[str]) -> list[str]:
    huvud = []
    for rad in rader:
        if avsnitt(rad) or sidslut(rad):
            break
        huvud.append(rad)
    return huvud[:8]


def rubrik(rader: list[str]) -> str | None:
    for rad in rader:
        rad = rad.strip()
        if rad and not SIDA.match(rad) and not i_huvudet(rad):
            return None if avsnitt(rad) or sidslut(rad) else rad
    return None


def beslut(rader: list[str]) -> str | None:
    """Till nästa rubrik; når beslutet sidans slut kan det fortsätta, och
    då blir det `null` hellre än kapat."""
    stripade = [r.strip() for r in rader]
    if "Beslut" not in stripade:
        return None
    text = []
    for rad in stripade[stripade.index("Beslut") + 1 :]:
        if sidslut(rad):
            return None
        if avsnitt(rad):
            break
        text.append(rad)
    return "\n".join(text).strip() or None


def sida(rader: list[str], start: int) -> int | None:
    for rad in reversed(rader[:start]):
        if m := SIDA.match(rad):
            return int(m[1])
    return None
