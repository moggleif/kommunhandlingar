"""Krav: K5, ADR-0016. Kod: src/kommunhandlingar/konvertering/olinjerade.py.

Orden är påhittade med koordinater i punkter och teckenhöjd 10, så att
facit går att räkna för hand: mellanrum upp till 5 är samma fält, från 10
ett nytt, och däremellan tvetydigt.
"""

import unittest
from pathlib import Path
from types import SimpleNamespace

from kommunhandlingar.konvertering.dokument import konvertera
from kommunhandlingar.konvertering.falt import falt
from kommunhandlingar.konvertering.olinjerade import tabeller

PDF = Path(__file__).parent / "fixtures" / "pdf"

HOJD = 10


def ord_(text: str, x1: float, top: float, bredd: float = 20) -> dict:
    return {"text": text, "x0": x1 - bredd, "x1": x1, "top": top, "bottom": top + HOJD}


def rad(top: float, etikett: str | None, *tal: tuple[str, float]) -> list[dict]:
    ut = [ord_(etikett, 100, top, 40)] if etikett else []
    for text, x1 in tal:
        ut += tal_ord(text, x1, top)
    return ut


def tal_ord(text: str, x1: float, top: float) -> list[dict]:
    """Ett tal med tusentalsmellanrum blir två ord med 2 punkter emellan."""
    delar = text.split(" ")
    if len(delar) == 1:
        return [ord_(text, x1, top, 15)]
    return [ord_(delar[0], x1 - 17, top, 5), ord_(delar[1], x1, top, 15)]


def sida(*rader: list[dict]) -> SimpleNamespace:
    alla = [o for r in rader for o in r]
    return SimpleNamespace(extract_words=lambda **_: alla)


BUDGET = [
    rad(100, "Intäkter", ("4 078", 200), ("4 054", 300)),
    rad(120, "Kostnader", ("-1 845", 200), ("-2 001", 300)),
    rad(140, "Ombudget", ("500", 200)),
    rad(160, "Netto", ("2 233", 200), ("2 053", 300)),
]


class TestFalt(unittest.TestCase):
    def test_tusentalsmellanrum_ar_samma_falt(self):
        self.assertEqual([f.text for f in falt(tal_ord("4 078", 200, 0))], ["4 078"])

    def test_stort_mellanrum_ar_nytt_falt(self):
        rad_ = [ord_("4", 100, 0), ord_("078", 130, 0)]
        self.assertEqual([f.text for f in falt(rad_)], ["4", "078"])

    def test_mellanrum_mellan_halv_och_hel_teckenhojd_ar_tvetydigt(self):
        self.assertIsNone(falt([ord_("4", 100, 0), ord_("078", 127, 0)]))


