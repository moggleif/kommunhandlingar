"""Krav: K72 i docs/02-KRAV.md, ADR-0099. Testar
src/kommunhandlingar/konvertering/bildyta.py med små ritade sidor."""

import random
import unittest

from PIL import Image, ImageDraw

from kommunhandlingar.konvertering import bildyta

B, H = 480, 680


def sida() -> Image.Image:
    return Image.new("RGB", (B, H), "white")


def foto(bild: Image.Image, ruta: tuple[int, int, int, int]) -> None:
    """En mjuk färgövergång, som ett foto eller en karta."""
    rita = ImageDraw.Draw(bild)
    x0, y0, x1, y1 = ruta
    for y in range(y0, y1):
        andel = (y - y0) / (y1 - y0)
        rita.line((x0, y, x1, y), fill=(40, int(80 + 120 * andel), 160))


def brus() -> Image.Image:
    slump = random.Random(1)
    liten = Image.new("L", (60, 85))
    liten.putdata([slump.randint(0, 255) for _ in range(60 * 85)])
    return liten.resize((B, H), Image.NEAREST).convert("RGB")


class TestBildyta(unittest.TestCase):
    def test_vit_sida_har_ingen_bildyta(self):
        yta = bildyta.storsta(sida(), [])
        self.assertEqual((yta.andel, yta.ruta), (0.0, None))

    def test_helsidesfoto_ar_en_jamn_bildyta(self):
        bild = sida()
        foto(bild, (0, 0, B, H))
        yta = bildyta.storsta(bild, [])
        self.assertEqual(yta.andel, 1.0)
        self.assertTrue(yta.jamn)

    def test_halv_bild_ger_halva_sidan_och_dess_ruta(self):
        bild = sida()
        foto(bild, (0, H // 2, B, H))
        yta = bildyta.storsta(bild, [])
        self.assertAlmostEqual(yta.andel, 0.5, delta=0.03)
        self.assertEqual(yta.ruta[1] // 10, (H // 2) // 10)

    def test_brus_ar_ingen_jamn_yta(self):
        yta = bildyta.storsta(brus(), [])
        self.assertEqual(yta.andel, 1.0)
        self.assertFalse(yta.jamn)

    def test_rutor_med_lasta_ord_raknas_inte(self):
        bild = sida()
        foto(bild, (0, 0, B, H))
        yta = bildyta.storsta(bild, [(0, 0, B, H // 2)])
        self.assertAlmostEqual(yta.andel, 0.5, delta=0.03)

    def test_mork_andel(self):
        bild = sida()
        ImageDraw.Draw(bild).rectangle((0, 0, B // 10 - 1, H - 1), fill="black")
        self.assertAlmostEqual(bildyta.mork_andel(bild), 0.1, places=2)
        ljus = Image.new("RGB", (B, H), (220, 235, 245))
        self.assertEqual(bildyta.mork_andel(ljus), 0.0)
