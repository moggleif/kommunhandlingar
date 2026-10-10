"""Krav: K11, ADR-0006 och ADR-0009.
Kod: src/kommunhandlingar/datakontroll.py och datakontroll_tabeller.py."""

import shutil
import tempfile
import unittest
from pathlib import Path

from kommunhandlingar import frontmatter, pool
from kommunhandlingar.behandla import Steg2, behandla
from kommunhandlingar.datakontroll import fel_i
from tests.test_hamta import TID, Klient, kandidat

DOKUMENT = "exempelby/ks/2025/2025-04-22/protokoll.md"
EJ_HAMTAD = "exempelby/ks/2025/2025-04-22/kallelse.md"
PERSONUPPGIFTER = (
    "personuppgifter som ska maskas (python -m kommunhandlingar.maska_poolen)"
)


def pool_med_tva_dokument(data: Path) -> None:
    klient = Klient()
    klient.filer |= {"u1": "sidor.pdf", "u2": "fel:http-404"}
    kandidater = (kandidat("s:1", "u1"), kandidat("s:2", "u2", typ="kallelse"))
    steg = Steg2(
        data,
        "exempelby",
        pool.las(data, "exempelby"),
        klient,
        frozenset(k.kallnyckel for k in kandidater),
        lambda: TID,
        "kommunhandlingar 0.1.0",
    )
    for k in kandidater:
        behandla(steg, k)


class Pool(unittest.TestCase):
    """En kopia av samma pool för varje test; den konverteras en gång."""

    @classmethod
    def setUpClass(cls):
        katalog = tempfile.TemporaryDirectory()
        cls.addClassCleanup(katalog.cleanup)
        cls.facit = Path(katalog.name)
        pool_med_tva_dokument(cls.facit)

    def setUp(self):
        katalog = tempfile.TemporaryDirectory()
        self.addCleanup(katalog.cleanup)
        self.data = Path(katalog.name) / "data"
        shutil.copytree(self.facit, self.data)

    def fel(self) -> list[str]:
        return fel_i(self.data)

    def andra(self, relativ: str, **falt) -> None:
        md = self.data / relativ
        _, huvud, kropp = md.read_text(encoding="utf-8").split("---\n", 2)
        nya = frontmatter.las(f"---\n{huvud}---\n") | falt
        md.write_text(frontmatter.skriv(nya) + kropp, encoding="utf-8")


class TestDatakontroll(Pool):
    def test_poolen_som_steg_2_skriver_den_gar_igenom(self):
        self.assertEqual(self.fel(), [])
        self.assertTrue((self.data / DOKUMENT).with_suffix(".tabeller").is_dir())

    def test_tom_eller_saknad_data_gar_igenom(self):
        self.assertEqual(fel_i(self.data / "finns-inte"), [])

    def test_temporara_filer(self):
        (self.data / (DOKUMENT + ".tmp")).write_text("x")
        ny = self.data / DOKUMENT.replace(".md", ".tabeller.ny")
        ny.mkdir()
        (ny / "1-1.csv").write_text("a\n")
        self.assertEqual(len(self.fel()), 2)
        self.assertIn("oväntad fil", self.fel()[0])

    def test_front_matter_som_inte_gar_att_lasa(self):
        (self.data / DOKUMENT).write_text("ingen front matter\n")
        self.assertIn(f"{DOKUMENT}: front matter går inte att läsa", self.fel())

    def test_falt_som_saknas(self):
        md = self.data / DOKUMENT
        md.write_text(md.read_text().replace("arenden: null\n", ""))
        self.assertEqual(
            self.fel(),
            [f"{DOKUMENT}: front matter har inte schemats fält i schemats ordning"],
        )

    def test_null_dar_det_aldrig_far_vara_null(self):
        self.andra(DOKUMENT, kalla_url="null")
        self.assertEqual(self.fel(), [f"{DOKUMENT}: kalla_url är null"])

    def test_okanda_varden(self):
        self.andra(EJ_HAMTAD, typ="protokol", kvalitet="bra")
        self.assertIn(f"{EJ_HAMTAD}: okänd typ 'protokol'", self.fel())
        self.assertIn(f"{EJ_HAMTAD}: okänd kvalitet 'bra'", self.fel())

    def test_sokvagen_stammer_inte_med_front_matter(self):
        self.andra(EJ_HAMTAD, organ="kf")
        vantad = "exempelby/kf/2025/2025-04-22/kallelse.md"
        self.assertEqual(self.fel(), [f"{EJ_HAMTAD}: sökvägen borde vara {vantad}"])

    def test_lopnr_och_namn_i_sokvagen(self):
        self.andra(EJ_HAMTAD, lopnr="2", namn="extra")
        vantad = "exempelby/ks/2025/2025-04-22-2/kallelse-extra.md"
        self.assertEqual(self.fel(), [f"{EJ_HAMTAD}: sökvägen borde vara {vantad}"])

    def test_ej_hamtad_har_inga_originalfalt(self):
        self.andra(EJ_HAMTAD, sha256="abc", fel="null")
        self.assertEqual(
            self.fel(),
            [f"{EJ_HAMTAD}: sha256 ska vara null", f"{EJ_HAMTAD}: fel saknas"],
        )

    def test_ocr_sida_maste_vara_obekraftad(self):
        self.andra(DOKUMENT, tal_obekraftade="[5, 6, 7, 9]")
        self.assertEqual(
            self.fel(),
            [f"{DOKUMENT}: sidan 11 är ocr men står inte i tal_obekraftade"],
        )

    def test_antalet_sidor(self):
        self.andra(DOKUMENT, sidor="12")
        self.assertEqual(
            self.fel(), [f"{DOKUMENT}: sidor stämmer inte med kvalitet_per_sida"]
        )


