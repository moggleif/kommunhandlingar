"""Krav: K39 i docs/02-KRAV.md, ADR-0060. Test: tests/test_navigering.py.

Kommunens sida: en rad per organ med antalet sammanträden och en kolumn
per sida över tid, så att det syns vilka organ som har vilka sidor. Ett
utskott står direkt under organet det hör till, och organen står i
kommunfilens grupper när den har några.
"""

from html import escape

from kommunhandlingar.konfiguration import Kommun, Organ
from kommunhandlingar.webbplats.flikar import SIDOR, overtid
from kommunhandlingar.webbplats.mall import Mall, sida
from kommunhandlingar.webbplats.rakning import Organrad

TOM = '<td class="tom">–<span class="dold"> saknas</span></td>'


def kommunsida(
    mall: Mall, kommun: Kommun, rader: list[Organrad], dokument: list[dict]
) -> str:
    sammantraden = {rad.id: rad.sammantraden for rad in rader}
    huvud = "".join(f'<th scope="col">{escape(r)}</th>' for _, r, _ in SIDOR)
    grupper = "".join(
        f"<tbody>{grupprad(namn, len(SIDOR) + 2)}"
        + "".join(organrad(mall, kommun.id, o, sammantraden[o.id]) for o in organen)
        + "</tbody>"
        for namn, organen in grupperade(kommun)
    )
    innehall = (
        inledning(dokument) + '<div class="tabell"><table class="oversikt"><thead><tr>'
        f'<th scope="col">Organ</th><th scope="col">Sammanträden</th>{huvud}'
        f"</tr></thead>{grupper}</table></div>"
    )
    return sida(mall, f"{kommun.id}.html", kommun.namn, innehall)


def inledning(dokument: list[dict]) -> str:
    datum = sorted(d["datum"] for d in dokument) or ["–"]
    antal = f"{len(dokument):,}".replace(",", " ")
    return (
        f"<p>{antal} dokument från {escape(datum[0])} till {escape(datum[-1])}. "
        "Välj ett organ, eller gå direkt till en av dess sidor över tid. "
        "Ett streck betyder att organet inte har sidan.</p>"
    )


# Utan grupper i kommunfilen står alla organ i en grupp utan namn.
def grupperade(kommun: Kommun) -> list[tuple[str, list[Organ]]]:
    ordnade = ordning(kommun.organ)
    if not kommun.grupper:
        return [("", ordnade)]
    grupp = {o.id: o.grupp for o in kommun.organ}
    return [
        (namn, [o for o in ordnade if grupp[o.hor_till or o.id] == namn])
        for namn in kommun.grupper
    ]


# Kommunfilens ordning, men varje utskott direkt efter sitt organ.
def ordning(organen: tuple[Organ, ...]) -> list[Organ]:
    plats = {o.id: i for i, o in enumerate(organen)}
    return sorted(organen, key=lambda o: (plats[o.hor_till or o.id], bool(o.hor_till)))


def grupprad(namn: str, kolumner: int) -> str:
    if not namn:
        return ""
    return (
        f'<tr class="grupp"><th scope="rowgroup" colspan="{kolumner}">'
        f"{escape(namn)}</th></tr>"
    )


def organrad(mall: Mall, kommun_id: str, organ: Organ, sammantraden: int) -> str:
    klass = ' class="utskott"' if organ.hor_till else ""
    organets = f"{kommun_id}/{organ.id}.html"
    antal = overtid(mall, kommun_id, organ.id)
    celler = "".join(
        f'<td><a href="{kommun_id}/{organ.id}/{sida}.html">'
        f"{antal[sida]} {escape(enhet)}</a></td>"
        if antal[sida]
        else TOM
        for sida, _, enhet in SIDOR
    )
    return (
        f'<tr><th scope="row"{klass}><a href="{organets}">'
        f"{escape(organ.namn[0])}</a></th>"
        f'<td><a href="{organets}">{sammantraden}</a></td>{celler}</tr>'
    )
