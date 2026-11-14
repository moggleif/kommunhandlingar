"""Krav: K48 i docs/02-KRAV.md, ADR-0071. Test: tests/test_paragrafer.py.

Diarienumret skrivs som det står i protokollet. Bara tankstreck och
mellanslag kring bindestrecket eller mellan förled och år blir ett
bindestreck, så att `BN 2024-000123`, `BN 2016–000170` och `MH-2021- 3122`
skrivs `BN-2024-000123`, `BN-2016-000170` och `MH-2021-3122`.
"""

import re

NUMMER = r"(?:[A-ZÅÄÖ]{1,5}[ /–-]?)?\d[\dA-Z]*(?:(?: ?[–-] ?|/|:)[A-Z]?\d[\dA-Z]*)*"
MED_ETIKETT = re.compile(rf"\b(?i:Dnr|Diarienr|Diarienummer)\.?:?\s*({NUMMER})")
UTAN_ETIKETT = re.compile(r"[A-ZÅÄÖ]{1,5}[ /–-]?\d{2,4}[–/:-]\d+(?:/\d+)?")


def i_huvudet(text: str, ensam: bool = False) -> list[str]:
    """Numren efter `Dnr`; med `ensam` också ett nummer som står ensamt."""
    if ensam and UTAN_ETIKETT.fullmatch(text.strip()):
        return [normaliserat(text.strip())]
    return [normaliserat(n) for n in MED_ETIKETT.findall(text)]


def normaliserat(nummer: str) -> str:
    nummer = re.sub(r" ?[–-] ?", "-", nummer)
    return re.sub(r"^([A-ZÅÄÖ]+) (?=\d)", r"\1-", nummer)
