"""Krav: K27 i docs/02-KRAV.md, ADR-0045. Test: tests/test_malgrupper.py.

Antalet per år på sidan om ett organs mål och direktiv: nämndmål och
direktiv med olika rubriker, uppföljningarna i poolen som redovisar dem,
och rubrikerna med en bedömning i någon av dem. Ett år utan rader är tomt,
inte noll.
"""

from dataclasses import dataclass

from kommunhandlingar.webbplats.mal import Mal
from kommunhandlingar.webbplats.malgraf import graf

FORKLARING = (
    "<p>Varje rubrik räknas en gång per år. Uppföljningarna är de "
    "delårsrapporter, årsredovisningar och andra rapporter till nämnden som "
    "målen är lästa ur; en uppföljning som inte gått att hämta till poolen "
    "räknas inte. Ett år utan mål står som –, eftersom dokumenten kan "
    "saknas i poolen.</p>"
)


@dataclass(frozen=True)
class Antal:
    namndmal: int
    direktiv: int
    uppfoljningar: int
    med_bedomning: int


def statistik(malen: list[Mal]) -> str:
    ar = range(min(m.ar for m in malen), max(m.ar for m in malen) + 1)
    antal = [rakna([m for m in malen if m.ar == a]) for a in ar]
    serier = [
        ("Nämndmål", [a and a.namndmal for a in antal]),
        ("Direktiv", [a and a.direktiv for a in antal]),
    ]
    return (
        '<h2 id="antal">Antal per år</h2>'
        + graf(list(ar), serier)
        + tabell(ar, antal)
        + FORKLARING
    )


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


def tabell(ar: range, antal: list[Antal | None]) -> str:
    huvud = "".join(
        f'<th scope="col">{t}</th>'
        for t in (
            "År",
            "Nämndmål",
            "Direktiv",
            "Uppföljningar med målen",
            "Med bedömning",
        )
    )
    rader = "".join(
        f'<tr><th scope="row">{a}</th>'
        + "".join(f'<td class="tal">{tal}</td>' for tal in tal_i(n))
        + "</tr>"
        for a, n in zip(ar, antal, strict=True)
    )
    return (
        f'<div class="tabell"><table><thead><tr>{huvud}</tr></thead>'
        f"<tbody>{rader}</tbody></table></div>"
    )


def tal_i(antal: Antal | None) -> list[str]:
    if antal is None:
        return ["–"] * 4
    return [
        str(t)
        for t in (
            antal.namndmal,
            antal.direktiv,
            antal.uppfoljningar,
            antal.med_bedomning,
        )
    ]
