"""Krav: K39 i docs/02-KRAV.md, ADR-0060. Test: tests/test_navigering.py.

Kommunens sida: en rad per organ med antalet sammanträden och en kolumn
per sida över tid, så att det syns vilka organ som har vilka sidor. Ett
utskott står direkt under organet det hör till.
"""

from html import escape

from kommunhandlingar.konfiguration import Kommun, Organ
from kommunhandlingar.webbplats.flikar import overtid
from kommunhandlingar.webbplats.mall import Mall, sida
from kommunhandlingar.webbplats.rakning import Organrad

TOM = '<td class="tom">–</td>'


def kommunsida(mall: Mall, kommun: Kommun, rader: list[Organrad]) -> str:
    sammantraden = {rad.id: rad.sammantraden for rad in rader}
    kolumner = [rubrik for _, rubrik, _ in overtid(mall, kommun.id, "")]
    huvud = "".join(f'<th scope="col">{escape(k)}</th>' for k in kolumner)
    kropp = "".join(
        organrad(mall, kommun.id, organ, sammantraden[organ.id])
        for organ in ordning(kommun.organ)
    )
    innehall = (
        "<p>Organen med antalet sammanträden i poolen och sidorna som följer "
        "dem över tid. Ett streck betyder att organet inte har sidan.</p>"
        '<div class="tabell"><table class="oversikt"><thead><tr>'
        f'<th scope="col">Organ</th><th scope="col">Sammanträden</th>{huvud}'
        f"</tr></thead><tbody>{kropp}</tbody></table></div>"
    )
    return sida(mall, f"{kommun.id}.html", kommun.namn, innehall)


# Kommunfilens ordning, men varje utskott direkt efter sitt organ.
def ordning(organen: tuple[Organ, ...]) -> list[Organ]:
    plats = {o.id: i for i, o in enumerate(organen)}
    return sorted(organen, key=lambda o: (plats[o.hor_till or o.id], bool(o.hor_till)))


def organrad(mall: Mall, kommun_id: str, organ: Organ, sammantraden: int) -> str:
    klass = ' class="utskott"' if organ.hor_till else ""
    organets = f"{kommun_id}/{organ.id}.html"
    celler = "".join(
        f'<td><a href="{kommun_id}/{organ.id}/{sida}.html">{antal}</a></td>'
        if antal
        else TOM
        for sida, _, antal in overtid(mall, kommun_id, organ.id)
    )
    return (
        f'<tr><th scope="row"{klass}><a href="{organets}">'
        f"{escape(organ.namn[0])}</a></th>"
        f'<td><a href="{organets}">{sammantraden}</a></td>{celler}</tr>'
    )
