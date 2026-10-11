"""Krav: K20, ADR-0025. Kod: src/kommunhandlingar/facit/.

Reglerna prövas på påhittade sidor och tabeller där facit går att räkna för
hand. Urvalet i tests/fixtures/facit prövas för sig: att facit hänger ihop,
att utdragen inte bär personuppgifter, och att måtten för poolens version
står i matt.csv.
"""

import tempfile
import unittest
from collections import Counter
from importlib.metadata import version
from pathlib import Path

import pdfplumber

from kommunhandlingar.facit.jamfor import MATT, jamfor
from kommunhandlingar.facit.lasa import Facit, Tabell, urvalet
from kommunhandlingar.facit.matt import URVALET, spara, sparade, totalt, urvalets_utfall
from kommunhandlingar.facit.rader import lika, siffror, talrad
from kommunhandlingar.konvertering.dokument import Resultat
from kommunhandlingar.konvertering.las_sida import Sida
from kommunhandlingar.personuppgifter import maska

RUBRIK = ["Belopp", "2025", "2026"]
RADER = [RUBRIK, ["Intäkter", "1 184", "-41,4"], ["Kostnader", "-5 802", "-"]]
TEXT = "Resultaträkning 2025 och 2026\nSida 4"
SIDANS_TAL = ["2025", "2026", "4"] + [c for r in RADER for c in r[1:]]


def facit(tal=None, skannade=(), tabeller=None) -> Facit:
    tabeller = [Tabell("1-1", 1, 1, 1, RADER)] if tabeller is None else tabeller
    return Facit(
        "prov", Path(), {1: SIDANS_TAL} | (tal or {}), list(skannade), tabeller
    )


def matt(*sidor: Sida, **facit_) -> Counter:
    sidor = list(sidor) or [ok(TEXT, RADER)]
    return jamfor(facit(**facit_), Resultat("full", sidor=sidor)).matt


def ok(text: str, *tabeller: list[list[str]]) -> Sida:
    return Sida("ok", False, text, list(tabeller))


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


class Tabellerna(unittest.TestCase):
    def test_en_ratt_tabell_och_ratt_text(self):
        utfall = matt()
        self.assertEqual(utfall["ratt"], 1)
        self.assertEqual(sum(utfall[m] for m in MATT if m != "ratt"), 0)

    def test_en_rad_med_fel_tal(self):
        fel = [RUBRIK, RADER[1], ["Kostnader", "-5 802", "5"]]
        utfall = matt(ok(TEXT, fel))
        self.assertEqual((utfall["fel_rader"], utfall["ofullstandiga"]), (1, 1))

    def test_en_forsta_datarad_med_fel_tal_ar_fel(self):
        fel = [RUBRIK, ["Intäkter", "1 184", "41,4"], RADER[2]]
        utfall = matt(ok(TEXT, fel))
        self.assertEqual((utfall["fel_rader"], utfall["ofullstandiga"]), (1, 1))

    def test_en_rad_som_kommer_tva_ganger_ar_fel(self):
        dubbel = [*RADER, RADER[2]]
        utfall = matt(ok(TEXT, dubbel))
        self.assertEqual((utfall["fel_rader"], utfall["ratt"]), (1, 1))

    def test_en_tabell_utan_rubrik_ar_ofullstandig(self):
        utfall = matt(ok(TEXT, RADER[1:]))
        self.assertEqual((utfall["ofullstandiga"], utfall["fel_rader"]), (1, 0))

    def test_en_tabell_delad_pa_tva_csv_ar_ofullstandig(self):
        utfall = matt(ok(TEXT, RADER[:2], RADER[2:]))
        self.assertEqual((utfall["ofullstandiga"], utfall["fel_rader"]), (1, 0))

    def test_tva_tabeller_i_samma_csv_ar_ofullstandiga(self):
        andra = [["Not", "Text"], ["Avgifter", "77"]]
        tabeller = [Tabell("1-1", 1, 1, 1, RADER), Tabell("1-2", 1, 1, 1, andra)]
        utfall = matt(
            ok(TEXT, [*RADER, andra[1]]),
            tal={1: [*SIDANS_TAL, "77"]},
            tabeller=tabeller,
        )
        self.assertEqual((utfall["ofullstandiga"], utfall["fel_rader"]), (2, 0))

    def test_en_rubrik_delad_pa_tva_rader_stammer(self):
        delad = [["Belopp", "År", "År"], ["", "2025", "2026"], *RADER[1:]]
        self.assertEqual(matt(ok(TEXT, delad))["ratt"], 1)

    def test_en_tabell_som_saknas_ar_saknad_eller_osaker(self):
        text = TEXT + "\nIntäkter 1 184 -41,4\nKostnader -5 802 -"
        self.assertEqual(matt(ok(text))["saknade"], 1)
        self.assertEqual(matt(Sida("tabell-osaker", False, text, []))["osakra"], 1)

    def test_en_tabell_pa_en_obekraftad_sida_ar_osaker(self):
        utfall = matt(Sida("ocr", True, "Intäkter 1 1 84", []), skannade=[1])
        self.assertEqual((utfall["osakra"], utfall["omarkta"]), (1, 0))

    def test_en_tabell_dar_facit_inte_har_nagon(self):
        sidor = [ok("", RADER), ok("", [["Not", "Text"]])]
        utfall = matt(*sidor, tal={1: [], 2: []}, tabeller=[])
        self.assertEqual((utfall["pahittade"], utfall["fel_rader"]), (1, 0))


