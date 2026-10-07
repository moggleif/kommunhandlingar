"""Krav: K5 i docs/02-KRAV.md, ADR-0005. Test: tests/test_konvertering.py.

Sidans text ur textlagret med bevarad uppställning. Minst tre talrader i
följd, där bara tomma rader får stå emellan, blir ett kodblock märkt
`osaker-tabell` med uppställningen kvar. Övriga rader skrivs utan indrag
men med mellanrummen kvar, så att tal i följd inte flyter ihop.
"""

import re
import textwrap

FALTGRANS = re.compile(r" {2,}")
TAL = re.compile(r"[-−–]?(?:\d+|\d{1,3}(?:[  ]\d{3})+)(?:,\d+)?(?: ?%)?")
MINSTA_FOLJD = 3


def ar_talrad(rad: str) -> bool:
    falt = FALTGRANS.split(rad.strip())
    return sum(1 for f in falt if TAL.fullmatch(f)) >= 2


def stycken(text: str) -> tuple[str, bool]:
    rader = [rad.rstrip() for rad in text.splitlines()]
    delar: list[str] = []
    osaker, i = False, 0
    while i < len(rader):
        slut = foljd(rader, i)
        if sum(1 for rad in rader[i:slut] if rad) >= MINSTA_FOLJD:
            block = textwrap.dedent("\n".join(rader[i:slut]))
            delar += ["", f"```osaker-tabell\n{block}\n```", ""]
            osaker, i = True, slut
        else:
            delar.append(rader[i].strip())
            i += 1
    return komprimera(delar), osaker


def foljd(rader: list[str], borjan: int) -> int:
    slut = borjan
    if not ar_talrad(rader[borjan]):
        return slut
    for j in range(borjan, len(rader)):
        if rader[j] and not ar_talrad(rader[j]):
            break
        if rader[j]:
            slut = j + 1
    return slut


def komprimera(delar: list[str]) -> str:
    text = "\n".join(delar)
    return re.sub(r"\n{3,}", "\n\n", text).strip("\n")
