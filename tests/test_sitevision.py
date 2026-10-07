"""Krav: K1 och K2 i docs/02-KRAV.md, ADR-0011. Kod: src/kommunhandlingar/adaptrar/."""

import copy
import unittest
from datetime import date, datetime

from kommunhandlingar.adaptrar.sitevision import upptack
from kommunhandlingar.fel import Konfigurationsfel
from kommunhandlingar.konfiguration import las, tolka
from tests.test_konfiguration import FIXTURER, ROT, exempelby

LANK = '<a href="/download/18.{nod}/1/{namn}">{namn} (Pdf, 1 MB)</a>'
JSON = (
    '<script>AppRegistry.registerInitialState(\'12.1\',{{"files":[{{"id":"18.{nod}",'
    '"name":"x","uri":"/download/18.{nod}/2/{namn}","lastModifiedBy":"255.0"}}]}});</script>'
)


def sida(*moten: tuple[str, str]) -> str:
    return "<h2>Möten</h2>" + "".join(
        f"<h3>{rubrik}</h3>{filer}" for rubrik, filer in moten
    )


def lank(nod: str, namn: str) -> str:
    return LANK.format(nod=nod, namn=namn)


def json_fil(nod: str, namn: str) -> str:
    return JSON.format(nod=nod, namn=namn)


class TestUpptack(unittest.TestCase):
    def setUp(self):
        self.kalla = las(FIXTURER / "exempelby.toml").kallor[0]

    def upptack(self, html: str):
        return upptack(
            self.kalla,
            {"https://exempelby.se/bun": html, "https://exempelby.se/fsn": ""},
        )

    def test_bada_formerna_av_fillista(self):
        html = sida(
            ("2 maj 2024", lank("a1", "Kallelse%202024-05-02.pdf")),
            ("3 maj 2024", json_fil("b2", "Protokoll%202024-05-03.pdf")),
        )
        kandidater, avvisade = self.upptack(html)
        self.assertEqual(avvisade, [])
        self.assertEqual(
            [k.kallnyckel for k in kandidater], ["sitevision:18.a1", "sitevision:18.b2"]
        )
        forsta = kandidater[0]
        self.assertEqual(
            (forsta.organ, forsta.typ, forsta.datum),
            ("bun", "kallelse", date(2024, 5, 2)),
        )
        self.assertEqual(
            forsta.url,
            "https://exempelby.se/download/18.a1/1/Kallelse%202024-05-02.pdf",
        )
        self.assertEqual(forsta.filnamn, "Kallelse 2024-05-02.pdf")
        self.assertEqual(forsta.kalla, "https://exempelby.se/bun")

    def test_datum_ur_rubriken_nar_filnamnet_saknar_det(self):
        kandidater, _ = self.upptack(
            sida(("21 februari 2024", lank("a1", "protokoll%20%C2%A7%2022.pdf")))
        )
        self.assertEqual(
            (kandidater[0].typ, kandidater[0].datum), ("protokoll", date(2024, 2, 21))
        )

    def test_rubrik_utan_ar_ger_filnamnets_datum(self):
        kandidater, _ = self.upptack(
            sida(("16 oktober", lank("a1", "Kallelse%202025-10-16.pdf")))
        )
        self.assertEqual(kandidater[0].datum, date(2025, 10, 16))

    def test_olika_datum_ger_ingen_kandidat(self):
        kandidater, avvisade = self.upptack(
            sida(("22 januari 2024", lank("a1", "Kallelse%202025-01-22.pdf")))
        )
        self.assertEqual(kandidater, [])
        self.assertEqual([a.filnamn for a in avvisade], ["Kallelse 2025-01-22.pdf"])

    def test_rattelsen_galler(self):
        kandidater, _ = self.upptack(
            sida(("27 mars 2024", lank("abc", "Kallelse%202024-04-24.pdf")))
        )
        self.assertEqual(kandidater[0].datum, date(2024, 5, 2))

    def test_inget_datum_alls_ger_ingen_kandidat(self):
        _, avvisade = self.upptack(
            sida(("Extra möte", lank("a1", "protokoll%20%C2%A7%201.pdf")))
        )
        self.assertEqual(len(avvisade), 1)

    def test_fil_under_tva_moten_blir_en_kandidat(self):
        fil = lank("a1", "Kallelse%202024-05-15.pdf")
        kandidater, avvisade = self.upptack(
            sida(("24 april 2024", fil), ("15 maj 2024", fil))
        )
        self.assertEqual(avvisade, [])
        self.assertEqual([k.datum for k in kandidater], [date(2024, 5, 15)])

    def test_absolut_adress_till_filen(self):
        adress = "https://exempelby.se/download/18.a1/1/Kallelse%202024-05-02.pdf"
        html = sida(("2 maj 2024", f'<a href="{adress}">Kallelse</a>'))
        kandidater, _ = self.upptack(html)
        self.assertEqual(
            [(k.kallnyckel, k.url) for k in kandidater], [("sitevision:18.a1", adress)]
        )

    def test_nytt_ar_nollstaller_rubriken(self):
        fil = lank("a1", "protokoll%20%C2%A7%201.pdf")
        kandidater, avvisade = self.upptack(
            sida(("2 maj 2024", "")) + "<h2>2025</h2>" + fil
        )
        self.assertEqual((kandidater, len(avvisade)), ([], 1))

    def test_andra_lankar_raknas_inte(self):
        kandidater, avvisade = self.upptack(
            sida(("2 maj 2024", '<a href="/kontakta-oss">Kontakt</a>'))
        )
        self.assertEqual((kandidater, avvisade), ([], []))


