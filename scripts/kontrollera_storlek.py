"""Krav: "Ren kod – strikt" i AGENTS.md. Test: tests/test_kontrollera_storlek.py."""

import ast
import re
import sys
from pathlib import Path

MAX_RADER_FUNKTION = 30
MAX_RADER_FIL = 250
UNDANTAG = re.compile(r"#\s*undantag:\s*\S")
ROT = Path(__file__).resolve().parent.parent
KATALOGER = ("src", "scripts", "tests")


def brott_i_fil(fil: Path) -> list[str]:
    text = fil.read_text(encoding="utf-8")
    rader = text.split("\n")
    fynd = []
    if text.count("\n") > MAX_RADER_FIL and not UNDANTAG.search(rader[0]):
        fynd.append(f"{fil}: över {MAX_RADER_FIL} rader")
    for nod in ast.walk(ast.parse(text)):
        if not isinstance(nod, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        langd = nod.end_lineno - nod.lineno + 1
        if langd > MAX_RADER_FUNKTION and not UNDANTAG.search(rader[nod.lineno - 1]):
            fynd.append(f"{fil}:{nod.lineno}: {nod.name} har {langd} rader")
    return fynd


def pythonfiler() -> list[Path]:
    return [fil for katalog in KATALOGER for fil in (ROT / katalog).rglob("*.py")]


if __name__ == "__main__":
    fynd = [rad for fil in pythonfiler() for rad in brott_i_fil(fil)]
    print("\n".join(fynd) or "Inga brott mot storleksgränserna.")
    sys.exit(1 if fynd else 0)
