"""Krav: K57 i docs/02-KRAV.md, ADR-0080. Test: tests/test_meetingsplus.py.

Formpipe Meetings Plus. Organets sida listar alla dess möten, och varje
mötes sida dess kallelse, protokoll och bilagor. Typen är avsnittets och
datumet mötets, utom i samlingsmötena, där ett "möte" rymmer ett helt
års protokoll och mönstren läser typ och datum ur filnamnet.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from urllib.parse import urlsplit

from kommunhandlingar import monster, schema
from kommunhandlingar.adaptrar import meetingsplus_html, sitevision
from kommunhandlingar.adaptrar.meetingsplus_html import Fil
from kommunhandlingar.fel import Hamtfel, IngenKandidat, Konfigurationsfel
from kommunhandlingar.kandidat import Avvisad, Kandidat

FALT = {"adapter", "sidor", "samlingsmoten", "monster"}
MONSTERGRUPPER = {"ar", "manad", "dag", "typ"}
# Länktexten slutar på .pdf; adressens sista del på pdf, ibland med ett löpnummer.
PDF = re.compile(r"(?i)pdf(-\d+)?$")


@dataclass(frozen=True)
class Kalla:
    sidor: dict[str, str]
    samlingsmoten: tuple[str, ...]
    monster: tuple[monster.Monster, ...]


def kalla_av(post: dict, organ_id: list[str], var: str) -> Kalla:
    schema.kontrollera_falt(post, FALT, var)
    sidor = sitevision.sidor(schema.varde(post, "sidor", dict, var), organ_id, var)
    samlingar = tuple(
        samlingsmote(a, sidor, var)
        for a in schema.textlista(post, "samlingsmoten", var)
    )
    poster = schema.valfritt(post, "monster", list, var) or []
    return Kalla(
        sidor,
        samlingar,
        tuple(monster.kompilera(p, MONSTERGRUPPER, f"{var}, mönster") for p in poster),
    )


def samlingsmote(adress: str, sidor: dict[str, str], var: str) -> str:
    """Mötessidan direkt under en organsida bredvid källans, skriven som
    upptäckten skriver den."""
    if not any(meetingsplus_html.under_en_organsida(adress, s) for s in sidor.values()):
        raise Konfigurationsfel(f"{var}: samlingsmötet {adress} är inget möte i källan")
    return adress.rstrip("/")


def upptack(
    kalla: Kalla, hamta_sida: Callable[[str], str]
) -> tuple[list[Kandidat], list[Avvisad]]:
    """En mötessida som inte går att hämta stoppar inte de andra (ADR-0080)."""
    kandidater: list[Kandidat] = []
    avvisade: list[Avvisad] = []
    missade: set[tuple[str, date]] = set()
    for organ, organsida in kalla.sidor.items():
        for motessida in egna_moten(kalla, organ, hamta_sida(organsida)):
            try:
                html = hamta_sida(motessida)
            except Hamtfel as fel:
                missade.add((organ, motesdatum(motessida)))
                avvisade.append(Avvisad(motessida, "mötessidan", fel.orsak))
                continue
            nya, bort = las_mote(kalla, organ, motessida, html)
            kandidater, avvisade = kandidater + nya, avvisade + bort
    return utan_missade_dagar(kandidater, missade), avvisade


def egna_moten(kalla: Kalla, organ: str, html: str) -> list[str]:
    """Ett möte under ett annat organs sida i källan är det organets (ADR-0080)."""
    andra = {s.rstrip("/") for o, s in kalla.sidor.items() if o != organ}
    moten = meetingsplus_html.moten(html, kalla.sidor[organ])
    return [m for m in moten if m.rpartition("/")[0] not in andra]


def utan_missade_dagar(
    kandidater: list[Kandidat], missade: set[tuple[str, date]]
) -> list[Kandidat]:
    """Ett annat möte samma dag kunde annars ta det missade mötets plats i
    poolen; organets kandidater den dagen väntar till nästa körning."""
    return [k for k in kandidater if (k.organ, k.datum) not in missade]


def las_mote(
    kalla: Kalla, organ: str, motessida: str, html: str
) -> tuple[list[Kandidat], list[Avvisad]]:
    kandidater: list[Kandidat] = []
    avvisade: list[Avvisad] = []
    for fil in motets_filer(meetingsplus_html.filer(html, motessida)):
        try:
            kandidater.append(kandidat(kalla, organ, motessida, fil))
        except IngenKandidat as fel:
            avvisade.append(Avvisad(motessida, fil.filnamn, str(fel)))
    return kandidater, avvisade


def motets_filer(filer: list[Fil]) -> list[Fil]:
    """Protokollets bilagor är oftast kallelsens igen, under en annan
    adress; bara de med ett eget filnamn tas med."""
    kallelsens = {f.filnamn for f in filer if f.del_ == "bilaga"}
    return [
        f
        for f in filer
        if f.del_ != "protokollets bilaga" or f.filnamn not in kallelsens
    ]


def kandidat(kalla: Kalla, organ: str, motessida: str, fil: Fil) -> Kandidat:
    if not PDF.search(fil.filnamn):
        raise IngenKandidat("inte en PDF")
    typ, datum = typ_och_datum(kalla, motessida, fil)
    return Kandidat(
        organ=organ,
        datum=datum,
        typ=typ,
        url=fil.adress,
        kalla=motessida,
        kallnyckel=f"meetingsplus:{fil.sokvag}",
        filnamn=fil.filnamn,
    )


def typ_och_datum(kalla: Kalla, motessida: str, fil: Fil) -> tuple[str, date]:
    if motessida in kalla.samlingsmoten:
        tolkning = monster.tolka(kalla.monster, fil.filnamn, ())
        if tolkning.datum is None:
            raise IngenKandidat("samlingsmötets fil har inget datum i filnamnet")
        return tolkning.typ, tolkning.datum
    typ = "bilaga" if fil.del_ == "protokollets bilaga" else fil.del_
    return typ, motesdatum(motessida)


def motesdatum(motessida: str) -> date:
    sista = urlsplit(motessida).path.rstrip("/").rpartition("/")[2]
    traff = meetingsplus_html.MOTESDATUM.search(sista)
    return monster.datum_av(traff.groupdict(), ())
