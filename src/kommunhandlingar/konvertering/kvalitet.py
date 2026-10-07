"""Krav: K6 i docs/02-KRAV.md, ADR-0005. Test: tests/test_konvertering.py.

Dokumentets kvalitet följer av sidornas; den första regeln som stämmer
gäller (docs/03-ARKITEKTUR.md#konvertering-och-kvalitet).
"""

LASTA = {"ok", "tabell-osaker", "ocr"}


def dokumentets(per_sida: list[str]) -> str:
    if not LASTA & set(per_sida):
        return "ej-konverterad"
    for sida, dokument in (
        ("ej-konverterad", "delvis"),
        ("ocr", "ocr"),
        ("tabell-osaker", "text-utan-tabeller"),
    ):
        if sida in per_sida:
            return dokument
    return "full"
