"""Krav: K17, ADR-0022. Kod: src/kommunhandlingar/konvertering/personuppgifter.py
och src/kommunhandlingar/maska_poolen.py.

Alla nummer och adresser här är påhittade. Personnumren har giltig
kontrollsiffra, så att de känns igen.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from kommunhandlingar.konvertering import las_sida
from kommunhandlingar.konvertering.personuppgifter import maska
from kommunhandlingar.maska_poolen import maska_poolen

PNR = "(personnummer borttaget)"
MOBIL = "(mobilnummer borttaget)"
EPOST = "(e-post borttagen)"
ADRESS = "(adress borttagen)"


class Personnummer(unittest.TestCase):
    def test_formerna_med_bindestreck_plus_och_tolv_siffror(self):
        for nummer in (
            "121212-1212",
            "121212+1212",
            "19121212-1212",
            "191212121212",
            "20121212-1212",
        ):
            with self.subTest(nummer):
                self.assertEqual(
                    maska(f"Anna, {nummer} ledamot"), f"Anna, {PNR} ledamot"
                )

    def test_samordningsnummer(self):
        self.assertEqual(maska("(701063-2391)"), f"({PNR})")

    def test_fel_kontrollsiffra_star_kvar(self):
        self.assertEqual(maska("121212-1213"), "121212-1213")

    def test_tal_som_inte_ar_personnummer_star_kvar(self):
        for text in (
            "212000-1256",  # organisationsnummer: månaden är 20
            "556666-5468",
            "perioden 260101-261231",
            "1007799594 = 1081967344",  # tio siffror utan bindestreck
            "KS 2024-00123",
            "2024-10-14",
            "1 212 121 212",
        ):
            with self.subTest(text):
                self.assertEqual(maska(text), text)


class Mobilnummer(unittest.TestCase):
    def test_vanliga_skrivsatt(self):
        for nummer in (
            "070-123 45 67",
            "0701-23 45 67",
            "0701234567",
            "0705 094409",
            "+46701234567",
            "+46 70 123 45 67",
            "+4670-123 45 67",
        ):
            with self.subTest(nummer):
                self.assertEqual(maska(f"Tel: {nummer}."), f"Tel: {MOBIL}.")

    def test_fasta_nummer_star_kvar(self):
        for text in ("0300-83 40 00", "031-335 50 00", "020-81 91 00"):
            with self.subTest(text):
                self.assertEqual(maska(text), text)

    def test_talgrupper_i_en_tabell_star_kvar(self):
        rad = "3 668 072 271 3 591 291 691"
        self.assertEqual(maska(rad), rad)


class Epost(unittest.TestCase):
    def test_adressen_byts_och_texten_runt_star_kvar(self):
        self.assertEqual(
            maska("Kontakt: fornamn.efternamn@exempelby.se."),
            f"Kontakt: {EPOST}.",
        )

    def test_escapad_som_markdown(self):
        self.assertEqual(maska(r"\<anna\_b@exempel.se>"), rf"\<{EPOST}>")


class Gatuadress(unittest.TestCase):
    def test_med_postnummer_pa_samma_rad(self):
        self.assertEqual(
            maska("Exempelvägen 12 A, 123 45 Exempelby"),
            f"{ADRESS}, 123 45 Exempelby",
        )

    def test_med_lagenhet_och_postnummer_pa_raden_efter(self):
        self.assertEqual(
            maska("Storgatan 3, Lgh 1101\n\n123 45 EXEMPELBY"),
            f"{ADRESS}\n\n123 45 EXEMPELBY",
        )

    def test_gatunamn_i_tva_ord(self):
        self.assertEqual(maska("Fritz väg 33, 123 45 Ort"), f"{ADRESS}, 123 45 Ort")

    def test_i_en_tabellcell(self):
        self.assertEqual(
            maska("Exempelbacken 9<br>123 45 Ort"), f"{ADRESS}<br>123 45 Ort"
        )

    def test_utan_postnummer_star_kvar(self):
        for text in ("detaljplan för Storgatan 12", "Storgatan 12 och 13"):
            with self.subTest(text):
                self.assertEqual(maska(text), text)


class Upprepning(unittest.TestCase):
    def test_en_andra_maskning_andrar_ingenting(self):
        text = "121212-1212, 070-123 45 67, a@b.se, Storgatan 1, 123 45 Ort"
        self.assertEqual(maska(maska(text)), maska(text))


class Konverteringen(unittest.TestCase):
    def test_sidans_text_och_celler_maskas(self):
        last = las_sida.Sida(
            "ok", False, "Anna 121212-1212", [[["Tel", "070-123 45 67"]]]
        )
        with (
            mock.patch.object(las_sida, "vag", return_value="text"),
            mock.patch.object(las_sida, "textsida", return_value=last),
        ):
            sida = las_sida.las_sida(None, None)
        self.assertEqual(sida.text, f"Anna {PNR}")
        self.assertEqual(sida.tabeller, [[["Tel", MOBIL]]])


class Poolen(unittest.TestCase):
    def setUp(self):
        katalog = tempfile.TemporaryDirectory()
        self.addCleanup(katalog.cleanup)
        self.data = Path(katalog.name)
        self.md = self.data / "exempelby/ks/2025/2025-04-22/handlingar.md"
        self.md.parent.mkdir(parents=True)
        self.huvud = (
            "---\nkalla_url: https://exempelby.se/download/121212-1212.pdf\n---\n"
        )
        self.md.write_text(self.huvud + "Anna 121212-1212\n", encoding="utf-8")
        self.csv = self.md.with_suffix(".tabeller") / "1-1.csv"
        self.csv.parent.mkdir()
        self.csv.write_text(
            'Namn,Telefon\n"Anna, chef",070-123 45 67\n', encoding="utf-8"
        )

    def test_text_och_tabeller_maskas_men_inte_front_matter(self):
        self.assertEqual(maska_poolen(self.data), 2)
        self.assertEqual(self.md.read_text(), self.huvud + f"Anna {PNR}\n")
        self.assertEqual(self.csv.read_text(), f'Namn,Telefon\n"Anna, chef",{MOBIL}\n')

    def test_en_andra_korning_andrar_ingenting(self):
        maska_poolen(self.data)
        self.assertEqual(maska_poolen(self.data), 0)


if __name__ == "__main__":
    unittest.main()
