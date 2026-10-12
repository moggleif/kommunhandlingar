"""Krav: K5, ADR-0030. Kod: src/kommunhandlingar/konvertering/ombrutna.py.

En etikett som fortsätter på nästa rad
(docs/03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer).
"""

import unittest

from kommunhandlingar.konvertering.ombrutna import ombruten


def tabell(*etiketter: str) -> list[list[str]]:
    return [["", e, "1"] for e in etiketter]


class TestOmbruten(unittest.TestCase):
    def test_etikett_som_slutar_med_ett_bindeord(self):
        self.assertTrue(ombruten(tabell("Kostnader för", "verksamheten")))

    def test_avstavat_ord(self):
        self.assertTrue(ombruten(tabell("Kommun-", "område")))

    def test_oppen_parentes(self):
        self.assertTrue(ombruten(tabell("Studsvik (13§ 5", "och 13§ 6)")))

    def test_sista_raden_i_en_cell_provas(self):
        self.assertTrue(ombruten(tabell("Andel\nav kostnader för", "verksamheten")))

    def test_varav_efter_en_hel_etikett(self):
        self.assertFalse(ombruten(tabell("Intäkter", "varav bidrag")))

    def test_versal_efter_ett_bindeord(self):
        self.assertFalse(ombruten(tabell("Kostnader för", "Verksamheten")))

    def test_ord_som_slutar_pa_bindeordets_bokstaver(self):
        self.assertFalse(ombruten(tabell("Driftkostnader", "varav lokaler")))
        self.assertFalse(ombruten(tabell("Bidrag", "övrigt")))

    def test_bindestreck_efter_en_siffra(self):
        self.assertFalse(ombruten(tabell("90-", "summa")))


if __name__ == "__main__":
    unittest.main()
