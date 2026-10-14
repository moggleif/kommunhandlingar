"""Krav: K23 i docs/02-KRAV.md, ADR-0039.
Kod: src/kommunhandlingar/adaptrar/episerver_arkiv.py."""

import unittest
from datetime import date

from kommunhandlingar.adaptrar.episerver_arkiv import nyckel_av, upptack
from kommunhandlingar.fel import Hamtfel
from tests.test_episerver import MAPP, kalla
from tests.test_sitevision_arkiv import Klient, bild

PDF = "mimetype:application/pdf"
G = "http://www.exempelby.se/Global/M%c3%b6ten/Barn%20och%20ungdom"
H = "https://exempelby.se/Global/M%C3%B6ten/Barn%20och%20ungdom"


class TestEpiserverArkivet(unittest.TestCase):
    def kandidater(self, svar):
        return upptack(kalla(), Klient({(MAPP, PDF): svar}, {}))

    def test_varje_fil_blir_en_kandidat(self):
        kandidater, avvisade, noteringar = self.kandidater(
            [
                ["20140703000000", f"{G}/Protokoll/2014/Protokoll%20140219.pdf", "9"],
                ["20140703000000", f"{G}/Handlingar/2014/H%20140219.pdf", "9"],
            ]
        )
        self.assertEqual(
            [(k.organ, k.datum, k.typ) for k in kandidater],
            [
                ("bun", date(2014, 2, 19), "protokoll"),
                ("bun", date(2014, 2, 19), "handlingar"),
            ],
        )
        self.assertEqual(kandidater[0].filnamn, "Protokoll 140219.pdf")
        self.assertEqual(kandidater[0].kalla, MAPP)
        self.assertEqual((avvisade, noteringar), ([], []))

    def test_samma_fil_under_flera_adresser_ar_en_fil(self):
        fil = "Protokoll/2014/Protokoll%20140219.pdf"
        kandidater, _, _ = self.kandidater(
            [
                ["20140101000000", f"{G}/{fil}", "5"],
                ["20150101000000", f"{H}/{fil}", "9"],
                ["20160101000000", f"{G}/{fil}", "9"],
            ]
        )
        self.assertEqual(len(kandidater), 1)
        self.assertEqual(kandidater[0].url, bild("20150101000000", f"{H}/{fil}"))
        self.assertEqual(
            kandidater[0].kallnyckel,
            "episerver:exempelby.se/Global/M%C3%B6ten/Barn%20och%20ungdom/" + fil,
        )

    def test_en_syskonmapp_med_langre_namn_hor_inte_till_mappen(self):
        kandidater, avvisade, _ = self.kandidater(
            [
                ["20140101000000", f"{G}/Protokoll/2014/P%20140219.pdf", "5"],
                ["20140101000000", f"{G}s%20au/Protokoll/2014/P%20140219.pdf", "5"],
            ]
        )
        self.assertEqual([k.filnamn for k in kandidater], ["P 140219.pdf"])
        self.assertEqual(avvisade, [])

    def test_nyckeln_har_inga_kommatecken_med_blanksteg(self):
        nyckel = nyckel_av("http://www.k.se:80/M%c3%b6ten,%20handlingar/a.pdf")
        self.assertEqual(nyckel, "episerver:k.se/M%C3%B6ten%2C%20handlingar/a.pdf")

    def test_en_fil_utan_datum_blir_ingen_kandidat(self):
        kandidater, avvisade, _ = self.kandidater(
            [["20140101000000", f"{G}/Protokoll/2014/01.pdf", "5"]]
        )
        self.assertEqual(kandidater, [])
        self.assertEqual(
            [(a.filnamn, a.orsak) for a in avvisade],
            [("01.pdf", "inget datummönster matchar")],
        )

    def test_en_mapp_som_arkivet_inte_svarar_for(self):
        kandidater, _, noteringar = self.kandidater(Hamtfel("anslutning"))
        self.assertEqual(kandidater, [])
        self.assertEqual(len(noteringar), 1)


if __name__ == "__main__":
    unittest.main()
