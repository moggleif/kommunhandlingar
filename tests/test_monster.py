"""Krav: K1 och K2 i docs/02-KRAV.md. Kod: src/kommunhandlingar/monster.py."""

import unittest
from datetime import date

from kommunhandlingar.fel import IngenKandidat, Konfigurationsfel
from kommunhandlingar.monster import kompilera, manader, tolka

GRUPPER = {"ar", "manad", "dag", "typ"}
DATUM = r"(?P<ar>\d+)-(?P<manad>\d+)-(?P<dag>\d+)"
MANADER = ("januari", "februari", "mars", "april", "maj", "juni")
MANADER += ("juli", "augusti", "september", "oktober", "november", "december")


def monster(*poster: dict):
    return tuple(kompilera(post, GRUPPER, "test") for post in poster)


class TestKompilera(unittest.TestCase):
    def stoppas(self, post: dict):
        with self.assertRaises(Konfigurationsfel):
            kompilera(post, GRUPPER, "test")

    def test_grupp_som_adaptern_inte_tar(self):
        self.stoppas({"regex": r"(?P<organ>\w+) (?P<typ>protokoll)"})
        self.stoppas({"regex": r"(?P<nummer>\d+) (?P<typ>protokoll)"})

    def test_bara_nagra_av_datumgrupperna(self):
        self.stoppas({"regex": r"(?P<typ>protokoll) (?P<ar>\d{4})"})

    def test_bade_eller_ingen_av_grupp_och_falt_typ(self):
        self.stoppas({"regex": r"(?P<typ>protokoll)", "typ": "protokoll"})
        self.stoppas({"regex": r"protokoll"})

    def test_okand_typ_i_faltet(self):
        self.stoppas({"regex": r"budget", "typ": "budget"})

    def test_ogiltigt_uttryck(self):
        self.stoppas({"regex": r"(?P<typ>protokoll", "typ": "protokoll"})

    def test_manadslista_med_fel_antal_eller_dubbletter(self):
        for lista in (MANADER[:11], MANADER[:11] + ("Januari",), MANADER + ("x",)):
            with self.subTest(lista=lista), self.assertRaises(Konfigurationsfel):
                manader({"manader": list(lista)}, "test")
        self.assertEqual(manader({}, "test"), ())


class TestTolka(unittest.TestCase):
    def test_typ_och_datum_ur_gruppen(self):
        tolkning = tolka(
            monster({"regex": rf"(?P<typ>\w+) {DATUM}"}), "Protokoll 2026-08-11", ()
        )
        self.assertEqual(
            (tolkning.typ, tolkning.datum), ("protokoll", date(2026, 8, 11))
        )

    def test_typ_ur_faltet_och_inget_datum(self):
        tolkning = tolka(
            monster({"regex": "§", "typ": "protokoll"}), "protokoll § 22", ()
        )
        self.assertEqual((tolkning.typ, tolkning.datum), ("protokoll", None))

    def test_manadens_namn(self):
        uttryck = r"(?P<dag>\d+) (?P<manad>\w+) (?P<ar>\d+)"
        tolkning = tolka(
            monster({"regex": uttryck, "typ": "kallelse"}), "6 Oktober 2026", MANADER
        )
        self.assertEqual(tolkning.datum, date(2026, 10, 6))

    def test_forsta_monstret_som_matchar_galler(self):
        poster = (
            {"regex": rf"(?P<typ>budget) {DATUM}"},
            {"regex": "budget", "typ": "bilaga"},
        )
        with self.assertRaises(IngenKandidat):
            tolka(monster(*poster), "budget 2026-01-01", ())

    def test_ingen_kandidat(self):
        fall = {
            "inget mönster matchar": "Årsredovisning 2025",
            "datum som inte finns": "kallelse 2025-02-30",
            "år utan fyra siffror": "kallelse 24-11-11",
            "okänt månadsnamn": "kallelse 2025-mars-03",
            "tom typ": " 2025-03-03",
            "ofullständigt datum": "kallelse 2025--03",
        }
        poster = monster(
            {"regex": r"(?P<typ>kallelse|) (?P<ar>\d+)-(?P<manad>\w+)?-(?P<dag>\d+)"}
        )
        for orsak, text in fall.items():
            with self.subTest(orsak), self.assertRaises(IngenKandidat):
                tolka(poster, text, ())


if __name__ == "__main__":
    unittest.main()
