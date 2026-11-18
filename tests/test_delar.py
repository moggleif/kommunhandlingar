"""Krav: K11 i docs/02-KRAV.md, ADR-0088.
Kod: src/kommunhandlingar/tidsbudget.py, hamta.py och provade.py."""

import tempfile
import unittest
from collections import Counter
from datetime import timedelta
from pathlib import Path

from kommunhandlingar import hamta, provade, tidsbudget
from tests.test_hamta import TID, kandidat


class TestDelar(unittest.TestCase):
    def test_delens_grans_ar_minuterna_eller_budgeten(self):
        nu = TID + timedelta(hours=1)
        budget = TID + timedelta(hours=5)
        self.assertEqual(
            tidsbudget.delens_grans(TID, 15, nu), nu + timedelta(minutes=15)
        )
        sent = TID + timedelta(hours=4, minutes=50)
        self.assertEqual(tidsbudget.delens_grans(TID, 15, sent), budget)
        self.assertEqual(tidsbudget.delens_grans(TID, None, nu), budget)

    def test_kod_4_bara_nar_delen_slutar_fore_budgeten(self):
        delen = TID + timedelta(hours=1)
        budget = tidsbudget.mjuk_grans(TID)
        vantar, klart = Counter({hamta.VANTAR: 3}), Counter({"konverterad": 3})
        self.assertEqual(hamta.slutkod(vantar, TID, delen), hamta.MER_I_NASTA_DEL)
        self.assertEqual(hamta.slutkod(vantar, TID, budget), 0)
        self.assertEqual(hamta.slutkod(klart, TID, delen), 0)


class TestProvade(unittest.TestCase):
    def setUp(self):
        katalog = tempfile.TemporaryDirectory()
        self.addCleanup(katalog.cleanup)
        self.fil = provade.fil(Path(katalog.name) / "kb.kandidater.json")

    def test_en_provad_kandidat_tas_inte_om_i_nasta_del(self):
        a, b, c = (kandidat(f"s:{n}", f"u{n}") for n in (1, 2, 3))
        self.assertEqual(provade.kvar([a, b, c], self.fil), [a, b, c])
        provade.skriv(self.fil, [a])
        provade.skriv(self.fil, [b])
        self.assertEqual(provade.kvar([a, b, c], self.fil), [c])

    def test_utan_delar_provas_allt(self):
        a = kandidat("s:1", "u1")
        provade.skriv(None, [a])
        self.assertEqual(provade.kvar([a], None), [a])
        self.assertEqual(self.fil.name, "kb.kandidater.provade")
