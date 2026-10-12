"""Krav: K5, ADR-0028 och ADR-0029. Kod: src/kommunhandlingar/konvertering/delade.py.

En tabell med linjer där en cell rymmer mer än ett tal delas efter de
lodräta linjer som finns i andra rader, efter talen i linje och efter
rutornas textrader
(docs/03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
Sidorna i delade.pdf beskrivs i tests/fixtures/pdf/skapa_delade.py.
"""

import unittest
from pathlib import Path

import pdfplumber

from kommunhandlingar.konvertering import delade, tabeller
from kommunhandlingar.konvertering.dokument import konvertera

PDF = Path(__file__).parent / "fixtures" / "pdf" / "delade.pdf"
INTAKTER = ["Intäkter", "4 078", "4 054"]
KOSTNADER = ["Kostnader", "-1 845", "-2 001"]


class TestDeladeSidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resultat = konvertera(PDF)

    def tabell(self, sida: int) -> list[list[str]]:
        (tabell,) = self.resultat.sidor[sida].tabeller
        return tabell

    def test_kvalitet_per_sida(self):
        self.assertEqual(
            self.resultat.kvalitet_per_sida,
            [
                "ok",  # rubrikraden utan lodräta linjer
                "ok",  # tre rader i varje ruta
                "ok",  # rubrik och värde i samma ruta
                "tabell-osaker",  # etiketten mitt emellan talen
                "ok",  # etiketten över linjen står i första kolumnen
                "tabell-osaker",  # ett tal i en cell över två kolumner
                "tabell-osaker",  # ett tal över en linje
                "ok",  # talen i linje utan lodrät linje emellan
                "ok",  # en rubrik över två kolumner
                "tabell-osaker",  # en etikett som bryts över två rader
            ],
        )

    def test_rubrikraden_delas_efter_linjerna_under(self):
        self.assertEqual(
            self.tabell(0), [["Belopp, tkr", "2026", "2027"], INTAKTER, KOSTNADER]
        )

    def test_raderna_i_rutan_blir_egna_rader(self):
        netto = ["Netto", "2 233", "2 053"]
        self.assertEqual(
            self.tabell(1), [["Post", "2026", "2027"], INTAKTER, KOSTNADER, netto]
        )

    def test_rubrik_och_varde_i_samma_ruta(self):
        self.assertEqual(
            self.tabell(2),
            [
                ["", "Bokslut\n2025", "Budget\n2026"],
                ["Nämnden", "-1,3", "-1,7"],
                ["Kostnader", "-48,6", "-53,8"],
            ],
        )

    def test_etikett_mitt_emellan_blir_ingen_tabell(self):
        sida = self.resultat.sidor[3]
        self.assertEqual(sida.tabeller, [])
        self.assertIn("4 078", sida.text)

    def test_etikett_over_linjen_star_i_forsta_kolumnen(self):
        with pdfplumber.open(PDF) as pdf:
            sida = pdf.pages[4]
            ord_ = sida.extract_words(return_chars=True)
            _, (fallen,) = tabeller.sakra(sida, ord_)
            rader, _ = delade.tabell(fallen, ord_)
        rubrik = ["Belopp i tusentals kronor, netto", "2026", "2027"]
        self.assertEqual(rader, [rubrik, INTAKTER, KOSTNADER])

    def test_talen_i_linje_blir_kolumner(self):
        self.assertEqual(
            self.tabell(7),
            [
                ["", "Namn", "Bokslut 2024", "Bokslut 2025"],
                ["", "Andel kvinnor\nsom har heltid", "94,3 %", "96,9 %"],
                ["", "Andel män som\nhar heltid", "98,6 %", "99,2 %"],
            ],
        )

    def test_rubrik_over_tva_kolumner_star_i_den_forsta(self):
        self.assertEqual(
            self.tabell(8),
            [
                ["", "Andel av volymen\nBokslut 2024", "Bokslut 2025"],
                ["Förskola", "22,6", "23,7"],
                ["Grundskola", "51,0", "50,2"],
            ],
        )

    def test_ord_over_en_linje_delas_inte(self):
        with pdfplumber.open(PDF) as pdf:
            sida = pdf.pages[6]
            ord_ = sida.extract_words(return_chars=True)
            _, (fallen,) = tabeller.sakra(sida, ord_)
            self.assertIsNone(delade.tabell(fallen, ord_))

    def test_tal_over_tva_kolumner_blir_ingen_tabell(self):
        sida = self.resultat.sidor[5]
        self.assertEqual(sida.tabeller, [])
        self.assertIn("8 132", sida.text)


if __name__ == "__main__":
    unittest.main()