class TestTabeller(unittest.TestCase):
    def test_talen_i_linje_blir_en_tabell_med_tom_cell(self):
        (tabell,) = tabeller(sida(*BUDGET), [])
        self.assertEqual(
            tabell.rader,
            [
                ["Intäkter", "4 078", "4 054"],
                ["Kostnader", "-1 845", "-2 001"],
                ["Ombudget", "500", ""],
                ["Netto", "2 233", "2 053"],
            ],
        )

    def test_rubrikrad_i_linje_tas_med(self):
        rubrik = [ord_("Budget", 180, 80, 20), ord_("2027", 200, 80, 18)]
        rubrik += [ord_("Plan", 280, 80, 20), ord_("2028", 300, 80, 18)]
        (tabell,) = tabeller(sida(rubrik, *BUDGET), [])
        self.assertEqual(tabell.rader[0], ["", "Budget 2027", "Plan 2028"])

    def test_rubrik_ur_linje_tas_inte_med_alls(self):
        rubrik = [ord_("Budget", 175, 80, 20), ord_("2027", 195, 80, 18)]
        (tabell,) = tabeller(sida(rubrik, *BUDGET), [])
        self.assertEqual(tabell.rader[0][0], "Intäkter")

    def test_rad_utan_etikett_ger_ingen_tabell(self):
        ar = rad(180, None, ("2012", 200), ("2013", 300))
        self.assertEqual(tabeller(sida(*BUDGET, ar), []), [])

    def test_ar_i_forsta_kolumnen_ger_ingen_tabell(self):
        ar = [
            rad(100 + 20 * i, "Löptext i spalten", (str(2021 + i), 200), ("62", 300))
            for i in range(3)
        ]
        self.assertEqual(tabeller(sida(*ar), []), [])

    def test_tal_ur_linje_ger_ingen_tabell(self):
        sned = rad(180, "Summa", ("1 000", 205), ("2 000", 300))
        self.assertEqual(tabeller(sida(*BUDGET, sned), []), [])

    def test_kolumn_med_ett_enda_tal_ger_ingen_tabell(self):
        extra = rad(180, "Summa", ("1 000", 200), ("2 000", 300), ("3", 400))
        self.assertEqual(tabeller(sida(*BUDGET, extra), []), [])

    def test_text_mellan_kolumnerna_ger_ingen_tabell(self):
        tva = rad(180, "Summa", ("1 000", 200), ("2 000", 300))
        tva.insert(3, ord_("Andra", 250, 180, 30))
        self.assertEqual(tabeller(sida(*BUDGET, tva), []), [])

    def test_ett_ord_till_inom_tabellens_yta_ger_ingen_tabell(self):
        hog = {"text": "X", "x0": 230, "x1": 240, "top": 60, "bottom": 170}
        self.assertEqual(tabeller(sida(*BUDGET, [hog]), []), [])

    def test_farre_an_tre_rader_med_tva_tal_ar_ingen_tabell(self):
        self.assertEqual(tabeller(sida(*BUDGET[:3]), []), [])

    def test_streck_ur_linje_ger_ingen_tabell(self):
        streck = rad(180, "Avgifter", ("1 000", 200), ("-", 290))
        self.assertEqual(tabeller(sida(*BUDGET, streck), []), [])

    def test_rad_med_tvetydigt_mellanrum_och_tal_ger_ingen_tabell(self):
        tvetydig = [ord_("Summa", 100, 180, 40), ord_("1", 180, 180, 5)]
        tvetydig += [ord_("2", 192, 180, 5), ord_("3", 300, 180, 5)]
        self.assertEqual(tabeller(sida(*BUDGET, tvetydig), []), [])

    def test_stort_radavstand_skiljer_tabellerna_at(self):
        langre_ned = [[dict(o, top=o["top"] + 120) for o in r] for r in BUDGET]
        langre_ned = [[dict(o, bottom=o["top"] + HOJD) for o in r] for r in langre_ned]
        self.assertEqual(len(tabeller(sida(*BUDGET, *langre_ned), [])), 2)

    def test_upptagen_yta_mellan_raderna_ger_ingen_tabell(self):
        linjerad = [ord_("Antal", 100, 175, 40), ord_("17", 200, 175, 10)]
        under = [
            [dict(o, top=o["top"] + 80, bottom=o["bottom"] + 80) for o in r]
            for r in BUDGET
        ]
        upptagna = [(55, 172, 305, 187)]
        self.assertEqual(tabeller(sida(*BUDGET, linjerad, *under), upptagna), [])


