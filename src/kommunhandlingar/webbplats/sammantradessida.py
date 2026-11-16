"""Krav: K54 i docs/02-KRAV.md, ADR-0078. Test: tests/test_sammantradessida.py.

Sammanträdets sida: en rad per dokument från sammanträdet och sedan
dagordningen, en punkt i taget (`punktkort.py`). Sidan ligger bredvid
sammanträdets katalog. Stilen är målkortens (`mal.css`) och `mote.css`.
"""

from html import escape
from pathlib import Path

from kommunhandlingar.webbplats.kortkoppling import organnamn
from kommunhandlingar.webbplats.luckor import motesnamn
from kommunhandlingar.webbplats.mall import Mall, rot, sida, stig
from kommunhandlingar.webbplats.meny import oversiktsnamn
from kommunhandlingar.webbplats.organsida import dokumentrubrik
from kommunhandlingar.webbplats.punktkort import Lankar, antal, punktkort
from kommunhandlingar.webbplats.sammantrade import Arende, Mote, adress, ordnade

STIL = [Path(__file__).with_name(f) for f in ("mal.css", "mote.css")]


def sammantradessida(mall: Mall, mote: Mote, arenden: list[Arende]) -> str:
    kommun, forsta = mote.kommun, mote.dokument[0]
    sidans, namn = f"{kommun.id}/{adress(mote.dokument)}", organnamn(kommun)
    lankar = Lankar(rot(sidans), handlingarna(kommun.id, mote.dokument), namn)
    vag = [
        (f"{lankar.rot}{kommun.id}.html", oversiktsnamn(mall.kommuner, kommun)),
        (f"{lankar.rot}{kommun.id}/{forsta['organ']}.html", namn[forsta["organ"]]),
    ]
    innehall = (
        stig(vag)
        + "<style>"
        + "".join(f.read_text(encoding="utf-8") for f in STIL)
        + "</style><h2>Sammanträdets dokument</h2>"
        + dokumentlista(kommun.id, mote.dokument, lankar.rot)
        + dagordningen(arenden, lankar)
    )
    rubrik = f"{namn[forsta['organ']]} {motesnamn(forsta['datum'], forsta['lopnr'])}"
    return sida(mall, sidans, rubrik, innehall)


def dagordningen(arenden: list[Arende], lankar: Lankar) -> str:
    if not arenden:
        return (
            "<h2>Dagordningen</h2><p>Dagordningen gick inte att läsa ur kallelsen.</p>"
        )
    hittade = sum(1 for a in arenden if a.handling)
    return (
        f"<h2>Dagordningen, {antal(len(arenden), 'punkt', 'punkter')}</h2>"
        "<p>Varje punkt med förslaget ur kallelsen, handlingens sidor, beslutet "
        "i protokollet och historiken i alla organ med samma diarienummer, som "
        f"det står i källan. Handlingen hittades för {hittade} av "
        f"{len(arenden)}.</p>"
        '<div class="malkort punkter">'
        + "".join(punktkort(a, lankar) for a in arenden)
        + "</div>"
    )


def dokumentlista(kommun_id: str, dokument: list[dict], till_rot: str) -> str:
    rader = "".join(
        f'<li><a href="{escape(till_rot + kommun_id + "/" + d["adress"])}">'
        f"{escape(dokumentrubrik(d).capitalize())}</a>{sidantal(d)}</li>"
        for d in ordnade(dokument)
    )
    return f"<ul>{rader}</ul>"


def handlingarna(kommun_id: str, dokument: list[dict]) -> str:
    adresser = [d["adress"] for d in ordnade(dokument) if d["typ"] == "handlingar"]
    return f"{kommun_id}/{adresser[0]}" if adresser else ""


def sidantal(d: dict) -> str:
    if d["sidor"] == "null":
        return ""
    return f" <small>{antal(int(d['sidor']), 'sida', 'sidor')}</small>"
