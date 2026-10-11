"""Krav: K20 i docs/02-KRAV.md, ADR-0025. Test: tests/test_facit.py.

Jämför en konvertering med sitt facit och räknar måtten i
docs/03-ARKITEKTUR.md#facit-för-konverteringen.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field

from kommunhandlingar.facit import tal
from kommunhandlingar.facit.lasa import Facit, Tabell
from kommunhandlingar.facit.rader import (
    kolumnernas_siffror,
    lika,
    siffror,
    talrad,
)
from kommunhandlingar.konvertering.dokument import Resultat
from kommunhandlingar.konvertering.flersidiga import Sammanslagen, tabeller

MATT = (
    "ratt",
    "ofullstandiga",
    "osakra",
    "saknade",
    "fel_rader",
    "pahittade",
    "tal_avviker",
    "omarkta",
)

type Traff = tuple[str, int, bool]


@dataclass
class Utfall:
    matt: Counter = field(default_factory=Counter)
    noter: list[str] = field(default_factory=list)
    # Facittabellens namn, raden i den och namnet på CSV:en där raden stod.
    traffar: set[tuple[str, int, str]] = field(default_factory=set)
    rubriker: dict[str, list[list[str]]] = field(default_factory=dict)

    def rakna(self, matt: str, noter: list[str]):
        self.matt[matt] += len(noter)
        if matt != "ratt":
            self.noter += [f"{matt}: {n}" for n in noter]


def jamfor(facit: Facit, resultat: Resultat) -> Utfall:
    utfall = Utfall()
    for t in tabeller(resultat.sidor):
        granska(t, facit.tabeller, utfall)
    markerade = markerade_sidor(resultat)
    for f in facit.tabeller:
        utfall.rakna(status(f, utfall, markerade), [f"tabell {f.namn}"])
    saknas, tillkommer = tal.avvikelser(facit, resultat)
    saknade = [f"saknas {t}" for t in saknas.elements()]
    utfall.rakna("tal_avviker", saknade + [f"ny {t}" for t in tillkommer.elements()])
    omarkta = [nr for nr in facit.skannade if nr not in resultat.tal_obekraftade]
    utfall.rakna("omarkta", [f"skannad sida {nr}" for nr in omarkta])
    return utfall


def granska(t: Sammanslagen, facits: list[Tabell], utfall: Utfall):
    kandidater = [
        f for f in facits if t.sida <= f.sista_sida and f.sida <= t.sista_sida
    ]
    if not kandidater:
        if any(map(talrad, t.rader)):
            utfall.rakna("pahittade", [f"tabell {t.namn}"])
        return
    forsta = forsta_dataraden(t.rader, kandidater)
    if forsta is not None:
        namn = traffa(t.rader[forsta], kandidater, set())[0]
        utfall.rubriker.setdefault(namn, t.rader[:forsta])
    rubrik = t.rader[: forsta or 0]
    anvanda = {(f, i) for f, i, _ in utfall.traffar}
    fel, nya = kroppen(t.rader[len(rubrik) :], kandidater, anvanda)
    utfall.traffar |= {(f, i, t.namn) for f, i in nya}
    fel = rubrikens_fel(rubrik, kandidater) + fel
    utfall.rakna("fel_rader", [f"{t.namn} {rad}" for rad in fel])


def forsta_dataraden(rader: list[list[str]], kandidater: list[Tabell]) -> int | None:
    for i, rad in enumerate(rader):
        traff = traffa(rad, kandidater, set()) if talrad(rad) else None
        if traff and traff[2]:
            return i
    return None


def traffa(rad: list[str], kandidater: list[Tabell], anvanda: set) -> Traff | None:
    """Den första facitraden som stämmer och inte redan använts."""
    for f in kandidater:
        for i, facitrad in enumerate(f.rader):
            if (f.namn, i) not in anvanda and lika(rad, facitrad):
                return f.namn, i, i >= f.rubrikrader
    return None


def kroppen(rader: list[list[str]], kandidater: list[Tabell], anvanda: set):
    """Raderna med tal efter rubriken: de som inte stämmer med en oanvänd
    rad i facit, och de datarader i facit som hittades."""
    fel, nya = [], set()
    for rad in filter(talrad, rader):
        traff = traffa(rad, kandidater, anvanda | nya)
        if traff is None:
            fel.append(rad)
        elif traff[2]:
            nya.add(traff[:2])
    return fel, nya


def rubrikens_fel(rubrik: list[list[str]], kandidater: list[Tabell]) -> list:
    """En rad med tal före den första dataraden får bara ha rubrikens tal."""
    tillatna = set(siffror([r for f in kandidater for r in f.rader[: f.rubrikrader]]))
    return [r for r in rubrik if talrad(r) and not set(siffror([r])) <= tillatna]


def markerade_sidor(resultat: Resultat) -> set[int]:
    sidor = enumerate(resultat.kvalitet_per_sida, 1)
    return {nr for nr, k in sidor if k != "ok"} | set(resultat.tal_obekraftade)


def status(f: Tabell, utfall: Utfall, markerade: set[int]) -> str:
    data = {i for i, r in enumerate(f.rader) if i >= f.rubrikrader and talrad(r)}
    per_csv = defaultdict(set)
    for namn, i, csv_namn in utfall.traffar:
        if namn == f.namn:
            per_csv[csv_namn].add(i)
    if not per_csv:
        spannet = set(range(f.sida, f.sista_sida + 1))
        return "osakra" if spannet & markerade else "saknade"
    hel = any(data <= rader for rader in per_csv.values())
    if hel and rubrik_stammer(f, utfall.rubriker.get(f.namn)):
        return "ratt"
    return "ofullstandiga"


def rubrik_stammer(f: Tabell, rubrik: list[list[str]] | None) -> bool:
    facits = kolumnernas_siffror(f.rader[: f.rubrikrader])
    if not any(facits):
        return True
    return rubrik is not None and kolumnernas_siffror(rubrik) == facits