class TestRubriker(unittest.TestCase):
    BUDGET_PLAN = [ord_("Budget", 200, 80, 25), ord_("Plan", 300, 80, 25)]

    def rubriker(self, *ovanfor: list[dict]) -> list[list[str]]:
        (tabell,) = tabeller(sida(*ovanfor, *BUDGET), [])
        return tabell.rader[: len(tabell.rader) - len(BUDGET)]

    def test_etikett_i_rubriken(self):
        rubrik = [ord_("Belopp", 100, 80, 40), *self.BUDGET_PLAN]
        self.assertEqual(self.rubriker(rubrik), [["Belopp", "Budget", "Plan"]])

    def test_rubrik_med_tal_ovanfor_tas_inte_med(self):
        tal = rad(65, "Annat", ("1 000", 200), ("2 000", 300))
        self.assertEqual(self.rubriker(tal, self.BUDGET_PLAN), [])

    def test_rubrik_som_borjar_bland_etiketterna_tas_inte_med(self):
        rubrik = [ord_("Verksamhetens", 200, 80, 120), ord_("Plan", 300, 80, 25)]
        self.assertEqual(self.rubriker(rubrik), [])

    def test_rubrik_i_mellanrummet_tas_inte_med(self):
        rubrik = [ord_("Utfall", 130, 80, 25), *self.BUDGET_PLAN]
        self.assertEqual(self.rubriker(rubrik), [])

    def test_rubrik_utan_varje_kolumn_overst_tas_inte_med(self):
        rubrik = [ord_("Driftbudget", 100, 80, 40), ord_("tkr", 300, 80, 15)]
        self.assertEqual(self.rubriker(rubrik), [])

    def test_tvaradig_rubrik_under_en_ensam_etikett(self):
        rubrik = [ord_("Budget", 200, 65, 25), ord_("Plan", 300, 65, 25)]
        rubrik2 = [ord_("tkr", 200, 80, 15), ord_("tkr", 300, 80, 15)]
        titel = [ord_("Driftbudget", 100, 50, 40)]
        self.assertEqual(
            self.rubriker(titel, rubrik, rubrik2),
            [["", "Budget", "Plan"], ["", "tkr", "tkr"]],
        )

    def test_tva_ord_ovanfor_rubriken_gor_den_osaker(self):
        titel = [ord_("Drift", 60, 65, 20), ord_("Budget", 100, 65, 20)]
        self.assertEqual(self.rubriker(titel, self.BUDGET_PLAN), [])


class TestSidorna(unittest.TestCase):
    """Sidorna 3, 12, 14 och 15 i sidor.pdf; se tests/fixtures/pdf/skapa.py."""

    @classmethod
    def setUpClass(cls):
        cls.resultat = konvertera(PDF / "sidor.pdf")

    def test_olinjerad_tabell_med_talen_i_linje_blir_rader(self):
        sida = self.resultat.sidor[2]
        self.assertEqual(
            sida.tabeller,
            [
                [
                    ["Intäkter", "4 078", "4 054"],
                    ["Kostnader", "-1 845", "-2 001"],
                    ["Netto", "2 233", "2 053"],
                ]
            ],
        )
        self.assertEqual(sida.text, "")

    def test_olinjerad_tabell_far_rubrikrad_tom_cell_och_streck(self):
        sida = self.resultat.sidor[11]
        self.assertEqual(sida.text, "Driftbudget")
        self.assertEqual(
            sida.tabeller,
            [
                [
                    ["Belopp, tkr", "Budget 2027", "Plan 2028"],
                    ["Intäkter", "4 078", "4 054"],
                    ["Kostnader", "-1 845", "-2 001"],
                    ["Ombudget", "500", ""],
                    ["Avgifter", "-", "120"],
                    ["Netto", "2 233", "2 053"],
                ]
            ],
        )

    def test_linjerad_tabell_med_tva_tal_i_en_cell_ar_inte_saker(self):
        self.assertEqual(
            self.resultat.sidor[13].tabeller,
            [
                [
                    ["Post", "2026", "2027"],
                    ["Intäkter", "4 078", "4 054"],
                    ["Kostnader", "-1 845", "-2 001"],
                    ["Netto", "2 233", "2 053"],
                ]
            ],
        )

    def test_fotnotssiffra_vid_ett_tal_ger_ingen_tabell(self):
        self.assertEqual(self.resultat.sidor[14].tabeller, [])
