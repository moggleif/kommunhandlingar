"""Krav: K46 i docs/02-KRAV.md, ADR-0069. Test: tests/test_projekt.py.

Läser kopplingsfilen, `projekt/<kommun>.csv`: en rad per detaljplan som
hör till ett projekt på kommunens lista med projekt (K45). Projektet är
projektsidans adress efter listans, en del eller två för en sida under
ett annat projekt, och dess dokument är projektorganets dokument vars
namn börjar med sidans sista del (ADR-0068). Ett dokument hör till det
längsta av filens projekt som namnet börjar med, så att `asa-restaurangstrak`
inte tar `asa-restaurangstrak-del-2`:s dokument när båda står i filen
(docs/03-ARKITEKTUR.md#projekten). Planens kort på detaljplanssidan
får en länk till projektsidan och en lista med dokumenten.
"""

import csv
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from kommunhandlingar import frontmatter
from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.plats import namn_av
from kommunhandlingar.webbplats.spar import Steg

KOLUMNER = ["organ", "detaljplan", "projekt", "tolkad"]
Dokument = tuple[tuple[str, str, str], ...]
# Organets dokument med namnet, som projektet känns igen på, efter datumet.
Organets = tuple[tuple[str, str, str, str], ...]


@dataclass(frozen=True)
class Projekt:
    # Projektsidans adress på kommunens webbplats.
    adress: str
    tolkad: bool
    # Projektets dokument i poolen: datum, titel och adress.
    dokument: Dokument


def las(fil: Path, kommun: Kommun, data: Path) -> dict[str, Projekt]:
    with fil.open(encoding="utf-8", newline="") as f:
        rubrik, *rader = list(csv.reader(f)) or [[]]
    if rubrik != KOLUMNER:
        raise Datafel(f"{fil}: rubrikerna är inte {','.join(KOLUMNER)}")
    listor = {o: a for k in kommun.kallor for o, a in k.projekt.items()}
    planerna = set()
    for nr, rad in enumerate(rader, 2):
        if fel := radfel(rad, listor, planerna):
            raise Datafel(f"{fil}, rad {nr}: {fel}")
        planerna.add(rad[1])
    namnen = {forled(r[2]) for r in rader}
    pool = {organ: organets(data, organ) for organ in {r[0] for r in rader}}
    return {
        plan: Projekt(
            f"{listor[organ]}/{projekt}",
            tolkad == "ja",
            dokumenten(forled(projekt), pool[organ], namnen),
        )
        for organ, plan, projekt, tolkad in rader
    }


def radfel(rad: list[str], listor: dict[str, str], planerna: set[str]) -> str:
    if len(rad) != len(KOLUMNER):
        return f"{len(rad)} fält, inte {len(KOLUMNER)}"
    organ, plan, projekt, tolkad = rad
    if organ not in listor:
        return f"organet {organ!r} har ingen lista med projekt i kommunfilen"
    if not plan or plan in planerna:
        return f"planen {plan!r} är tom eller står redan i filen"
    if not re.fullmatch(r"[a-z0-9-]+(/[a-z0-9-]+)?", projekt):
        return f"projektet {projekt!r} är inte en eller två delar av en adress"
    if tolkad not in ("", "ja"):
        return f"tolkad {tolkad!r} är varken tom eller ja"
    return ""


# Dokumentens namn börjar med projektsidans sista del, också för en sida
# under ett annat projekt (ADR-0068).
def forled(projekt: str) -> str:
    return namn_av(projekt.rpartition("/")[2])


def dokumenten(projekt: str, organets: Organets, namnen: set[str]) -> Dokument:
    langre = [n for n in namnen if n.startswith(projekt + "-")]
    return tuple(
        (datum, titel, adress)
        for datum, namn, titel, adress in organets
        if namn.startswith(projekt + "-")
        and not any(namn.startswith(n + "-") for n in langre)
    )


# Titeln är källans filnamn som det står, med å, ä, ö och versaler.
def organets(data: Path, organ: str) -> Organets:
    dokumenten = []
    for fil in sorted((data / organ).rglob("*.md")):
        falt = frontmatter.las(fil.read_text(encoding="utf-8"))
        kalla = frontmatter.adresser(falt["kalla_url"])[0]
        titel = unquote(PurePosixPath(urlsplit(kalla).path).stem)
        adress = fil.relative_to(data).with_suffix(".html").as_posix()
        dokumenten.append((falt["datum"], falt["namn"], titel, adress))
    return tuple(sorted(dokumenten))


def kontrollera(projekten: dict[str, Projekt], stegen: list[Steg], fil: str) -> None:
    planerna = {s.namn for s in stegen}
    if okanda := sorted(set(projekten) - planerna):
        raise Datafel(f"{fil}: planen {okanda[0]!r} står inte bland detaljplanerna")
