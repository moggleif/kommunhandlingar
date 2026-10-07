"""Krav: K14 i docs/02-KRAV.md. Test: tests/test_webbplats.py."""

from collections import Counter
from dataclasses import dataclass

from kommunhandlingar.frontmatter import lista
from kommunhandlingar.kandidat import TYPORDNING
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.konvertering.kvalitet import KVALITETER


@dataclass(frozen=True)
class Organrad:
    id: str
    namn: str
    sammantraden: int
    typer: Counter
    kvaliteter: Counter
    obekraftade_sidor: int

    @property
    def dokument(self) -> int:
        return self.typer.total()


def okanda(dokument: dict[str, str], kommun: Kommun) -> list[str]:
    tillatna = {
        "organ": {organ.id for organ in kommun.organ},
        "typ": set(TYPORDNING),
        "kvalitet": set(KVALITETER),
    }
    return [
        f"{falt} {dokument[falt]!r}"
        for falt, varden in tillatna.items()
        if dokument[falt] not in varden
    ]


def rakna(kommun: Kommun, dokument: list[dict[str, str]]) -> list[Organrad]:
    return [
        organrad(
            organ.id, organ.namn[0], [d for d in dokument if d["organ"] == organ.id]
        )
        for organ in kommun.organ
    ]


def organrad(organ_id: str, namn: str, dokument: list[dict[str, str]]) -> Organrad:
    return Organrad(
        organ_id,
        namn,
        len({(d["datum"], d["lopnr"]) for d in dokument}),
        Counter(d["typ"] for d in dokument),
        Counter(d["kvalitet"] for d in dokument),
        sum(len(lista(d["tal_obekraftade"])) for d in dokument),
    )
