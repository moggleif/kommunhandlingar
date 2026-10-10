"""Krav: K17 i docs/02-KRAV.md, ADR-0022. Test: tests/test_webbplats_dokument.py."""

from collections import defaultdict
from html import escape

from kommunhandlingar.frontmatter import lista
from kommunhandlingar.kandidat import TYPORDNING
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats.mall import Mall, sida, stig
from kommunhandlingar.webbplats.rakning import Organrad

Mote = tuple[str, str]


def organsida(mall: Mall, kommun: Kommun, rad: Organrad, dokument: list[dict]) -> str:
    moten = defaultdict(list)
    for d in dokument:
        moten[(d["datum"], d["lopnr"])].append(d)
    saknas = {(lucka.datum, lucka.lopnr): lucka.saknas for lucka in rad.luckor}
    ar = defaultdict(list)
    for mote in sorted(moten, key=ordning, reverse=True):
        ar[mote[0][:4]].append(motesavsnitt(mote, moten[mote], saknas.get(mote, ())))
    innehall = stig([(f"../{kommun.id}.html", kommun.namn)]) + (
        "".join(f"<h2>{escape(a)}</h2>{''.join(m)}" for a, m in ar.items())
        or "<p>Inget hämtat än.</p>"
    )
    return sida(mall, f"{kommun.id}/{rad.id}.html", rad.namn, innehall)


# Det första sammanträdet en dag har inget löpnummer, nästa har 2 (ADR-0003).
def ordning(mote: Mote) -> tuple[str, int]:
    datum, lopnr = mote
    return datum, int(lopnr.replace("null", "1"))


def motesnamn(mote: Mote) -> str:
    datum, lopnr = mote
    return datum if lopnr == "null" else f"{datum}-{lopnr}"


def motesavsnitt(mote: Mote, dokument: list[dict], saknas: tuple[str, ...]) -> str:
    ordnade = sorted(dokument, key=lambda d: (TYPORDNING.index(d["typ"]), d["namn"]))
    poster = [dokumentpost(d) for d in ordnade]
    poster += [f"{escape(grupp)} saknas" for grupp in saknas]
    namn = escape(motesnamn(mote))
    lista_ = "".join(f"<li>{post}</li>" for post in poster)
    return f'<h3 id="{namn}">{namn}</h3><ul>{lista_}</ul>'


def dokumentpost(d: dict) -> str:
    rubrik = d["typ"] + ("" if d["namn"] == "null" else f" – {d['namn']}")
    rader = [f"kvalitet {d['kvalitet']}"]
    if d["fel"] != "null":
        rader.append(f"fel {d['fel']}")
    if obekraftade := len(lista(d["tal_obekraftade"])):
        rader.append(f"obekräftade tal på {obekraftade} sidor")
    return f'<a href="{escape(d["adress"])}">{escape(rubrik)}</a>: ' + escape(
        ", ".join(rader)
    )
