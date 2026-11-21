"""Krav: K73 i docs/02-KRAV.md, ADR-0100. Testar
src/kommunhandlingar/konvertering/sakra_rader.py med påhittade TSV:er från
Tesseract."""

import unittest
from unittest import mock

from PIL import Image

from kommunhandlingar.konvertering import ocr, sakra_rader

HUVUD = "\t".join(
    [
        "level",
        "page_num",
        "block_num",
        "par_num",
        "line_num",
        "word_num",
        "left",
        "top",
        "width",
        "height",
        "conf",
        "text",
    ]
)


def tsv(*rader: list[tuple[str, float]]) -> str:
    """En TSV med en rad per lista av (ord, säkerhet), i var sitt block."""
    ut = [HUVUD]
    for nr, ord_ in enumerate(rader, 1):
        for i, (text, conf) in enumerate(ord_, 1):
            ut.append(f"5\t1\t{nr}\t1\t1\t{i}\t0\t0\t10\t10\t{conf}\t{text}")
    return "\n".join(ut)


def mening(antal: int, conf: float = 95) -> list[tuple[str, float]]:
    return [("planen", conf)] * antal


class TestRader(unittest.TestCase):
    def test_saker_rad_behalls_och_osaker_faller(self):
        lasning = tsv([("Detaljplan", 92), ("Kolla", 88)], [("Mx", 20), ("§&r", 30)])
        self.assertEqual(sakra_rader.rader(lasning), ["Detaljplan Kolla"])

    def test_rad_utan_ord_med_tre_bokstaver_faller(self):
        self.assertEqual(sakra_rader.rader(tsv([("12", 96), ("4:5", 96)])), [])

    def test_rad_med_bara_punktutfyllnad_faller(self):
        self.assertEqual(sakra_rader.rader(tsv([("..........sss", 95)])), [])

    def test_punktutfyllnad_raknas_inte_in_i_sakerheten(self):
        rad = [("Inledning", 93), ("...........sss", 10), ("3", 90)]
        self.assertEqual(sakra_rader.rader(tsv(rad)), ["Inledning ...........sss 3"])


class TestLas(unittest.TestCase):
    def setUp(self):
        self.gra = Image.new("L", (100, 140), 255)

    def test_for_fa_ord_ger_ingen_text(self):
        with mock.patch.object(ocr, "las_bild", return_value=("", "")):
            self.assertIsNone(sakra_rader.las(self.gra, tsv(mening(29))))

    def test_minst_trettio_ord_ger_raderna(self):
        with mock.patch.object(ocr, "las_bild", return_value=("", "")):
            text = sakra_rader.las(self.gra, tsv(mening(15), mening(15), mening(9, 30)))
        self.assertEqual(text, "\n".join([" ".join(["planen"] * 15)] * 2))

    def test_vriden_lasning_med_flest_ord_galler(self):
        """Bestämmelser på högkant: den vridna läsningen ger fler säkra ord."""
        vriden = (tsv(mening(40)), "")
        with mock.patch.object(ocr, "las_bild", side_effect=[vriden, ("", "")]) as las:
            text = sakra_rader.las(self.gra, tsv(mening(5)))
        self.assertEqual((text.count("planen"), las.call_count), (40, 2))
        self.assertEqual(las.call_args_list[0].args[0].size, (140, 100))

    def test_tesseract_som_fallerar_i_en_vriden_lasning(self):
        with (
            mock.patch.object(ocr, "las_bild", return_value=None),
            self.assertRaises(sakra_rader.Fallerade),
        ):
            sakra_rader.las(self.gra, tsv(mening(40)))