class Talen(unittest.TestCase):
    def test_ett_tal_som_delats_i_texten(self):
        text = TEXT.replace("Sida 4", "Sida 4 1 1 84")
        utfall = matt(ok(text, RADER), tal={1: [*SIDANS_TAL, "1 184"]})
        self.assertEqual(utfall["tal_avviker"], 3)

    def test_talen_pa_en_obekraftad_sida_jamfors_inte(self):
        utfall = matt(Sida("ocr", True, "Intäkter 1 1 84", []), skannade=[1])
        self.assertEqual(utfall["tal_avviker"], 0)

    def test_en_skannad_sida_som_inte_markts(self):
        self.assertEqual(matt(ok(""), skannade=[1])["omarkta"], 1)


class MattFilen(unittest.TestCase):
    def test_en_rad_per_version(self):
        with tempfile.TemporaryDirectory() as katalog:
            fil = Path(katalog) / "matt.csv"
            fil.write_text("version," + ",".join(MATT) + "\n", encoding="utf-8")
            spara(fil, "0.1.0", Counter(ratt=1))
            spara(fil, "0.2.0", Counter(ratt=2))
            spara(fil, "0.1.0", Counter(ratt=3))
            rader = sparade(fil)
        self.assertEqual(list(rader), ["0.1.0", "0.2.0"])
        self.assertEqual(
            (rader["0.1.0"]["ratt"], rader["0.1.0"]["saknade"]), ("3", "0")
        )


def tabellerna():
    for f in urvalet(URVALET):
        for t in f.tabeller:
            sidor = range(t.sida, t.sista_sida + 1)
            yield f.namn, t, Counter(siffror([f.tal.get(s, []) for s in sidor]))


def sidtexterna():
    for f in urvalet(URVALET):
        with pdfplumber.open(f.pdf) as pdf:
            for nr, sida in enumerate(pdf.pages, 1):
                yield f.namn, nr, sida.extract_text()


class Urvalet(unittest.TestCase):
    def test_tabellernas_tal_star_bland_sidans_tal(self):
        for namn, t, sidans in tabellerna():
            with self.subTest(namn, tabell=t.namn):
                self.assertEqual({len(r) for r in t.rader}, {len(t.rader[0])})
                self.assertEqual(Counter(siffror(t.rader)) - sidans, Counter())

    def test_utdragens_textlager_bar_inga_personuppgifter(self):
        for namn, nr, text in sidtexterna():
            with self.subTest(namn, sida=nr):
                self.assertEqual(maska(text), text)

    def test_matten_for_poolens_version_star_i_matt_csv(self):
        sparat = sparade(URVALET / "matt.csv")[version("kommunhandlingar")]
        utfall = totalt(urvalets_utfall(URVALET))
        self.assertEqual({m: int(sparat[m]) for m in MATT}, dict(utfall))


if __name__ == "__main__":
    unittest.main()
