"""Krav: K6, issue #257. Kod: src/kommunhandlingar/konvertering/las_sida.py."""

import unittest
from unittest import mock

from kommunhandlingar.konvertering import las_sida


class Styrtecken(unittest.TestCase):
    def test_styrtecken_blir_ersattningstecken_i_text_och_celler(self):
        last = las_sida.Sida(
            "ok", True, "Åtgärder:\n\x00 Fönster\tmot spåret\x18", [[["a\x02b", "1"]]]
        )
        with (
            mock.patch.object(las_sida, "vag", return_value="text"),
            mock.patch.object(las_sida, "textsida", return_value=last),
        ):
            sida = las_sida.las_sida(None, None)
        self.assertEqual(sida.text, "Åtgärder:\n� Fönster\tmot spåret�")
        self.assertEqual(sida.tabeller, [[["a�b", "1"]]])