class TestTabellkontroll(Pool):
    def setUp(self):
        super().setUp()
        self.katalog = (self.data / DOKUMENT).with_suffix(".tabeller")
        self.relativ = DOKUMENT.replace(".md", ".tabeller")

    def test_personnummer_i_texten(self):
        md = self.data / DOKUMENT
        md.write_text(md.read_text(encoding="utf-8") + "Sökanden 121212-1212\n")
        self.assertEqual(self.fel(), [f"{DOKUMENT}: {PERSONUPPGIFTER}"])

    def test_namn(self):
        (self.katalog / "02-1.csv").write_text("a\n")
        namn = "<sida>-<nr>.csv eller <sida>-<nr>.tolkad.csv"
        self.assertEqual(self.fel(), [f"{self.relativ}/02-1.csv: heter inte {namn}"])

    def test_lucka_i_numren(self):
        (self.katalog / "2-3.csv").write_text("a\n")
        self.assertEqual(self.fel(), [f"{self.relativ}/2-3.csv: 2-2.csv saknas"])

    def test_sidan_ar_inte_last_ur_textlagret(self):
        (self.katalog / "11-1.csv").write_text("a\n")
        self.assertEqual(
            self.fel(),
            [
                f"{self.relativ}/11-1.csv: sidan 11 finns inte "
                "eller är inte läst ur textlagret"
            ],
        )

    def test_katalog_utan_md(self):
        (self.data / DOKUMENT).unlink()
        self.assertIn(
            f"{self.relativ}/2-1.csv: tabellkatalogen har ingen protokoll.md",
            self.fel(),
        )

    def test_format(self):
        fil = self.katalog / "2-1.csv"
        for innehall, fel in (
            (b"\xef\xbb\xbfa,b\n", "börjar med BOM"),
            (b"a,b\r\nc,d\r\n", "radslut CRLF"),
            (b"a,b\nc\n", "raderna har olika många fält"),
        ):
            with self.subTest(fel=fel):
                fil.write_bytes(innehall)
                self.assertEqual(self.fel(), [f"{self.relativ}/2-1.csv: {fel}"])

    def test_personnummer_i_en_tabell(self):
        (self.katalog / "2-1.csv").write_text("Roll,Nummer\nSökanden,121212-1212\n")
        self.assertEqual(
            self.fel(),
            [f"{self.relativ}/2-1.csv: {PERSONUPPGIFTER}"],
        )

    def test_csv_utan_personuppgifter_i_annan_form(self):
        (self.katalog / "2-1.csv").write_text('"Roll","Antal"\nLedamot,3')
        self.assertEqual(self.fel(), [])

    def test_inte_utf_8(self):
        (self.katalog / "2-1.csv").write_bytes(b"\xff\n")
        self.assertIn("inte CSV i UTF-8", self.fel()[0])


if __name__ == "__main__":
    unittest.main()
