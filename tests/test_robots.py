"""Krav: K10, ADR-0013. Kod: src/kommunhandlingar/hamtning/robots.py."""

import unittest
from pathlib import Path

from kommunhandlingar.hamtning.robots import tillater, tolka

FIXTURER = Path(__file__).parent / "fixtures"
SIDA = "https://exempelby.se"


def far(text: str, sokvag: str, produkt: str = "kommunhandlingar") -> bool:
    return tillater(tolka(text, produkt), SIDA + sokvag)


class TestRobots(unittest.TestCase):
    def test_utan_regler_ar_allt_tillatet(self):
        self.assertTrue(far("", "/vad-som-helst"))

    def test_prefix_stanger(self):
        self.assertFalse(far("User-agent: *\nDisallow: /privat", "/privat/a.pdf"))
        self.assertTrue(far("User-agent: *\nDisallow: /privat", "/publik"))

    def test_jokertecken_och_slut(self):
        text = "User-agent: *\nDisallow: /*91.*\nDisallow: /*.pdf$"
        self.assertFalse(far(text, "/download/18.1/2/protokoll%2076-91.pdf"))
        self.assertFalse(far(text, "/a.pdf"))
        self.assertTrue(far(text, "/a.pdf?x=1"))

    def test_fragestrangen_raknas(self):
        self.assertFalse(far("User-agent: *\nDisallow: /*?sv*", "/sida?sv.state=1"))

    def test_langsta_regeln_och_allow_vid_lika(self):
        text = "User-agent: *\nDisallow: /a\nAllow: /a/b\nDisallow: /a/c\nAllow: /a/c"
        self.assertFalse(far(text, "/a/x"))
        self.assertTrue(far(text, "/a/b"))
        self.assertTrue(far(text, "/a/c"))

    def test_egen_grupp_fore_stjarnan(self):
        text = (
            "User-agent: *\nDisallow: /\n\n"
            "User-agent: Kommunhandlingar\nUser-agent: annan\nDisallow: /hemligt"
        )
        self.assertTrue(far(text, "/oppet"))
        self.assertFalse(far(text, "/hemligt"))
        self.assertFalse(far(text, "/oppet", "annanrobot"))

    def test_tom_egen_grupp_tillater_allt(self):
        text = "User-agent: *\nDisallow: /\n\nUser-agent: kommunhandlingar\nDisallow:"
        self.assertTrue(far(text, "/oppet"))

    def test_kommentarer_och_sitemap_bryter_inte_gruppen(self):
        text = "User-agent: * # alla\nSitemap: /karta.xml\nDisallow: /x # nej"
        self.assertFalse(far(text, "/x"))

    def test_kungsbacka(self):
        text = (FIXTURER / "kungsbacka-robots.txt").read_text()
        protokoll = (
            "/download/18.1/2/N%C3%A4mnden%20f%C3%B6r%20V%C3%A5rd%20%26%20Omsorg%20"
            "protokoll%202025-05-15,%20%C2%A7%C2%A7%2074,%2076-91.pdf"
        )
        self.assertFalse(far(text, protokoll))
        self.assertTrue(far(text, "/download/18.2/3/Protokoll%202025-05-15.pdf"))
        self.assertTrue(far(text, "/kommun-och-politik/sammantraden"))
