"""Krav: K6, K72 och K73 i docs/02-KRAV.md, ADR-0005, ADR-0099 och ADR-0100.
Test: tests/test_konvertering.py.

Dokumentets kvalitet följer av sidornas; den första regeln som stämmer
gäller (docs/03-ARKITEKTUR.md#konvertering-och-kvalitet).
"""

# Dokumentets kvalitetsnivåer, från bäst till sämst.
KVALITETER = (
    "full",
    "text-utan-tabeller",
    "ocr",
    "delvis",
    "ej-konverterad",
    "ej-hamtad",
)
SIDKVALITETER = (
    "ok",
    "tabell-osaker",
    "ocr",
    "bild",
    "ointressant",
    "tom",
    "ej-konverterad",
)
LASTA = {"ok", "tabell-osaker", "ocr", "bild", "ointressant"}
UTAN_TEXT = ("ej-hamtad", "ej-konverterad")


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
