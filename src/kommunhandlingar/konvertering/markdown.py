"""Krav: K4 i docs/02-KRAV.md, ADR-0021. Test: tests/test_markdown.py.

Text ur PDF:en escapas så att den visas som den står när den läses som
Markdown: CommonMark med GFM:s tabeller och genomstrykning, och GitHubs
formler med `$`. Bara det som annars ändrar betydelse escapas, så att
råfilen går att läsa som den är.
"""

import re

# Var som helst i raden: \ före skiljetecken och i radslutet, kod, betoning,
# genomstrykning och formler, HTML och autolänkar, entiteter, länkar och
# `_` som inte står inne i ett ord.
I_RADEN = re.compile(
    r"\\(?=[!-/:-@\[-`{-~]|$)"
    r"|[`*~$]"
    r"|<(?=[A-Za-z/!?])"
    r"|&(?=#?[0-9A-Za-z]+;)"
    r"|\](?=\()"
    r"|(?<![^\W_])_|_(?![^\W_])",
    re.MULTILINE,
)
# Radens början: listor, rubriker, citat och länkdefinitioner.
LISTA_MED_TAL = re.compile(r"^(\d+)([.)])(?= |$)")
FORSTA_TECKEN = re.compile(r"^(?:[-+](?= |$)|#|>|\[(?=[^\]]*\]:))")
# En rad av bara streck kan bli rubrikstreck, linje eller tabellavgränsare;
# ett \ först räcker för att den ska bli text.
STRECK = re.compile(r"[-=_*|: ]+")


def rad(text: str) -> str:
    rad_ = text.strip()
    if STRECK.fullmatch(rad_):
        return "\\" + rad_
    escapad = LISTA_MED_TAL.sub(r"\1\\\2", i_raden(rad_))
    return FORSTA_TECKEN.sub(lambda m: "\\" + m.group(), escapad)


def cell(text: str) -> str:
    return i_raden(text).replace("|", "\\|").replace("\n", "<br>")


def i_raden(text: str) -> str:
    return I_RADEN.sub(lambda m: "\\" + m.group(), text)


def kodstaket(block: str) -> str:
    langsta = max((len(m) for m in re.findall(r"`+", block)), default=0)
    return "`" * max(3, langsta + 1)
