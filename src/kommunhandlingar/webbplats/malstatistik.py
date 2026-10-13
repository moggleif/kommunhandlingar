"""Krav: K27, K28 och K29 i docs/02-KRAV.md, ADR-0045, ADR-0046 och ADR-0047.
Test: tests/test_malgrupper.py och tests/test_uppfoljningar.py.

Antalet per år på sidan om ett organs mål och direktiv: nämndmål och
direktiv med olika rubriker, uppföljningarna i poolen som redovisar dem,
och rubrikerna med en bedömning i någon av dem, och ur protokollen
uppföljningarna och dragningarna om målen i nämnden. Ett år utan rader, eller
utan protokoll i poolen, är tomt, inte noll. Det senaste årets antal står
bredvid grafen, och tabellen är hopfälld under dem.
"""

from dataclasses import astuple, dataclass

from kommunhandlingar.webbplats.mal import Mal
from kommunhandlingar.webbplats.malgraf import graf
from kommunhandlingar.webbplats.uppfoljningar import Uppfoljning

FORKLARING = (
    "<p>Varje rubrik räknas en gång per år. Uppföljningarna är de "
    "delårsrapporter, årsredovisningar och andra rapporter till nämnden som "
    "målen är lästa ur; en uppföljning som inte gått att hämta till poolen "
    "räknas inte. Ett år utan mål står som –, eftersom dokumenten kan "
    "saknas i poolen. Uppföljningar och dragningar i nämnden är paragraferna "
    "i mötets protokoll där nämnden godkänner eller tar emot en uppföljning, "
    "som årsredovisningen, delårsrapporten eller uppföljningen per april, "
    "eller noterar en dragning om målen, och räknas på mötets år. Ett år "
    "utan protokoll i poolen står som –, och protokoll kan saknas också "
    "andra år.</p>"
)
RUBRIKER = (
    "År",
    "Nämndmål",
    "Direktiv",
    "Uppföljningar med målen",
    "Med bedömning",
    "Uppföljningar i nämnden",
    "Dragningar om målen",
)

UTAN_TEXT = ("ej-hamtad", "ej-konverterad")


@dataclass(frozen=True)
class Antal:
    namndmal: int
    direktiv: int
    uppfoljningar: int
    med_bedomning: int


def statistik(
    malen: list[Mal], uppfoljningar: list[Uppfoljning], protokollar: set[int]
) -> str:
    ar = range(min(m.ar for m in malen), max(m.ar for m in malen) + 1)
    antal = [rakna([m for m in malen if m.ar == a]) for a in ar]
    namnden = [
        i_namnden([u for u in uppfoljningar if u.ar == a]) if a in protokollar else None
        for a in ar
    ]
    serier = [
        ("Nämndmål", [a and a.namndmal for a in antal]),
        ("Direktiv", [a and a.direktiv for a in antal]),
    ]
    return (
        '<h2 id="antal">Antal per år</h2><div class="sammandrag">'
        + senaste(ar[-1], antal[-1], namnden[-1])
        + f'<div class="ruta">{graf(list(ar), serier)}</div></div>'
        + "<details><summary>Tabell över antal per år</summary>"
        + tabell(ar, antal, namnden)
        + FORKLARING
        + "</details>"
    )


# Det senaste året har alltid mål, eftersom åren slutar med målens sista år.
def senaste(ar: int, antal: Antal, namnden: tuple[int, int] | None) -> str:
    tal = [(antal.namndmal, "nämndmål"), (antal.direktiv, "direktiv")]
    if namnden:
        tal += zip(
            namnden, ("uppföljningar i nämnden", "dragningar om målen"), strict=True
        )
    siffror = "".join(f"<div><dt>{text}</dt><dd>{n}</dd></div>" for n, text in tal)
    return f'<div class="ruta"><h3>{ar}</h3><dl class="siffror">{siffror}</dl></div>'


# Uppföljningarna i nämnden räknas bara år med ett protokoll med text.
def protokollar(organets: list[dict]) -> set[int]:
    return {
        int(d["datum"][:4])
        for d in organets
        if d["typ"] == "protokoll" and d["kvalitet"] not in UTAN_TEXT
    }


def rakna(arets: list[Mal]) -> Antal | None:
    if not arets:
        return None
    uppfoljda = [m for m in arets if m.uppfoljning]
    return Antal(
        len({m.namn for m in arets if m.slag == "nämndmål"}),
        len({m.namn for m in arets if m.slag == "direktiv"}),
        len({m.kalla.split("#")[0] for m in uppfoljda}),
        len({m.namn for m in uppfoljda if m.bedomning != "ingen"}),
    )


def i_namnden(arets: list[Uppfoljning]) -> tuple[int, int]:
    return (
        sum(u.slag == "uppföljning" for u in arets),
        sum(u.slag == "dragning" for u in arets),
    )


def tabell(ar: range, antal: list[Antal | None], namnden: list) -> str:
    huvud = "".join(f'<th scope="col">{t}</th>' for t in RUBRIKER)
    rader = "".join(
        f'<tr><th scope="row">{a}</th>'
        + "".join(f'<td class="tal">{t}</td>' for t in tal_i(n and astuple(n), 4))
        + "".join(f'<td class="tal">{t}</td>' for t in tal_i(i, 2))
        + "</tr>"
        for a, n, i in zip(ar, antal, namnden, strict=True)
    )
    return (
        f'<div class="tabell"><table><thead><tr>{huvud}</tr></thead>'
        f"<tbody>{rader}</tbody></table></div>"
    )


# Ett år utan uppgift är ett streck i varje kolumn, inte en nolla.
def tal_i(varden: tuple[int, ...] | None, kolumner: int) -> list[str]:
    if varden is None:
        return ["–"] * kolumner
    return [str(v) for v in varden]
