"""Kontrollerar rader per funktion och fil enligt "Ren kod – strikt" i AGENTS.md.

Test: tests/test_kontrollera_storlek.py. Ett undantag skrivs som en kommentar
`# undantag: <skäl>` på def-raden, eller på första raden för en hel fil.
"""

import ast
import sys
from pathlib import Path

MAX_RADER_FUNKTION = 30
MAX_RADER_FIL = 250
UNDANTAG = "# undantag:"
KATALOGER = ("src", "scripts", "tests")


def brott_i_fil(fil: Path) -> list[str]:
    rader = fil.read_text(encoding="utf-8").splitlines()
    fynd = []
    if len(rader) > MAX_RADER_FIL and UNDANTAG not in rader[0]:
        fynd.append(f"{fil}: {len(rader)} rader, gränsen är {MAX_RADER_FIL}")
    for nod in ast.walk(ast.parse("\n".join(rader))):
        if not isinstance(nod, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        langd = nod.end_lineno - nod.lineno + 1
        if langd > MAX_RADER_FUNKTION and UNDANTAG not in rader[nod.lineno - 1]:
            fynd.append(
                f"{fil}:{nod.lineno}: {nod.name} har {langd} rader, "
                f"gränsen är {MAX_RADER_FUNKTION}"
            )
    return fynd


def brott(filer: list[Path]) -> list[str]:
    return [fynd for fil in filer for fynd in brott_i_fil(fil)]


def pythonfiler() -> list[Path]:
    return [fil for katalog in KATALOGER for fil in Path(katalog).rglob("*.py")]


if __name__ == "__main__":
    fynd = brott(pythonfiler())
    print("\n".join(fynd) or "Inga brott mot storleksgränserna.")
    sys.exit(1 if fynd else 0)
