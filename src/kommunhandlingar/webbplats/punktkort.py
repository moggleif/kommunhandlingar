"""Krav: K54 i docs/02-KRAV.md, ADR-0078. Test: tests/test_sammantradessida.py.

En punkt på dagordningen som ett kort: numret, diarienumret, rubriken,
förslaget ur kallelsen, sammanfattningen ur tjänsteskrivelsen, handlingens
sidor, beslutet i protokollet och historiken. Det som inte hittades sägs.
"""

from dataclasses import dataclass
from html import escape

from kommunhandlingar.webbplats.dagordning import FORSLAG
from kommunhandlingar.webbplats.kortkoppling import Kortlank
from kommunhandlingar.webbplats.sammantrade import Arende


@dataclass(frozen=True)
class Lankar:
    # Från sidan till webbplatsens rot.
    rot: str
    # Handlingarnas sida, från webbplatsens rot; tomt utan handlingar.
    handlingar: str
    organnamn: dict[str, str]


def punktkort(arende: Arende, lankar: Lankar) -> str:
    punkt = arende.punkt
    rubrik = punkt.rubrik or (arende.beslut or {}).get("rubrik") or "Rubriken saknas"
    return (
        f'<article id="punkt-{punkt.nummer}"><p class="markor">'
        f"<span>Punkt {punkt.nummer}</span>{dnr(arende.diarienummer)}</p>"
        f"<h3>{escape(rubrik)}</h3>"
        + forslag(punkt.forslag)
        + sammanfattning(arende.sammanfattning, arende.handling)
        + handling(arende.handling, lankar)
        + utfall(arende, lankar)
        + "</article>"
    )


def dnr(nummer: str) -> str:
    return f"<span>Dnr {escape(nummer)}</span>" if nummer else ""


# Utan diarienummer finns inget att söka beslutet och historiken på.
def utfall(arende: Arende, lankar: Lankar) -> str:
    if not arende.diarienummer:
        return (
            "<p>Punkten har inget diarienummer i kallelsen, så beslut och "
            "historik söks inte.</p>"
        )
    return beslut(arende.beslut, lankar) + historik(arende, lankar)


def forslag(stycken: tuple[str, ...] | None) -> str:
    if stycken is None:
        return "<p>Förslaget gick inte att läsa ur kallelsen.</p>"
    if not stycken:
        return "<p>Inget förslag till beslut i kallelsen.</p>"
    return "".join(
        f"<h4>{escape(s)}</h4>"
        if s.startswith(FORSLAG)
        else f"<blockquote>{escape(s)}</blockquote>"
        for s in stycken
    )


# Utan handling säger raden om handlingen det; med handling men utan
# avsnittet sägs det här.
def sammanfattning(stycken: tuple[str, ...], omfang: range | None) -> str:
    if not omfang:
        return ""
    if not stycken:
        return "<p>Ingen sammanfattning av ärendet i handlingen.</p>"
    text = "".join(f"<p>{escape(s)}</p>" for s in stycken)
    rubrik = "<summary>Sammanfattning ur tjänsteskrivelsen</summary>"
    return f"<details>{rubrik}{text}</details>"


def handling(omfang: range | None, lankar: Lankar) -> str:
    if not omfang:
        return "<p>Handlingen: ingen egen handling hittad för punkten.</p>"
    adress = f"{lankar.rot}{lankar.handlingar}#sida-{omfang.start}"
    sidor = f"sidorna {omfang.start}–{omfang[-1]}"
    if len(omfang) == 1:
        sidor = f"sidan {omfang.start}"
    return f'<p>Handlingen: <a href="{escape(adress)}">{sidor} i handlingarna</a></p>'


def beslut(paragraf: dict | None, lankar: Lankar) -> str:
    if not paragraf:
        return "<h4>Beslut</h4><p>Ingen paragraf med diarienumret i protokollet.</p>"
    text = escape(paragraf["beslut"] or "Beslutstexten gick inte att läsa ut.")
    return f"<h4>Beslut</h4><p>{paragrafs_lank(paragraf, lankar)}: {text}</p>"


def historik(arende: Arende, lankar: Lankar) -> str:
    if not (arende.historik or arende.kort):
        return "<p>Historik: inga andra paragrafer med diarienumret i poolen.</p>"
    kort = "".join(kortpost(k, lankar) for k in arende.kort)
    poster = "".join(paragraf(p, arende.diarienummer, lankar) for p in arende.historik)
    hur_manga = (
        f"{antal(len(arende.historik), 'paragraf', 'paragrafer')}, "
        f"{len(arende.kort)} kort"
    )
    return (
        f"<details><summary>Historik: {hur_manga}</summary>"
        f"{f'<ul>{kort}</ul>' if kort else ''}<ol>{poster}</ol></details>"
    )


def kortpost(kort: Kortlank, lankar: Lankar) -> str:
    tolkad = " <small>tolkad</small>" if kort.tolkad else ""
    adress = escape(lankar.rot + kort.adress)
    return f'<li>Följs på <a href="{adress}">{escape(kort.rubrik)}</a>{tolkad}</li>'


# Diarienumren står efter en paragraf som kom med genom ett annat nummer.
def paragraf(p: dict, nummer: str, lankar: Lankar) -> str:
    annat = ""
    if nummer not in p["diarienummer"]:
        annat = f" <small>({escape(', '.join(p['diarienummer']))})</small>"
    return (
        f"<li><b>{p['datum']}</b> {escape(lankar.organnamn[p['organ']])} "
        f"{paragrafs_lank(p, lankar)} {escape(p['rubrik'] or '')}{annat}</li>"
    )


def paragrafs_lank(p: dict, lankar: Lankar) -> str:
    return f'<a href="{escape(lankar.rot + p["sida"])}">§ {p["paragraf"]}</a>'


def antal(tal: int, ett: str, flera: str) -> str:
    return f"{tal} {ett if tal == 1 else flera}"
