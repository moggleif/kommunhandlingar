"""Krav: K15, ADR-0017. Kod: src/kommunhandlingar/konvertering/figurer.py,
src/kommunhandlingar/tolkning.py och skrivning.py.

Sidan är 100 × 100 punkter, så att en andel av sidan är lika många
kvadratpunkter i hundratal: en bild på 20 × 20 täcker 4 %.
"""

import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from kommunhandlingar import frontmatter, skrivning
from kommunhandlingar.konvertering import las_sida
from kommunhandlingar.konvertering.dokument import konvertera
from kommunhandlingar.konvertering.figurer import har_figur
from kommunhandlingar.tolkning import AndratOriginal, arbetslista, rendera
from tests.test_hamta import Klient

PDF = Path(__file__).parent / "fixtures" / "pdf"


def ruta(x0: float, top: float, x1: float, bottom: float, **mer) -> dict:
    hoj = {"width": x1 - x0, "height": bottom - top}
    return {"x0": x0, "top": top, "x1": x1, "bottom": bottom} | hoj | mer


def stapel(x0: float, farg=(0.2, 0.4, 0.8), bredd: float = 4) -> dict:
    fyllning = {"stroke": False, "fill": True, "non_stroking_color": farg}
    return ruta(x0, 40, x0 + bredd, 90, **fyllning)


def sida(images=(), curves=(), rects=(), chars=()) -> SimpleNamespace:
    return SimpleNamespace(
        width=100, height=100, images=list(images), curves=list(curves),
        rects=list(rects), chars=list(chars),
    )  # fmt: skip


STAPLAR = [stapel(10 + 10 * i) for i in range(8)]


class TestRegeln(unittest.TestCase):
    def test_bild_over_tva_procent_ar_en_figur(self):
        self.assertTrue(har_figur(sida(images=[ruta(10, 10, 30, 30)]), []))

    def test_liten_logotyp_ar_ingen_figur(self):
        self.assertFalse(har_figur(sida(images=[ruta(10, 10, 20, 15)]), []))

    def test_bild_over_hela_sidan_ar_en_skanning(self):
        self.assertFalse(har_figur(sida(images=[ruta(0, 0, 100, 100)]), []))

    def test_atta_staplar_ar_en_figur(self):
        self.assertTrue(har_figur(sida(rects=STAPLAR), []))

    def test_sju_staplar_ar_ingen_figur(self):
        self.assertFalse(har_figur(sida(rects=STAPLAR[:7]), []))

    def test_atta_kurvor_pa_liten_yta_ar_ett_vapen(self):
        kurvor = [ruta(80, 5, 81 + i * 0.2, 6) for i in range(8)]
        self.assertFalse(har_figur(sida(curves=kurvor), []))

    def test_vita_ytor_och_tunna_linjer_raknas_inte(self):
        vita = [stapel(10 + 10 * i, farg=(1, 1, 1)) for i in range(4)]
        tunna = [stapel(50 + 10 * i, bredd=2) for i in range(4)]
        self.assertFalse(har_figur(sida(rects=vita + tunna), []))

    def test_ytor_med_text_i_raknas_inte(self):
        tecken = [ruta(s["x0"] + 1, 50, s["x0"] + 3, 52) for s in STAPLAR]
        self.assertFalse(har_figur(sida(rects=STAPLAR, chars=tecken), []))

    def test_ytor_i_en_saker_tabell_raknas_inte(self):
        self.assertFalse(har_figur(sida(rects=STAPLAR), [(0, 0, 100, 100)]))

    def test_en_sida_som_lases_med_ocr_provas_ocksa(self):
        with mock.patch.object(las_sida.figurer, "har_figur", return_value=True):
            sidor = konvertera(PDF / "sidor.pdf").sidor
        self.assertEqual((sidor[8].kvalitet, sidor[8].figur), ("ej-konverterad", True))

    def test_stapeldiagrammet_i_fixturen_marks(self):
        self.assertEqual(konvertera(PDF / "sidor.pdf").figurer, [17])


class TestVerktygen(unittest.TestCase):
    def setUp(self):
        katalog = tempfile.TemporaryDirectory()
        self.addCleanup(katalog.cleanup)
        self.rot = Path(katalog.name)
        self.md = self.rot / "data/exempelby/ks/2025/2025-04-22/protokoll.md"
        self.md.parent.mkdir(parents=True)
        sha = hashlib.sha256((PDF / "sidor.pdf").read_bytes()).hexdigest()
        self.skriv(figurer="[2, 17]", tolkade="[2]", sha256=sha)

    def skriv(self, **falt) -> None:
        grund = dict.fromkeys(frontmatter.FALT, "null") | {"kalla_url": "u1"}
        self.md.write_text(frontmatter.skriv(grund | falt), encoding="utf-8")

    def test_arbetslistan_har_de_otolkade_sidorna(self):
        rader = arbetslista(self.rot / "data")
        self.assertEqual(rader, ["exempelby/ks/2025/2025-04-22/protokoll.md: [17]"])

    def test_dokument_utan_figurer_star_inte_i_listan(self):
        self.skriv(figurer="null", tolkade="null")
        self.assertEqual(arbetslista(self.rot / "data"), [])

    def test_de_otolkade_sidorna_renderas(self):
        klient = Klient()
        klient.filer["u1"] = "sidor.pdf"
        (png,) = rendera(self.md, self.rot, klient)
        self.assertEqual(png, self.rot / "17.png")
        self.assertGreater(png.stat().st_size, 0)

    def test_dokument_utan_otolkade_sidor_hamtas_inte(self):
        self.skriv(figurer="null", tolkade="null")
        klient = Klient()
        self.assertEqual(rendera(self.md, self.rot / "ny", klient), [])
        self.assertEqual(klient.anrop, [])

    def test_ett_andrat_original_renderas_inte(self):
        klient = Klient()
        klient.filer["u1"] = "begransad.pdf"
        with self.assertRaises(AndratOriginal):
            rendera(self.md, self.rot, klient)
        self.assertEqual(list(self.rot.glob("*.png")), [])

    def test_en_ny_konvertering_tar_bort_tolkningarna(self):
        katalog = skrivning.tabellkatalog(self.md)
        katalog.mkdir()
        (katalog / "17-1.tolkad.csv").write_text("År,Besök\n2023,120\n")
        skrivning.skriv(self.md, "ny text\n", {"2-1.csv": "a,b\n"})
        self.assertEqual([p.name for p in katalog.iterdir()], ["2-1.csv"])


if __name__ == "__main__":
    unittest.main()
