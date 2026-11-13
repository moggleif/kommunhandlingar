"""Krav: K46 i docs/02-KRAV.md, ADR-0069. Test: tests/test_projekt.py.

Läser kopplingsfilen, `projekt/<kommun>.csv`: en rad per detaljplan som
hör till ett projekt på kommunens lista med projekt (K45). Projektet är
projektsidans sista del i adressen, och dess dokument är projektorganets
dokument vars namn börjar med det (ADR-0068). Ett dokument hör till det
längsta av filens projekt som namnet börjar med, så att `asa-restaurangstrak`
inte tar `asa-restaurangstrak-del-2`:s dokument när båda står i filen
(docs/03-ARKITEKTUR.md#projekten). Planens kort på detaljplanssidan
får en länk till projektsidan och en lista med dokumenten.
"""

import csv
import re
from dataclasses import dataclass
from html import escape
from itertools import islice, takewhile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from kommunhandlingar import frontmatter
from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.plats import namn_av
from kommunhandlingar.webbplats.spar import Steg

# Spårslaget vars saker är detaljplanerna.
SLAG = "detaljplaner"
KOLUMNER = ["organ", "detaljplan", "projekt", "tolkad"]
# Datum, titel och adress för varje dokument.
Dokument = tuple[tuple[str, str, str], ...]
# Datum, namn, titel och adress för ett organs dokument.
Pool = tuple[tuple[str, str, str, str], ...]


@dataclass(frozen=True)
class Projekt:
    plan: str
    # Projektsidans adress på kommunens webbplats.
    adress: str
    tolkad: bool
    # Projektets dokument i poolen.
    dokument: Dokument


def las(fil: Path, kommun: Kommun, data: Path) -> dict[str, Projekt]:
    with fil.open(encoding="utf-8", newline="") as f:
        rader = list(csv.reader(f))
    if not rader or rader[0] != KOLUMNER:
        raise Datafel(f"{fil}: rubrikerna är inte {','.join(KOLUMNER)}")
    listor = {o: a for k in kommun.kallor for o, a in k.projekt.items()}
    for nr, rad in enumerate(rader[1:], 2):
        if fel := radfel(rad, listor, {r[1] for r in rader[1 : nr - 1]}):
            raise Datafel(f"{fil}, rad {nr}: {fel}")
    pool = {organ: poolens(data, organ) for organ, *_ in rader[1:]}
    return {
        rad[1]: projektet(rad, listor[rad[0]], pool[rad[0]], rader[1:])
        for rad in rader[1:]
    }


def radfel(rad: list[str], listor: dict[str, str], tidigare: set[str]) -> str:
    if len(rad) != len(KOLUMNER):
        return f"{len(rad)} fält, inte {len(KOLUMNER)}"
    organ, plan, projekt, tolkad = rad
    if organ not in listor:
        return f"organet {organ!r} har ingen lista med projekt i kommunfilen"
    if not plan or plan in tidigare:
        return f"planen {plan!r} är tom eller står redan i filen"
    if not re.fullmatch(r"[a-z0-9-]+", projekt):
        return f"projektet {projekt!r} är inte en del av en adress"
    if tolkad not in ("", "ja"):
        return f"tolkad {tolkad!r} är varken tom eller ja"
    return ""


def projektet(
    rad: list[str], lista: str, pool: Pool, rader: list[list[str]]
) -> Projekt:
    organ, plan, projekt, tolkad = rad
    namn = namn_av(projekt)
    langre = [namn_av(r[2]) for r in rader if r[0] == organ]
    langre = [n for n in langre if n.startswith(namn + "-")]
    dokument = tuple(
        (datum, titel, adress)
        for datum, d, titel, adress in pool
        if d.startswith(namn + "-") and not any(d.startswith(n + "-") for n in langre)
    )
    return Projekt(plan, f"{lista}/{projekt}", tolkad == "ja", dokument)


# Organets dokument, bara front matter, lästa en gång per organ.
def poolens(data: Path, organ: str) -> Pool:
    return tuple(sorted(dokumentet(fil, data) for fil in (data / organ).rglob("*.md")))


# Titeln är källans filnamn, med å, ä och ö, som namnet saknar.
def dokumentet(fil: Path, data: Path) -> tuple[str, str, str, str]:
    with fil.open(encoding="utf-8") as f:
        huvud = "".join(takewhile(lambda r: r != "---\n", islice(f, 1, None)))
    falt = frontmatter.las(f"---\n{huvud}---\n")
    kalla = frontmatter.adresser(falt["kalla_url"])[0]
    titel = unquote(PurePosixPath(urlsplit(kalla).path).stem)
    adress = fil.relative_to(data).with_suffix(".html").as_posix()
    return falt["datum"], falt["namn"], titel, adress


def kontrollera(projekten: dict[str, Projekt], stegen: list[Steg], fil: str) -> None:
    planerna = {s.namn for s in stegen}
    if okanda := sorted(set(projekten) - planerna):
        raise Datafel(f"{fil}: planen {okanda[0]!r} står inte bland detaljplanerna")


# Länken till projektsidan och projektets dokument, som ligger i ett
# annat organs katalog.
def kortdel(projekt: Projekt | None) -> str:
    if not projekt:
        return ""
    tolkad = " <small>tolkad</small>" if projekt.tolkad else ""
    lank = (
        f'<p><a href="{escape(projekt.adress)}">Kommunens projektsida</a>{tolkad}</p>'
    )
    if not projekt.dokument:
        return lank + "<p>Projektets dokument: inga i poolen.</p>"
    poster = "".join(
        f'<li><a href="../{escape(adress)}">'
        f"{escape(namn.replace('-', ' ').capitalize())}</a> {datum}</li>"
        for datum, namn, adress in projekt.dokument
    )
    return (
        lank + "<details><summary>Projektets dokument i poolen, "
        f"{len(projekt.dokument)} st</summary><ul>{poster}</ul></details>"
    )
