"""Krav: K4, K5, K8 och K19, ADR-0004, ADR-0009 och ADR-0024.
Test: tests/test_hamta.py och tests/test_skarvar.py.

Dokumentets `.md` och tabellkatalog. Tabellerna skrivs först och ersätter
katalogen som helhet; `.md` skrivs sist, via en temporär fil i samma
katalog som byter namn, så att en avbruten körning aldrig lämnar en
halvskriven `.md`.
"""

import shutil
from pathlib import Path

from kommunhandlingar.konvertering import flersidiga
from kommunhandlingar.konvertering.las_sida import Sida
from kommunhandlingar.konvertering.tabeller import som_csv, som_markdown


def tabellkatalog(md: Path) -> Path:
    return md.with_suffix(".tabeller")


def tabellfiler(sidor: list[Sida]) -> dict[str, str]:
    return {f"{t.namn}.csv": som_csv(t.rader) for t in flersidiga.tabeller(sidor)}


def brodtext(sidor: list[Sida], katalog: str) -> str:
    tabeller = flersidiga.tabeller(sidor)
    delar = []
    for nr, sida in enumerate(sidor, 1):
        delar.append(f"<!-- sida {nr} -->")
        delar += [sida.text] if sida.text else []
        for t in [t for t in tabeller if t.sida == nr]:
            lank = f"[Tabell {t.namn}]({katalog}/{t.namn}.csv)"
            delar.append(f"{lank}\n\n{som_markdown(t.rader)}")
    return "\n\n".join(delar) + "\n"


def skriv(md: Path, text: str, tabeller: dict[str, str]) -> None:
    md.parent.mkdir(parents=True, exist_ok=True)
    katalog = tabellkatalog(md)
    ny = katalog.with_name(katalog.name + ".ny")
    ta_bort(ny)
    if tabeller:
        ny.mkdir()
        for namn, innehall in tabeller.items():
            (ny / namn).write_text(innehall, encoding="utf-8")
    ta_bort(katalog)
    if tabeller:
        ny.rename(katalog)
    skriv_md(md, text)


def skriv_md(md: Path, text: str) -> None:
    tillfallig = md.with_name(md.name + ".tmp")
    tillfallig.write_text(text, encoding="utf-8")
    tillfallig.replace(md)


def ta_bort(katalog: Path) -> None:
    if katalog.exists():
        shutil.rmtree(katalog)
