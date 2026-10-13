"""Krav: K1, K2 och K23 i docs/02-KRAV.md, ADR-0039.
Kod: src/kommunhandlingar/adaptrar/episerver.py och konfiguration.py."""

import copy
import unittest
from datetime import date

from kommunhandlingar.adaptrar.episerver import Kalla, kalla_av, typ_och_datum
from kommunhandlingar.fel import IngenKandidat, Konfigurationsfel
from kommunhandlingar.konfiguration import tolka
from tests.test_konfiguration import exempelby

MAPP = "exempelby.se/Global/Möten/Barn och ungdom/"
POST = {
    "adapter": "episerver",
    "manader": [
        "jan",
        "feb",
        "mar",
        "apr",
        "maj",
        "jun",
        "jul",
        "aug",
        "sep",
        "okt",
        "nov",
        "dec",
    ],
    "datum": [
        r"(?P<ar>\d{4})-(?P<manad>\d{2})-(?P<dag>\d{2})",
        r"(?<!\d)(?P<ar>\d{4})(?P<manad>\d{2})(?P<dag>\d{2})(?!\d)",
        r"(?<!\d)(?P<ar>\d{2})(?P<manad>\d{2})(?P<dag>\d{2})(?!\d)",
        r"(?i)^[^/]+/(?P<ar>\d{4})/[^/]*?(?P<dag>\d{1,2}) (?P<manad>[a-zåäö]{3})",
    ],
    "mappar": {"bun": [MAPP]},
    "typer": [
        {"typ": "handlingar", "regex": "(?i)^handlingar/"},
        {"typ": "kallelse", "regex": "(?i)/[^/]*kallelse[^/]*$"},
        {"typ": "protokoll", "regex": "(?i)^protokoll/"},
    ],
    "rattelser": {"episerver:exempelby.se/x/1.pdf": date(2014, 2, 19)},
}


def kalla(**andrat) -> Kalla:
    return kalla_av(POST | andrat, ["bun", "fsn"], "kalla 2")


class TestKommunfilen(unittest.TestCase):
    def test_lases_som_arkivkalla(self):
        data = exempelby()
        data["kalla"].append(copy.deepcopy(POST))
        kommun = tolka("exempelby", data)
        self.assertEqual(len(kommun.kallor), 1)
        self.assertEqual(kommun.arkivkallor[0].mappar, {"bun": (MAPP,)})

    def test_mappar_for_ett_okant_organ(self):
        with self.assertRaisesRegex(Konfigurationsfel, "mapparna för 'okant'"):
            kalla(mappar={"okant": [MAPP]})

    def test_en_mapp_slutar_pa_snedstreck(self):
        with self.assertRaisesRegex(Konfigurationsfel, "slutar inte på /"):
            kalla(mappar={"bun": ["exempelby.se/Global"]})

    def test_datummonster_har_alla_datumgrupper(self):
        with self.assertRaisesRegex(Konfigurationsfel, "grupperna ar, manad och dag"):
            kalla(datum=[r"(?P<ar>\d{4})"])

    def test_typmonster_har_en_typ(self):
        with self.assertRaisesRegex(Konfigurationsfel, "antingen gruppen"):
            kalla(typer=[{"regex": "x"}])

    def test_rattelse_med_en_annan_plattform(self):
        with self.assertRaisesRegex(Konfigurationsfel, "rättelsen"):
            kalla(rattelser={"sitevision:18.a": date(2014, 2, 19)})


class TestTypOchDatum(unittest.TestCase):
    def tolkat(self, text: str, nyckel: str = "episerver:x") -> tuple[str, date]:
        return typ_och_datum(kalla(), text, nyckel)

    def test_mappen_ger_typen(self):
        self.assertEqual(
            self.tolkat("Protokoll/2018/2018-02-07.pdf"),
            ("protokoll", date(2018, 2, 7)),
        )

    def test_filnamnet_gar_fore_mappen(self):
        self.assertEqual(
            self.tolkat("Protokoll/2014/Kallelse nämnd 140514.pdf"),
            ("kallelse", date(2014, 5, 14)),
        )

    def test_forsta_monstret_som_matchar_galler(self):
        self.assertEqual(
            self.tolkat("Handlingar/2018/kallelse-till-web-20180919.pdf")[0],
            "handlingar",
        )

    def test_datum_i_filnamnet_gar_fore_mappens_ar(self):
        self.assertEqual(
            self.tolkat("protokoll/2021/protokoll-220119.pdf")[1], date(2022, 1, 19)
        )

    def test_mappens_ar_och_manadens_forkortning(self):
        self.assertEqual(
            self.tolkat("Protokoll/2013/GV protokoll 20 november.pdf")[1],
            date(2013, 11, 20),
        )

    def test_rattelsen_galler(self):
        self.assertEqual(
            self.tolkat("Protokoll/2014/01.pdf", "episerver:exempelby.se/x/1.pdf"),
            ("protokoll", date(2014, 2, 19)),
        )

    def test_utan_datum_blir_det_ingen_kandidat(self):
        with self.assertRaisesRegex(IngenKandidat, "inget datummönster"):
            self.tolkat("Protokoll/2014/01.pdf")

    def test_utan_typ_blir_det_ingen_kandidat(self):
        with self.assertRaisesRegex(IngenKandidat, "inget typmönster"):
            self.tolkat("Ovrigt/2014/2014-02-19.pdf")

    def test_ett_datum_som_inte_finns(self):
        with self.assertRaisesRegex(IngenKandidat, "datumet finns inte"):
            self.tolkat("Protokoll/2021/211340.pdf")


if __name__ == "__main__":
    unittest.main()
