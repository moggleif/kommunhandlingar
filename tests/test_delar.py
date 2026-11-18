"""Krav: K11 i docs/02-KRAV.md, ADR-0088.
Kod: src/kommunhandlingar/tidsbudget.py och hamta.py."""

import unittest
from collections import Counter
from datetime import timedelta

from kommunhandlingar import hamta, tidsbudget
from tests.test_hamta import TID


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
