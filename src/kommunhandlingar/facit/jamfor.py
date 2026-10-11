"""Krav: K20 i docs/02-KRAV.md, ADR-0025. Test: tests/test_facit.py.

Jämför en konvertering med sitt facit och räknar måtten i
docs/03-ARKITEKTUR.md#facit-för-konverteringen. En rad i en CSV stämmer
när varje tal står i samma kolumn som i facit och etiketten börjar eller
slutar som facits. Talen i texten och tabellerna jämförs som siffergrupper
på de sidor vars tal är bekräftade.
"""

import re
from collections import Counter
from dataclasses import dataclass, field

from kommunhandlingar.facit.lasa import Facit, Tabell
from kommunhandlingar.konvertering.dokument import Resultat
from kommunhandlingar.konvertering.flersidiga import Sammanslagen, tabeller
from kommunhandlingar.konvertering.tabeller import TALRAD

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
SIFFROR = re.compile(r"\d+")
TECKEN_OCH_TAL = re.compile(r"^([-−–+]) (?=\d)")


@dataclass
class Utfall:
    matt: Counter = field(default_factory=Counter)
    noter: list[str] = field(default_factory=list)
    traffar: set[tuple[str, int]] = field(default_factory=set)
    rubriker: dict[str, list[list[str]]] = field(default_factory=dict)

    def rakna(self, matt: str, noter: list[str]):
        self.matt[matt] += len(noter)
        self.noter += [f"{matt}: {n}" for n in noter]


def jamfor(facit: Facit, resultat: Resultat) -> Utfall:
    utfall = Utfall()
    producerade = tabeller(resultat.sidor)
    for t in producerade:
        granska(t, facit.tabeller, utfall)
    markerade = markerade_sidor(resultat)
    for f in facit.tabeller:
        matt = status(f, utfall.traffar, utfall.rubriker.get(f.namn), markerade)
        if matt == "ratt":
            utfall.matt["ratt"] += 1
        else:
            utfall.rakna(matt, [f"tabell {f.namn}"])
    rakna_tal(facit, resultat, producerade, utfall)
    omarkta = [nr for nr in facit.skannade if nr not in resultat.tal_obekraftade]
    utfall.rakna("omarkta", [f"skannad sida {nr}" for nr in omarkta])
    return utfall


def granska(t: Sammanslagen, facits: list[Tabell], utfall: Utfall):
    """Varje rad med tal efter den första som stämmer med en datarad i facit
    ska stämma med en rad i facit; raderna före den är tabellens rubrik."""
    kandidater = [f for f in facits if overlappar(t, f)]
    if not kandidater:
        utfall.rakna("pahittade", [f"tabell {t.namn}"] * any(map(talrad, t.rader)))
        return
    funna = [traffa(rad, kandidater) if talrad(rad) else None for rad in t.rader]
    forsta = next((i for i, tr in enumerate(funna) if tr and tr[2]), len(funna))
    if forsta < len(funna):
        utfall.rubriker.setdefault(funna[forsta][0], t.rader[:forsta])
    else:
        forsta = 0
    utfall.traffar |= {tr[:2] for tr in funna[forsta:] if tr}
    par = list(zip(t.rader, funna, strict=True))[forsta:]
    fel = [rad for rad, tr in par if talrad(rad) and not tr]
    utfall.rakna("fel_rader", [f"{t.namn} {rad}" for rad in fel])


def overlappar(t: Sammanslagen, f: Tabell) -> bool:
    return t.sida <= f.sista_sida and f.sida <= t.sista_sida


def traffa(rad: list[str], kandidater: list[Tabell]) -> tuple[str, int, bool] | None:
    for f in kandidater:
        for i, facitrad in enumerate(f.rader):
            if lika(rad, facitrad):
                return f.namn, i, i >= f.rubrikrader
    return None


def lika(rad: list[str], facitrad: list[str]) -> bool:
    if len(rad) != len(facitrad):
        return False
    for a, b in zip(map(cell, rad), map(cell, facitrad), strict=True):
        if (ar_tal(a) or ar_tal(b)) and a != b:
            return False
    egen, facits = bokstaver(rad), bokstaver(facitrad)
    if facits and not egen:
        return False
    return facits.startswith(egen) or facits.endswith(egen)


def cell(text: str) -> str:
    return TECKEN_OCH_TAL.sub(r"\1", " ".join(text.split()))


def ar_tal(text: str) -> bool:
    return bool(text) and TALRAD.fullmatch(text) is not None


def talrad(rad: list[str]) -> bool:
    return any(ar_tal(cell(c)) for c in rad)


def bokstaver(rad: list[str]) -> str:
    text = "".join(c for c in map(cell, rad) if not ar_tal(c))
    return "".join(t for t in text.lower() if t.isalpha())


def markerade_sidor(resultat: Resultat) -> set[int]:
    sidor = enumerate(resultat.kvalitet_per_sida, 1)
    return {nr for nr, k in sidor if k != "ok"} | set(resultat.tal_obekraftade)


def status(f: Tabell, traffar: set, rubrik, markerade: set[int]) -> str:
    data = {i for i, r in enumerate(f.rader) if i >= f.rubrikrader and talrad(r)}
    funna = {i for namn, i in traffar if namn == f.namn} & data
    if not funna:
        spannet = set(range(f.sida, f.sista_sida + 1))
        return "osakra" if spannet & markerade else "saknade"
    if funna == data and rubrik_stammer(f, rubrik):
        return "ratt"
    return "ofullstandiga"


def rubrik_stammer(f: Tabell, rubrik: list[list[str]] | None) -> bool:
    """Rubrikens tal, kolumn för kolumn, oavsett hur raderna delats."""
    facits = kolumnernas_siffror(f.rader[: f.rubrikrader])
    if not any(facits):
        return True
    return rubrik is not None and kolumnernas_siffror(rubrik) == facits


def kolumnernas_siffror(rader: list[list[str]]) -> list[list[str]]:
    bredd = max(map(len, rader), default=0)
    return [
        [s for rad in rader if j < len(rad) for s in SIFFROR.findall(rad[j])]
        for j in range(bredd)
    ]


def rakna_tal(facit: Facit, resultat: Resultat, producerade, utfall: Utfall):
    utanfor = set(resultat.tal_obekraftade) | set(facit.skannade)
    ut = Counter()
    for nr, sida in enumerate(resultat.sidor, 1):
        if nr not in utanfor:
            ut.update(SIFFROR.findall(sida.text))
    for t in producerade:
        if t.sida not in utanfor:
            ut.update(s for rad in t.rader for c in rad for s in SIFFROR.findall(c))
    ratt = Counter(
        s
        for nr, tal in facit.tal.items()
        if nr not in utanfor
        for x in tal
        for s in SIFFROR.findall(x)
    )
    saknas, tillkommer = ratt - ut, ut - ratt
    utfall.matt["tal_avviker"] += saknas.total() + tillkommer.total()
    if saknas or tillkommer:
        utfall.noter.append(
            f"tal_avviker: saknas {dict(saknas)}, ny {dict(tillkommer)}"
        )
