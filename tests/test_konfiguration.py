"""Krav: K1 i docs/02-KRAV.md. Kod: src/kommunhandlingar/konfiguration.py."""

import copy
import tomllib
import unittest
from datetime import date, datetime
from pathlib import Path

from kommunhandlingar.fel import Konfigurationsfel
from kommunhandlingar.konfiguration import las, tolka

FIXTURER = Path(__file__).parent / "fixtures"
ROT = Path(__file__).parent.parent


def exempelby() -> dict:
    with (FIXTURER / "exempelby.toml").open("rb") as fil:
        return tomllib.load(fil)


class TestKommunfilen(unittest.TestCase):
    def test_exempelby_lases(self):
        kommun = las(FIXTURER / "exempelby.toml")
        self.assertEqual(kommun.id, "exempelby")
        self.assertEqual([o.id for o in kommun.organ], ["bun", "fsn"])
        self.assertEqual(kommun.organ[1].foregangare, ("bun",))
        self.assertEqual(
            kommun.kallor[0].rattelser, {"sitevision:18.abc": date(2024, 5, 2)}
        )

    def test_kungsbacka_lases(self):
        kommun = las(ROT / "kommuner" / "kungsbacka.toml")
        self.assertEqual(len(kommun.organ), 17)
        self.assertEqual(kommun.organ[0].id, "ga")
        self.assertEqual([o.id for o in kommun.organ[-3:]], ["ks", "ks-au", "kf"])
        self.assertFalse(kommun.kallor[0].wayback)

    def test_utan_arkiv(self):
        self.assertFalse(las(FIXTURER / "exempelby.toml").kallor[0].wayback)


class TestFelStopparKorningen(unittest.TestCase):
    def stoppas(self, andra, kommun_id: str = "exempelby"):
        data = copy.deepcopy(exempelby())
        andra(data)
        with self.assertRaises(Konfigurationsfel):
            tolka(kommun_id, data)

    def test_okant_falt(self):
        self.stoppas(lambda d: d.update(kommunkod="1384"))
        self.stoppas(lambda d: d["organ"][0].update(prioritet=1))
        self.stoppas(lambda d: d["kalla"][0].update(startadress="x"))
        self.stoppas(lambda d: d["kalla"][0]["monster"][0].update(organ="x"))

    def test_id_som_inte_ar_katalognamn(self):
        self.stoppas(lambda d: d["organ"][0].update(id="Bun"))
        self.stoppas(lambda d: None, kommun_id="Exempel by")

    def test_tva_organ_med_samma_id(self):
        self.stoppas(lambda d: d["organ"][1].update(id="bun", foregangare=[]))

    def test_organ_utan_namn(self):
        self.stoppas(lambda d: d["organ"][0].update(namn=[]))
        self.stoppas(lambda d: d["organ"][0].pop("namn"))

    def test_foregangare_som_inte_finns(self):
        self.stoppas(lambda d: d["organ"][1].update(foregangare=["kun"]))

    def test_samma_namn_med_overlappande_period(self):
        def overlapp(data):
            data["organ"][1]["namn"] = ["barn-  och UNGDOMSNÄMNDEN"]
            del data["organ"][1]["fran"]

        self.stoppas(overlapp)

    def test_varde_av_fel_slag(self):
        self.stoppas(lambda d: d["organ"][0].update(fran="2019-01-01"))
        self.stoppas(lambda d: d["organ"][0].update(fran=datetime(2019, 1, 1, 8)))
        self.stoppas(lambda d: d["organ"][0].update(namn="Barn- och ungdomsnämnden"))
        self.stoppas(lambda d: d.update(organ={}))

    def test_okand_adapter(self):
        self.stoppas(lambda d: d["kalla"][0].update(adapter="episerver"))

    def test_wayback_ar_sant_eller_falskt(self):
        self.stoppas(lambda d: d["kalla"][0].update(wayback="ja"))


class TestSammaNamnUtanOverlapp(unittest.TestCase):
    def test_godkanns(self):
        data = exempelby()
        data["organ"][1]["namn"] = ["Barn- och ungdomsnämnden"]
        self.assertEqual(len(tolka("exempelby", data).organ), 2)


if __name__ == "__main__":
    unittest.main()
