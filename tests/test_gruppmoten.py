"""Krav: K49 i docs/02-KRAV.md, ADR-0072. Kod: src/kommunhandlingar/gruppmote.py,
webbplats/kalender.py, kalendervyer.py och kalendersida.py."""

import tomllib
import unittest
from datetime import UTC, date, datetime
from pathlib import Path

from kommunhandlingar.fel import Konfigurationsfel
from kommunhandlingar.gruppmote import Gruppmote
from kommunhandlingar.konfiguration import las as las_kommun
from kommunhandlingar.konfiguration import tolka
from kommunhandlingar.webbplats.kalender import Sammantrade, dagen_fore, gruppmoten
from kommunhandlingar.webbplats.kalendersida import kalendersida
from kommunhandlingar.webbplats.mall import Mall

FIXTURER = Path(__file__).parent / "fixtures"
ROT = Path(__file__).parent.parent
REGEL = Gruppmote("fsn", 0, "kväll")
TID = datetime(2026, 11, 14, 20, 0, tzinfo=UTC)


def kommun(gruppmote: dict | None):
    with (FIXTURER / "exempelby.toml").open("rb") as fil:
        data = tomllib.load(fil)
    if gruppmote is not None:
        data["gruppmote"] = gruppmote
    return tolka("exempelby", data)


def sammantrade(organ: str, datum: str) -> Sammantrade:
    return Sammantrade(organ, date.fromisoformat(datum), "", "", "https://x.se", "")


SAMMANTRADEN = [
    sammantrade("fsn", "2026-11-10"),
    sammantrade("fsn", "2026-11-17"),
    sammantrade("bun", "2026-11-24"),
]


class TestKommunfilen(unittest.TestCase):
    def test_regeln_lases(self):
        regel = {"fore": "fsn", "veckodag": "måndag", "tid": "kväll"}
        self.assertEqual(kommun(regel).gruppmote, REGEL)

    def test_utan_regel(self):
        self.assertIsNone(kommun(None).gruppmote)

    def test_okant_organ(self):
        with self.assertRaises(Konfigurationsfel):
            kommun({"fore": "ks", "veckodag": "måndag", "tid": "kväll"})

    def test_okand_veckodag(self):
        with self.assertRaises(Konfigurationsfel):
            kommun({"fore": "fsn", "veckodag": "Måndag", "tid": "kväll"})

    def test_kungsbacka_fore_kommunstyrelsen(self):
        kungsbacka = las_kommun(ROT / "kommuner" / "kungsbacka.toml")
        self.assertEqual(kungsbacka.gruppmote, Gruppmote("ks", 0, "kväll"))


class TestGruppmoten(unittest.TestCase):
    def test_dagen_fore_ar_narmaste_veckodag_fore(self):
        for sammantrade_dag, mote in [
            ("2027-01-12", "2027-01-11"),
            ("2027-01-14", "2027-01-11"),
            ("2027-01-11", "2027-01-04"),
        ]:
            datum = dagen_fore(date.fromisoformat(sammantrade_dag), 0)
            self.assertEqual(datum, date.fromisoformat(mote))

    def test_bara_organets_kommande(self):
        moten = gruppmoten(SAMMANTRADEN, REGEL, date(2026, 11, 14))
        self.assertEqual([m.datum for m in moten], [date(2026, 11, 16)])
        self.assertEqual(moten[0].tid, "kväll")

    def test_dagens_gruppmote_tas_med(self):
        moten = gruppmoten(SAMMANTRADEN, REGEL, date(2026, 11, 16))
        self.assertEqual(len(moten), 1)

    def test_tva_sammantraden_samma_vecka_ett_gruppmote(self):
        tva = [sammantrade("fsn", "2026-11-17"), sammantrade("fsn", "2026-11-19")]
        moten = gruppmoten(tva, REGEL, date(2026, 11, 1))
        self.assertEqual([m.datum for m in moten], [date(2026, 11, 16)])

    def test_utan_regel_inga(self):
        self.assertEqual(gruppmoten(SAMMANTRADEN, None, date(2026, 1, 1)), [])


class TestSidan(unittest.TestCase):
    def sida(self, gruppmote: dict | None) -> str:
        k = kommun(gruppmote)
        return kalendersida(Mall([k], "https://github.com/x/y", TID), k, SAMMANTRADEN)

    def test_gruppmotet_i_vyerna_och_urvalet(self):
        html = self.sida({"fore": "fsn", "veckodag": "måndag", "tid": "kväll"})
        self.assertIn('data-organ="gruppmöte">Gruppmöte kväll</span>', html)
        self.assertIn('data-datum="2026-11-16"', html)
        self.assertIn('type="checkbox" checked data-organ="gruppmöte"', html)
        self.assertIn("Partiernas gruppmöte inför Förskole- och skolnämnden", html)
        self.assertIn("Det är en vana hos partierna, inget beslutat", html)
        self.assertIn("måndagen före varje sammanträde i Förskole-", html)

    def test_gruppmoten_raknas_inte_som_sammantraden(self):
        html = self.sida({"fore": "fsn", "veckodag": "måndag", "tid": "kväll"})
        self.assertIn("0 av 3 datum är osäkra", html)

    def test_utan_regel_inget_om_gruppmoten(self):
        html = self.sida(None)
        self.assertNotIn('data-organ="gruppmöte"', html)
        self.assertNotIn("Partierna har gruppmöte", html)
