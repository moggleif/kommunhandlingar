"""Krav: ADR-0002, "Confirmation": varje fil som AGENTS.md pekar ut finns."""

import re
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
HANVISNING = re.compile(r"`([^`]+)`|\]\(([^)#]+)")


def utpekade_sokvagar(text: str) -> set[str]:
    trafar = (kod or lank for kod, lank in HANVISNING.findall(text))
    return {
        sokvag
        for sokvag in trafar
        if "<" not in sokvag
        and "://" not in sokvag
        and ("/" in sokvag or Path(sokvag).suffix in {".md", ".toml"})
    }


class TestAgentfil(unittest.TestCase):
    def test_utpekade_filer_finns(self):
        text = (ROT / "AGENTS.md").read_text(encoding="utf-8")
        saknas = [s for s in utpekade_sokvagar(text) if not (ROT / s).exists()]
        self.assertEqual(saknas, [])

    def test_mallar_ord_och_webbadresser_raknas_inte(self):
        text = "`kommuner/<kommun>.toml` `.md` `main` [w](https://a.se/b)"
        text += " [x](docs/a.md#rubrik)"
        self.assertEqual(utpekade_sokvagar(text), {"docs/a.md"})


if __name__ == "__main__":
    unittest.main()
