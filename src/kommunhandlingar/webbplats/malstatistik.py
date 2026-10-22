"""Krav: K27, K28, K29 och K35 i docs/02-KRAV.md, ADR-0045, ADR-0046, ADR-0050
och ADR-0056. Test: tests/test_malgrupper.py, tests/test_uppfoljningar.py och
tests/test_fokusomraden.py.

Antalet per år på sidan om ett organs mål och direktiv: rubrikerna av
varje slag som finns på sidan, uppföljningarna i poolen som redovisar dem,
och rubrikerna med en bedömning i någon av dem, och ur protokollen
uppföljningarna och dragningarna om målen i nämnden. Ett år utan rader, eller
utan protokoll i poolen, är tomt, inte noll. Det senaste årets antal står
bredvid grafen, och tabellen är hopfälld under dem.
"""

from dataclasses import dataclass

from kommunhandlingar.webbplats.mal import SLAG, Mal
from kommunhandlingar.webbplats.malgraf import graf
from kommunhandlingar.webbplats.uppfoljningar import Uppfoljning

FORKLARING = (
    "<p>Varje mål räknas en gång per år, också när det har två rubriker. "
    "Uppföljningarna är de delårsrapporter, årsredovisningar och andra "
    "rapporter till nämnden som målen är lästa ur; en uppföljning som inte "
    "gått att hämta till poolen räknas inte. Ett år utan mål står som –, "
    "eftersom dokumenten kan saknas i poolen. Uppföljningar och dragningar "
    "i nämnden är paragraferna i mötets protokoll där nämnden godkänner "
    "eller tar emot en uppföljning, som årsredovisningen, delårsrapporten "
    "eller uppföljningen per april, eller noterar en dragning om målen, "
    "och räknas på mötets år. Ett år utan protokoll i poolen står som –, och "
    "protokoll kan saknas också andra år.</p>"
)
FLERTAL = {
    "nämndmål": "nämndmål",
    "kommunmål": "kommunmål",
    "fokusområde": "fokusområden",
    "direktiv": "direktiv",
}
RUBRIKER = ("Uppföljningar med målen", "Med bedömning")
NAMNDEN = ("uppföljningar i nämnden", "dragningar om målen")

UTAN_TEXT = ("ej-hamtad", "ej-konverterad")


@dataclass(frozen=True)
class Antal:
    per_slag: tuple[int, ...]
    uppfoljningar: int
    med_bedomning: int

    @property
    def tal(self) -> tuple[int, ...]:
        return (*self.per_slag, self.uppfoljningar, self.med_bedomning)


def statistik(
    malen: list[Mal], uppfoljningar: list[Uppfoljning], protokollar: set[int]
) -> str:
    ar = range(min(m.ar for m in malen), max(m.ar for m in malen) + 1)
    slagen = [s for s in SLAG if any(m.slag == s for m in malen)]
    antal = [rakna([m for m in malen if m.ar == a], slagen) for a in ar]
    namnden = [
        i_namnden([u for u in uppfoljningar if u.ar == a]) if a in protokollar else None
        for a in ar
    ]
    serier = [
        (FLERTAL[s].capitalize(), [a and a.per_slag[i] for a in antal])
        for i, s in enumerate(slagen)
    ]
    return (
        '<h2 id="antal">Antal per år</h2><div class="sammandrag">'
        + senaste(ar[-1], slagen, antal[-1], namnden[-1])
        + f'<div class="ruta">{graf(list(ar), serier)}</div></div>'
        + "<details><summary>Tabell över antal per år</summary>"
        + tabell(ar, slagen, antal, namnden)
        + FORKLARING
        + "</details>"
    )


# Det senaste året har alltid mål, eftersom åren slutar med målens sista år.
def senaste(ar: int, slagen: list[str], antal: Antal, namnden: tuple | None) -> str:
    tal = list(zip(antal.per_slag, (FLERTAL[s] for s in slagen), strict=True))
    if namnden:
        tal += zip(namnden, NAMNDEN, strict=True)
    siffror = "".join(f"<div><dt>{text}</dt><dd>{n}</dd></div>" for n, text in tal)
    return f'<div class="ruta"><h3>{ar}</h3><dl class="siffror">{siffror}</dl></div>'


# Uppföljningarna i nämnden räknas bara år med ett protokoll med text.
def protokollar(organets: list[dict]) -> set[int]:
    return {
        int(d["datum"][:4])
        for d in organets
        if d["typ"] == "protokoll" and d["kvalitet"] not in UTAN_TEXT
    }


def rakna(arets: list[Mal], slagen: list[str]) -> Antal | None:
    if not arets:
        return None
    uppfoljda = [m for m in arets if m.uppfoljning]
    return Antal(
        tuple(len({m.spar for m in arets if m.slag == s}) for s in slagen),
        len({m.dokument for m in uppfoljda}),
        len({m.spar for m in uppfoljda if m.bedomning != "ingen"}),
    )


def i_namnden(arets: list[Uppfoljning]) -> tuple[int, int]:
    return (
        sum(u.slag == "uppföljning" for u in arets),
        sum(u.slag == "dragning" for u in arets),
    )


def tabell(ar: range, slagen: list[str], antal: list[Antal | None], namnden) -> str:
    rubriker = ["År", *(FLERTAL[s].capitalize() for s in slagen), *RUBRIKER]
    rubriker += [n.capitalize() for n in NAMNDEN]
    huvud = "".join(f'<th scope="col">{t}</th>' for t in rubriker)
    kolumner = len(slagen) + len(RUBRIKER)
    rader = "".join(
        f'<tr><th scope="row">{a}</th>'
        + "".join(f'<td class="tal">{t}</td>' for t in tal_i(n and n.tal, kolumner))
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
