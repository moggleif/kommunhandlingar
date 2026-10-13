"""Krav: K27 i docs/02-KRAV.md, ADR-0045. Test: tests/test_mal.py.

En linjegraf i SVG, utan skript: år längs x-axeln, antal längs y-axeln
och en linje per serie. Serierna skiljs med streckning och punktform, inte
med färg. Ett år utan värde är ett avbrott i linjen, inte en nolla.
"""

from html import escape
from itertools import groupby

BREDD, HOJD = 640, 260
VANSTER, HOGER, TOPP, BOTTEN = 40, 16, 36, 30
# Linjens streckning och punktens fyllning per serie, i seriernas ordning.
STILAR = [("", "currentColor"), ('stroke-dasharray="6 4"', "#fff")]

Serie = tuple[str, list[int | None]]


def graf(ar: list[int], serier: list[Serie]) -> str:
    topp = max([v for _, varden in serier for v in varden if v is not None] + [1])
    steg = 1 if topp <= 6 else 2 if topp <= 12 else 5
    topp = -(-topp // steg) * steg
    punkt = punktare(len(ar), topp)
    delar = [axlar(ar, topp, steg, punkt)]
    for nr, (namn, varden) in enumerate(serier):
        delar.append(linje(varden, STILAR[nr], punkt))
        delar.append(forklaring(nr, namn, STILAR[nr]))
    return (
        f'<svg class="graf" viewBox="0 0 {BREDD} {HOJD}" role="img" '
        f'aria-label="Antal per år; talen står i tabellen under." '
        f'font-size="12" fill="currentColor">{"".join(delar)}</svg>'
    )


def punktare(antal: int, topp: int):
    bredd = (BREDD - VANSTER - HOGER) / max(antal - 1, 1)
    hojd = HOJD - TOPP - BOTTEN

    def punkt(i: int, varde: float) -> tuple[float, float]:
        return VANSTER + i * bredd, TOPP + hojd * (1 - varde / topp)

    return punkt


def axlar(ar: list[int], topp: int, steg: int, punkt) -> str:
    delar = []
    for v in range(0, topp + 1, steg):
        x, y = punkt(0, v)
        delar.append(
            f'<line x1="{x}" x2="{BREDD - HOGER}" y1="{y}" y2="{y}" '
            f'stroke="#ccc"/><text x="{x - 6}" y="{y + 4}" '
            f'text-anchor="end">{v}</text>'
        )
    for i, a in enumerate(ar):
        x, y = punkt(i, 0)
        delar.append(f'<text x="{x}" y="{y + 18}" text-anchor="middle">{a}</text>')
    return "".join(delar)


def linje(varden: list[int | None], stil: tuple[str, str], punkt) -> str:
    streck, fyllning = stil
    delar = []
    med = [(i, v) for i, v in enumerate(varden) if v is not None]
    # Följande år har samma skillnad mellan år och plats i listan.
    for _, bit in groupby(enumerate(med), key=lambda e: e[1][0] - e[0]):
        xy = " ".join("{},{}".format(*punkt(i, v)) for _, (i, v) in bit)
        delar.append(
            f'<polyline points="{xy}" fill="none" stroke="currentColor" '
            f'stroke-width="2" {streck}/>'
        )
    delar += [
        f'<circle cx="{x}" cy="{y}" r="4" fill="{fyllning}" stroke="currentColor"/>'
        for x, y in (punkt(i, v) for i, v in med)
    ]
    return "".join(delar)


def forklaring(nr: int, namn: str, stil: tuple[str, str]) -> str:
    streck, fyllning = stil
    x = VANSTER + nr * 140
    return (
        f'<line x1="{x}" x2="{x + 30}" y1="14" y2="14" stroke="currentColor" '
        f'stroke-width="2" {streck}/><circle cx="{x + 15}" cy="14" r="4" '
        f'fill="{fyllning}" stroke="currentColor"/>'
        f'<text x="{x + 38}" y="18">{escape(namn)}</text>'
    )
