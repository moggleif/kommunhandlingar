"""Krav: K54 i docs/02-KRAV.md, ADR-0078.
Kod: src/kommunhandlingar/webbplats/kortkoppling.py."""

import unittest

from kommunhandlingar.webbplats.kortkoppling import (
    Kortlank,
    kortlankar,
    sidindex,
    tacker,
)
from kommunhandlingar.webbplats.spar import Steg
from kommunhandlingar.webbplats.sparslag import INITIATIV
from tests.test_webbplats import exempelby

FIL = "fsn/2024/2024-05-02/protokoll.md"


def paragraf(sida: int, *diarienummer: str) -> dict:
    return {
        "fil": f"data/exempelby/{FIL}",
        "sidnummer": sida,
        "diarienummer": list(diarienummer),
    }


INDEX = sidindex(
    [paragraf(2, "FSN-2024-1"), paragraf(4, "FSN-2024-2"), paragraf(4, "FSN-2024-3")]
)


def steg(sida: int, namn: str = "Ny skola") -> Steg:
    return Steg("fsn", namn, 2024, "vackt", "", "text", f"{FIL}#sida-{sida}", "")


class TestKortkoppling(unittest.TestCase):
    def test_sidan_tacks_av_den_sista_paragrafen_som_borjat(self):
        self.assertEqual(tacker(INDEX, f"{FIL}#sida-3"), [["FSN-2024-1"]])

    def test_paragraferna_som_borjar_pa_sidan(self):
        paragraferna = [["FSN-2024-2"], ["FSN-2024-3"]]
        self.assertEqual(tacker(INDEX, f"{FIL}#sida-4"), paragraferna)

    def test_en_kalla_over_flera_sidor_raknas_fran_den_forsta(self):
        self.assertEqual(tacker(INDEX, f"{FIL}#sida-3-5"), [["FSN-2024-1"]])

    def test_en_sida_fore_forsta_paragrafen_och_ett_annat_dokument(self):
        self.assertEqual(tacker(INDEX, f"{FIL}#sida-1"), [])
        self.assertEqual(tacker(INDEX, "fsn/2024/2024-05-02/handlingar.md#sida-3"), [])

    def test_kortet_lankas_och_ar_tolkat_nar_sidan_har_andra_nummer(self):
        lankar = kortlankar(exempelby(), [(INITIATIV, [steg(3), steg(4)])], INDEX)
        adress = "exempelby/fsn/initiativ.html#sak-0"
        rubrik = "Initiativ och motioner, Förskole- och skolnämnden: Ny skola"
        self.assertEqual(lankar["FSN-2024-1"], [Kortlank(adress, rubrik, False)])
        self.assertEqual(lankar["FSN-2024-3"], [Kortlank(adress, rubrik, True)])

    def test_en_paragraf_med_tva_nummer_ar_inte_tolkad(self):
        index = sidindex([paragraf(2, "FSN-2024-1", "FSN-2024-9")])
        lankar = kortlankar(exempelby(), [(INITIATIV, [steg(2)])], index)
        self.assertFalse(lankar["FSN-2024-1"][0].tolkad)
        self.assertFalse(lankar["FSN-2024-9"][0].tolkad)
