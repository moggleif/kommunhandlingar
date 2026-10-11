"""Krav: K20, ADR-0025. Kod: src/kommunhandlingar/facit/.

Reglerna prövas på påhittade sidor och tabeller där facit går att räkna för
hand. Urvalet i tests/fixtures/facit prövas för sig: att facit hänger ihop,
att utdragen inte bär personuppgifter, och att måtten för poolens version
står i matt.csv.
"""

import re
import unittest
from importlib.metadata import version
from pathlib import Path

import pdfplumber

from kommunhandlingar.facit.__main__ import sparade, totalt, urvalets_utfall
from kommunhandlingar.facit.jamfor import MATT, SIFFROR, jamfor, lika, talrad
from kommunhandlingar.facit.lasa import Facit, Tabell, urvalet
from kommunhandlingar.konvertering.dokument import Resultat
from kommunhandlingar.konvertering.las_sida import Sida
from kommunhandlingar.personuppgifter import maska

KATALOG = Path(__file__).parent / "fixtures" / "facit"
RUBRIK = ["Belopp", "2025", "2026"]
RADER = [RUBRIK, ["Intäkter", "1 184", "-41,4"], ["Kostnader", "-5 802", "-"]]
TEXT = "Resultaträkning 2025 och 2026\nSida 4"


def facit(tal=None, skannade=()) -> Facit:
    tal = {1: ["2025", "2026", "4"] + [c for r in RADER for c in r[1:]]} | (tal or {})
    return Facit("prov", Path(), tal, list(skannade), [Tabell("1-1", 1, 1, 1, RADER)])


def resultat(*sidor: Sida, obekraftade: bool = False) -> Resultat:
    return Resultat(
        "full", sidor=list(sidor) or [Sida("ok", obekraftade, TEXT, [RADER])]
    )


class Rader(unittest.TestCase):
    def test_talen_ska_sta_i_samma_kolumn(self):
        self.assertTrue(lika(["Intäkter", "1 184", "-41,4"], RADER[1]))
        self.assertFalse(lika(["Intäkter", "-41,4", "1 184"], RADER[1]))
        self.assertFalse(lika(["Intäkter", "1 184", ""], RADER[1]))
        self.assertFalse(lika(["Intäkter", "1 184", "-41,4", ""], RADER[1]))

    def test_ett_tappat_tecken_ar_fel_men_inte_ett_mellanrum(self):
        self.assertFalse(lika(["Intäkter", "1 184", "41,4"], RADER[1]))
        self.assertTrue(lika(["Intäkter", "1  184", "- 41,4"], RADER[1]))

    def test_etiketten_far_vara_avkortad_men_inte_borta(self):
        lang = ["Summa nämnder och styrelser", "7"]
        self.assertTrue(lika(["Summa nämnder", "7"], lang))
        self.assertTrue(lika(["och styrelser", "7"], lang))
        self.assertFalse(lika(["nämnder", "7"], lang))
        self.assertFalse(lika(["", "7"], lang))
        self.assertTrue(lika(["", "7"], ["", "7"]))

    def test_ett_streck_ar_ett_varde(self):
        self.assertTrue(talrad(["Kostnader", "", "-"]))
        self.assertFalse(talrad(["Not 3", "Summa"]))


