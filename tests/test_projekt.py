"""Krav: K46 i docs/02-KRAV.md, ADR-0069. Kod: src/kommunhandlingar/webbplats/
projekt.py."""

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import las as las_kommun
from kommunhandlingar.webbplats import projekt, spar
from kommunhandlingar.webbplats.sparkort import projektet
from kommunhandlingar.webbplats.sparslag import DETALJPLANER
from tests.test_detaljplaner import ROT, sida
from tests.test_webbplats import dokument, exempelby

RUBRIK = "organ,detaljplan,projekt,tolkad\n"
PLAN = "Skola inom Skolan 1:2"
LISTA = "https://exempelby.se/projekt"


def kommunen():
    kommun = exempelby()
    kalla = replace(kommun.kallor[0], projekt={"fsn": LISTA})
    return replace(kommun, kallor=(kalla,))


# Varje fil som namn i poolen och filnamn i källans adress.
def las(rader: str, filer: dict[str, str] | None = None) -> dict[str, projekt.Projekt]:
    with tempfile.TemporaryDirectory() as tmp:
        fil, data = Path(tmp) / "exempelby.csv", Path(tmp) / "data"
        fil.write_text(RUBRIK + rader, encoding="utf-8")
        for nr, (namn, filnamn) in enumerate((filer or {}).items(), 1):
            stalle = data / f"fsn/2024/2024-0{nr}-01/handlingar-{namn}.md"
            stalle.parent.mkdir(parents=True, exist_ok=True)
            url = f"https://exempelby.se/download/18.c{nr}/1/{filnamn}"
            text = dokument(
                datum=f"2024-0{nr}-01", typ="handlingar", namn=namn, url=url
            )
            stalle.write_text(text, encoding="utf-8")
        return projekt.las(fil, kommunen(), data)


class TestLas(unittest.TestCase):
    def test_projektets_adress_och_dokument(self):
        filer = {
            "skolan-plankarta": "PM%20Plankarta%20f%C3%B6r%20R-51%202021-10-08.pdf",
            "skolan-del-2-buller": "Buller.pdf",
            "annat-skolan-pm": "PM.pdf",
        }
        rader = f"fsn,{PLAN},skolan,\nfsn,Annan plan,skolan-del-2,ja\n"
        projekten = las(rader, filer)
        skolan = projekten[PLAN]
        self.assertEqual(skolan.adress, f"{LISTA}/skolan")
        self.assertFalse(skolan.tolkad)
        self.assertEqual(
            skolan.dokument,
            (
                (
                    "2024-01-01",
                    "PM Plankarta för R-51 2021-10-08",
                    "fsn/2024/2024-01-01/handlingar-skolan-plankarta.html",
                ),
            ),
        )
        self.assertEqual([d[1] for d in projekten["Annan plan"].dokument], ["Buller"])
        self.assertTrue(projekten["Annan plan"].tolkad)

    def test_fel_rubrik_stoppar(self):
        with tempfile.TemporaryDirectory() as tmp:
            fil = Path(tmp) / "exempelby.csv"
            fil.write_text("organ,plan,projekt,tolkad\n", encoding="utf-8")
            with self.assertRaisesRegex(Datafel, "rubrikerna är inte"):
                projekt.las(fil, kommunen(), Path(tmp))

    def test_fel_rad_stoppar(self):
        fel = {
            "bun,X,skolan,\n": "ingen lista med projekt",
            f"fsn,{PLAN},skolan,\nfsn,{PLAN},annat,\n": "står redan i filen",
            "fsn,,skolan,\n": "är tom",
            f"fsn,{PLAN},Skolan/1,\n": "inte en del av en adress",
            f"fsn,{PLAN},skolan,kanske\n": "varken tom eller ja",
            f"fsn,{PLAN},skolan\n": "3 fält",
        }
        for rader, orsak in fel.items():
            with self.subTest(rader), self.assertRaisesRegex(Datafel, orsak):
                las(rader)

    def test_plan_som_inte_finns_stoppar(self):
        projekten = las(f"fsn,Okänd plan,skolan,\nfsn,{PLAN},skolan-2,\n")
        steg = spar.Steg("bun", PLAN, 2024, "samrad", "", "t", "k", "")
        with self.assertRaisesRegex(Datafel, "'Okänd plan' står inte"):
            projekt.kontrollera(projekten, [steg], "projekt/exempelby.csv")


class TestKortet(unittest.TestCase):
    def test_lank_och_dokument_pa_planens_kort(self):
        projekten = las(
            f"fsn,{PLAN},skolan,ja\n", {"skolan-plankarta": "SKA-rapport.pdf"}
        )
        html = sida(projekten)
        self.assertIn(f'<a href="{LISTA}/skolan">Kommunens projektsida</a>', html)
        self.assertIn("<small>tolkad</small>", html)
        self.assertIn("Projektets dokument i poolen, 1 st", html)
        self.assertIn(
            '<a href="../fsn/2024/2024-01-01/handlingar-skolan-plankarta.html">'
            "SKA-rapport</a> 2024-01-01",
            html,
        )

    def test_projekt_utan_dokument(self):
        html = projektet(las(f"fsn,{PLAN},skolan,\n")[PLAN])
        self.assertIn("Projektets dokument: inga i poolen.", html)
        self.assertEqual(projektet(None), "")


class TestKungsbacka(unittest.TestCase):
    def test_filen_gar_ihop_med_kommunfilen_och_detaljplanerna(self):
        kungsbacka = las_kommun(ROT / "kommuner" / "kungsbacka.toml")
        data = ROT / "data" / "kungsbacka"
        fil = ROT / "projekt" / "kungsbacka.csv"
        projekten = projekt.las(fil, kungsbacka, data)
        planer = ROT / "detaljplaner" / "kungsbacka.csv"
        stegen = spar.las(planer, kungsbacka, data, DETALJPLANER)
        projekt.kontrollera(projekten, stegen, "projekt/kungsbacka.csv")
        self.assertEqual(fil.read_bytes().count(b"\r"), 0)
