"""Krav: K61 och ADR-0087. Kod: src/kommunhandlingar/konvertering/rutkanter.py.

Kanten där två fyllda rutor möts kant i kant är en cellgräns
(docs/03-ARKITEKTUR.md#konvertering-och-kvalitet). Sidorna i rutor.pdf
beskrivs i tests/fixtures/pdf/skapa_rutor.py.
"""

import unittest
from pathlib import Path

from kommunhandlingar.konvertering.dokument import konvertera
from kommunhandlingar.konvertering.rutkanter import gemensamma

PDF = Path(__file__).parent / "fixtures" / "pdf" / "rutor.pdf"


def ruta(x0: float, top: float, x1: float, bottom: float) -> dict:
    return {"x0": x0, "top": top, "x1": x1, "bottom": bottom}


def lage(kant: dict) -> tuple:
    return tuple(round(kant[k], 1) for k in ("x0", "top", "x1", "bottom"))


class TestGemensamma(unittest.TestCase):
    def test_rutor_bredvid_varandra_ger_en_lodrat_kant(self):
        kanter = gemensamma([ruta(0, 0, 100, 50), ruta(100.5, 10, 200, 60)])
        self.assertEqual([lage(k) for k in kanter], [(100.2, 10, 100.2, 50)])

    def test_rutor_ovanpa_varandra_ger_en_vagrat_kant(self):
        kanter = gemensamma([ruta(0, 0, 100, 50), ruta(20, 50, 200, 90)])
        self.assertEqual([lage(k) for k in kanter], [(20, 50, 100, 50)])

    def test_rutor_med_mellanrum_ger_ingen_kant(self):
        self.assertEqual(gemensamma([ruta(0, 0, 100, 50), ruta(102, 0, 200, 50)]), [])

    def test_rutor_som_bara_nuddar_i_ett_horn_ger_ingen_kant(self):
        self.assertEqual(gemensamma([ruta(0, 0, 100, 50), ruta(100, 49, 200, 90)]), [])

    def test_en_ensam_ruta_ger_ingen_kant(self):
        self.assertEqual(gemensamma([ruta(0, 0, 100, 50)]), [])


class TestRutorPdf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sidor = konvertera(PDF).sidor

    def test_kolumner_utan_streck_halls_isar(self):
        self.assertEqual(
            self.sidor[0].tabeller,
            [
                [
                    ["Mål", "Uppdrag", "Kommentar"],
                    ["Digital vardag", "Stärka digital", "Uppfylls"],
                    ["Hållbarhet", "Minska plast", "Uppfylls inte"],
                ]
            ],
        )

    def test_en_fargad_rad_ger_ingen_ny_cellgrans(self):
        (tabell,) = self.sidor[1].tabeller
        self.assertEqual([len(rad) for rad in tabell], [3, 3, 3])

    def test_rutor_som_inte_mots_blir_ingen_tabell(self):
        self.assertEqual(self.sidor[2].tabeller, [])


if __name__ == "__main__":
    unittest.main()