class Matten(unittest.TestCase):
    def matt(self, *sidor: Sida, **facit_):
        return jamfor(facit(**facit_), resultat(*sidor)).matt

    def test_en_ratt_tabell_och_ratt_text(self):
        matt = self.matt()
        self.assertEqual(matt["ratt"], 1)
        self.assertEqual(sum(matt[m] for m in MATT if m != "ratt"), 0)

    def test_en_rad_med_fel_tal(self):
        fel = [RUBRIK, RADER[1], ["Kostnader", "-5 802", "5"]]
        matt = self.matt(Sida("ok", False, TEXT, [fel]))
        self.assertEqual((matt["fel_rader"], matt["ofullstandiga"]), (1, 1))

    def test_en_tabell_utan_rubrik_ar_ofullstandig(self):
        matt = self.matt(Sida("ok", False, TEXT, [RADER[1:]]))
        self.assertEqual((matt["ofullstandiga"], matt["fel_rader"]), (1, 0))

    def test_en_rubrik_delad_pa_tva_rader_stammer(self):
        delad = [["Belopp", "År", "År"], ["", "2025", "2026"], *RADER[1:]]
        self.assertEqual(self.matt(Sida("ok", False, TEXT, [delad]))["ratt"], 1)

    def test_en_tabell_som_saknas_ar_saknad_eller_osaker(self):
        text = TEXT + "\nIntäkter 1 184 -41,4\nKostnader -5 802 -"
        self.assertEqual(self.matt(Sida("ok", False, text))["saknade"], 1)
        self.assertEqual(self.matt(Sida("tabell-osaker", False, text))["osakra"], 1)

    def test_ett_tal_som_delats_i_texten(self):
        text = TEXT.replace("Sida 4", "Sida 4 1 1 84")
        matt = self.matt(
            Sida("ok", False, text, [RADER]),
            tal={1: ["2025", "2026", "4", "1 184"] + [c for r in RADER for c in r[1:]]},
        )
        self.assertEqual(matt["tal_avviker"], 3)

    def test_talen_pa_en_obekraftad_sida_jamfors_inte(self):
        matt = self.matt(Sida("ocr", True, "Intäkter 1 1 84"), skannade=[1])
        self.assertEqual((matt["tal_avviker"], matt["omarkta"]), (0, 0))
        self.assertEqual(matt["osakra"], 1)

    def test_en_skannad_sida_som_inte_markts(self):
        matt = self.matt(Sida("ok", False, ""), skannade=[1])
        self.assertEqual(matt["omarkta"], 1)

    def test_en_tabell_dar_facit_inte_har_nagon(self):
        annan = Facit("prov", Path(), {1: [], 2: []}, [], [])
        sidor = [Sida("ok", False, "", [RADER]), Sida("ok", False, "")]
        matt = jamfor(annan, Resultat("full", sidor=sidor)).matt
        self.assertEqual((matt["pahittade"], matt["fel_rader"]), (1, 0))


def tabellerna(katalog: Path):
    for f in urvalet(katalog):
        for t in f.tabeller:
            sidor = range(t.sida, t.sista_sida + 1)
            yield f, t, " ".join(x for s in sidor for x in f.tal.get(s, []))


def sidtexterna(katalog: Path):
    for f in urvalet(katalog):
        with pdfplumber.open(f.pdf) as pdf:
            yield from (
                (f.namn, nr, s.extract_text()) for nr, s in enumerate(pdf.pages, 1)
            )


class Urvalet(unittest.TestCase):
    def test_tabellernas_tal_star_bland_sidans_tal(self):
        for f, t, sidans in tabellerna(KATALOG):
            for rad in t.rader:
                siffror = [s for c in rad for s in SIFFROR.findall(c)]
                saknas = [
                    s for s in siffror if not re.search(rf"(?<!\d){s}(?!\d)", sidans)
                ]
                with self.subTest(f.namn, tabell=t.namn, rad=rad):
                    self.assertEqual(len(rad), len(t.rader[0]))
                    self.assertEqual(saknas, [])

    def test_utdragen_bar_inga_personuppgifter(self):
        for namn, nr, text in sidtexterna(KATALOG):
            with self.subTest(namn, sida=nr):
                self.assertEqual(maska(text), text)

    def test_matten_for_poolens_version_star_i_matt_csv(self):
        sparat = sparade(KATALOG / "matt.csv")[version("kommunhandlingar")]
        matt = totalt(urvalets_utfall(KATALOG))
        self.assertEqual({m: int(sparat[m]) for m in MATT}, dict(matt))


if __name__ == "__main__":
    unittest.main()
