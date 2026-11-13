"""Krav: K2, K8, K9 och K45, ADR-0003 och ADR-0068.
Kod: src/kommunhandlingar/plats.py."""

import unittest
from dataclasses import replace
from datetime import date

from kommunhandlingar.kandidat import Kandidat
from kommunhandlingar.plats import Plats, grundplats, ledigt_namn, namn_av


class TestPlats(unittest.TestCase):
    def test_sokvagen(self):
        plats = Plats("ks", date(2019, 5, 28), "handlingar", "arende-4")
        self.assertEqual(
            str(plats.sokvag("kungsbacka")),
            "kungsbacka/ks/2019/2019-05-28/handlingar-arende-4.md",
        )

    def test_namnet(self):
        self.assertEqual(
            namn_av("Nämnden för Vård & Omsorg protokoll §§ 74, 76-91"),
            "namnden-for-vard-omsorg-protokoll-74-76-91",
        )
        self.assertEqual(namn_av("Café Ølstue – ÅÄÖ"), "cafe-lstue-aao")
        self.assertEqual(namn_av("§§"), "")

    def test_langt_namn_kortas_vid_bindestreck(self):
        namn = namn_av("ord " * 30)
        self.assertLessEqual(len(namn), 80)
        self.assertFalse(namn.endswith("-"))
        self.assertTrue(namn.endswith("ord"))

    def test_upptaget_eller_tomt_namn_blir_lopnummer(self):
        upptagna = {"kallelse", "2"}
        self.assertEqual(ledigt_namn("ny", upptagna.__contains__), "ny")
        self.assertEqual(ledigt_namn("kallelse", upptagna.__contains__), "3")
        self.assertEqual(ledigt_namn("", upptagna.__contains__), "3")

    def test_upptaget_adapternamn_far_lopnummer_efter_namnet(self):
        upptagna = {"projekt-plankarta", "projekt-plankarta-2"}.__contains__
        self.assertEqual(
            ledigt_namn("projekt-plankarta", upptagna, "projekt-plankarta"),
            "projekt-plankarta-3",
        )

    def test_adapterns_namn_ger_alltid_ett_namn(self):
        kandidat = Kandidat(
            "bun-projekt",
            date(2026, 5, 22),
            "handlingar",
            "https://x/a.pdf",
            "https://x",
            "sitevision:18.a",
            "a.pdf",
            namn="projektet-a",
        )
        self.assertEqual(grundplats(kandidat).namn, "projektet-a")
        self.assertIsNone(grundplats(replace(kandidat, namn="")).namn)