class TestSitevisionsFaltStopparFel(unittest.TestCase):
    def stoppas(self, andra):
        data = copy.deepcopy(exempelby())
        andra(data["kalla"][0])
        with self.assertRaises(Konfigurationsfel):
            tolka("exempelby", data)

    def test_sida_for_organ_som_inte_finns(self):
        self.stoppas(
            lambda kalla: kalla["sidor"].update(kun="https://exempelby.se/kun")
        )

    def test_rubrik_utan_datumgrupperna(self):
        self.stoppas(lambda kalla: kalla.update(rubrik=r"(?P<dag>\d+) (?P<manad>\w+)"))

    def test_rattelse_som_inte_ar_ett_datum(self):
        self.stoppas(
            lambda kalla: kalla["rattelser"].update({"sitevision:18.abd": "2024-05-02"})
        )

    def test_monster_med_gruppen_organ(self):
        self.stoppas(
            lambda kalla: kalla["monster"].append(
                {"regex": r"(?P<organ>\w+)", "typ": "bilaga"}
            )
        )

    def test_rattelse_som_ar_en_tidpunkt(self):
        self.stoppas(
            lambda kalla: kalla["rattelser"].update(
                {"sitevision:18.abd": datetime(2024, 5, 2, 10)}
            )
        )

    def test_sidor_saknas(self):
        self.stoppas(lambda kalla: kalla.pop("sidor"))


AVVISADE = [
    "1384 2026-00068  om hastighet på Gåsevadholmsvägen.pdf",
    "Avfallsföreskrifter, Reviderad utställningsversion & förändringslogg"
    " 2026-08-03.pdf",
    "Delårsrapport 2024 för Kungsbacka kommun.pdf",
    "Kommunbudget 2025, plan 2026-2027.pdf",
    "Kommunbudget 2027, plan 2028-2029, kommunstyrelsens förslag till"
    " kommunfullmäktige.pdf",
    "Nämndbudget 2026, Nämnden för Teknik.pdf",
    "Särredovisning Teknik 2023.pdf",
    "Årsredovisning 2023 för Kungsbacka kommun.pdf",
    "Årsredovisning 2024 för Kungsbacka kommun.pdf",
    "Årsredovisning 2025 för Kungsbacka kommun.pdf",
]


class TestKungsbackasSparadeSidor(unittest.TestCase):
    """De 17 mötessidorna som de såg ut 2026-10-07, mot siffrorna i ADR-0011."""

    @classmethod
    def setUpClass(cls):
        cls.kalla = las(ROT / "kommuner" / "kungsbacka.toml").kallor[0]
        sidor = FIXTURER / "sitevision"
        html = {
            adress: (sidor / f"{adress.rsplit('/', 1)[1]}.html").read_text()
            for adress in cls.kalla.sidor.values()
        }
        cls.kandidater, cls.avvisade = upptack(cls.kalla, html)

    def test_antalet_kandidater(self):
        self.assertEqual(len(self.kandidater), 1662)
        self.assertEqual(len({k.kallnyckel for k in self.kandidater}), 1662)

    def test_de_som_inte_blev_kandidater(self):
        avvisade = sorted((a.filnamn, a.orsak) for a in self.avvisade)
        self.assertEqual(
            avvisade, [(namn, "inget mönster matchar") for namn in AVVISADE]
        )

    def test_varje_rattelse_galler(self):
        datum = {k.kallnyckel: k.datum for k in self.kandidater}
        for kallnyckel, ratt in self.kalla.rattelser.items():
            self.assertEqual(datum[kallnyckel], ratt, kallnyckel)

    def test_filer_som_bara_star_som_json(self):
        datum = {k.kallnyckel: k.datum for k in self.kandidater}
        self.assertEqual(
            datum["sitevision:18.64d6e63a1a0f5cec92f1f6d1"], date(2026, 10, 6)
        )

    def test_datum_ur_rubriken(self):
        kandidat = next(
            k
            for k in self.kandidater
            if k.filnamn == "Valnämnden protokoll 24-11-11.pdf"
        )
        self.assertEqual((kandidat.organ, kandidat.datum), ("val", date(2024, 11, 11)))

    def test_organet_ar_sidans(self):
        kandidat = next(
            k
            for k in self.kandidater
            if "Grundskolas arbetsutskott 21 augusti" in k.filnamn
        )
        self.assertEqual(kandidat.organ, "fg")


if __name__ == "__main__":
    unittest.main()
