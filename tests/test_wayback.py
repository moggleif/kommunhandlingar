"""Krav: K16 i docs/02-KRAV.md, ADR-0018.
Kod: src/kommunhandlingar/adaptrar/wayback.py."""

import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from kommunhandlingar.adaptrar.wayback import (
    CDX,
    Kopia,
    adress,
    fraga,
    kapad,
    sista_per_ar,
)
from kommunhandlingar.fel import Hamtfel


class Klient:
    def __init__(self, svar: str):
        self.svar, self.anrop = svar, []

    def text(self, url: str) -> str:
        self.anrop.append(url)
        return self.svar


class TestCdx(unittest.TestCase):
    def test_fragan_och_raderna(self):
        klient = Klient(
            '[["timestamp","original","length"],'
            '["20230101000000","https://k.se/download/18.a/1/P.pdf","812"]]'
        )
        kopior = fraga(klient, "k.se/download/", "application/pdf", prefix=True)
        self.assertEqual(
            kopior, [Kopia("20230101000000", "https://k.se/download/18.a/1/P.pdf", 812)]
        )
        url = urlsplit(klient.anrop[0])
        self.assertEqual(f"{url.scheme}://{url.netloc}{url.path}", CDX)
        self.assertEqual(
            parse_qs(url.query),
            {
                "url": ["k.se/download/"],
                "output": ["json"],
                "fl": ["timestamp,original,length"],
                "filter": ["statuscode:200", "mimetype:application/pdf"],
                "matchType": ["prefix"],
            },
        )

    def test_svar_som_inte_ar_json(self):
        with self.assertRaisesRegex(Hamtfel, "arkivets lista för k.se/a: inte-json"):
            fraga(Klient("<html>Temporarily Offline</html>"), "k.se/a", "text/html")

    def test_fel_far_fragans_adress(self):
        class Fel:
            def text(self, url):
                raise Hamtfel("http-503")

        with self.assertRaisesRegex(Hamtfel, "arkivets lista för k.se/a: http-503"):
            fraga(Fel(), "k.se/a", "text/html")

    def test_inga_kopior(self):
        self.assertEqual(fraga(Klient("\n"), "k.se/a", "text/html"), [])
        self.assertEqual(fraga(Klient("[]"), "k.se/a", "text/html"), [])

    def test_kopians_adress(self):
        kopia = Kopia("20230101000000", "https://k.se/a.pdf", 1)
        self.assertEqual(
            adress(kopia),
            "https://web.archive.org/web/20230101000000id_/https://k.se/a.pdf",
        )

    def test_sista_ogonblicksbilden_per_ar_nyast_forst(self):
        kopior = [
            Kopia(tid, "a", 1)
            for tid in ("20221201", "20220301", "20231105", "20230102", "20240601")
        ]
        self.assertEqual(
            [k.tidsstampel for k in sista_per_ar(kopior)],
            ["20240601", "20231105", "20221201"],
        )


class TestKapad(unittest.TestCase):
    def kapad(self, innehall: bytes) -> bool:
        with tempfile.TemporaryDirectory() as katalog:
            pdf = Path(katalog) / "a.pdf"
            pdf.write_bytes(innehall)
            return kapad(pdf)

    def test_utan_slut_ar_kapad(self):
        self.assertTrue(self.kapad(b"%PDF-1.7\n" + b"x" * 5000))
        self.assertTrue(self.kapad(b"%%EOF" + b"x" * 1100))

    def test_med_slut_ar_hel(self):
        self.assertFalse(self.kapad(b"%PDF-1.7\n" + b"x" * 5000 + b"%%EOF"))
        self.assertFalse(self.kapad(b"%PDF-1.7\n" + b"x" * 5000 + b"%%EOF\r\n\x00\x00"))
        self.assertFalse(self.kapad(b"%%EOF"))
