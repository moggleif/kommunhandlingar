"""Krav: K11 och K52, ADR-0006 och ADR-0075.
Kod: src/kommunhandlingar/tidsbudget.py, behandla.py och hamta.py."""

import os
import signal
import tempfile
import time
import unittest
from datetime import timedelta
from pathlib import Path
from unittest import mock

from kommunhandlingar import frontmatter, pool, tidsbudget
from kommunhandlingar.behandla import Steg2
from kommunhandlingar.datakontroll import fel_i
from kommunhandlingar.hamta import kor
from kommunhandlingar.konvertering import dokument
from kommunhandlingar.tidsbudget import Dokumentgrans, Tidsgrans, avbryt, utan_avbrott
from tests.test_hamta import PDF, TID, Klient, kandidat


class Avbrytande(Klient):
    """Som om den hårda gränsen nås medan den andra filen hämtas."""

    def fil(self, url: str, mal: Path) -> None:
        super().fil(url, mal)
        if len(self.anrop) == 2:
            raise Tidsgrans


class TestBudgeten(unittest.TestCase):
    def setUp(self):
        katalog = tempfile.TemporaryDirectory()
        self.addCleanup(katalog.cleanup)
        self.data = Path(katalog.name)
        self.klient = Avbrytande()
        self.klient.filer |= {f"u{n}": "kort.pdf" for n in range(1, 5)}
        self.klient.filer["u1"] = "fel:http-404"
        self.kandidater = [
            kandidat(f"s:{n}", f"u{n}", filnamn=f"{n}.pdf") for n in range(1, 5)
        ]

    def kor(self, mjuk):
        steg = Steg2(
            self.data,
            "exempelby",
            pool.las(self.data, "exempelby"),
            self.klient,
            frozenset(k.kallnyckel for k in self.kandidater),
            lambda: TID,
            "kommunhandlingar 0.1.0",
        )
        return kor(steg, self.kandidater, mjuk)

    def test_inget_nytt_dokument_startar_efter_den_mjuka_gransen(self):
        utfall = self.kor(TID)
        self.assertEqual(utfall, {"väntar på nästa körning": 4})
        self.assertEqual(self.klient.anrop, [])

    def test_dokumentet_vid_den_harda_gransen_laggs_at_sidan(self):
        utfall = self.kor(TID + timedelta(hours=1))
        self.assertEqual(
            utfall,
            {
                "ej hämtad (http-404)": 1,
                "lagd åt sidan vid tidsgränsen": 1,
                "väntar på nästa körning": 2,
            },
        )
        filer = [p.name for p in self.data.rglob("*") if p.is_file()]
        self.assertEqual(filer, ["protokoll.md"])
        self.assertEqual(fel_i(self.data), [])

    def test_konverteringen_fangar_inte_tidsgransen(self):
        self.klient.filer["u1"] = "kort.pdf"
        with mock.patch(
            "kommunhandlingar.konvertering.dokument.las_sidor", side_effect=Tidsgrans
        ):
            utfall = self.kor(TID + timedelta(hours=1))
        self.assertEqual(utfall["lagd åt sidan vid tidsgränsen"], 1)
        self.assertEqual(list(self.data.rglob("*")), [])


class TestGranserna(unittest.TestCase):
    def setUp(self):
        gammal = signal.getsignal(signal.SIGALRM)
        self.addCleanup(signal.signal, signal.SIGALRM, gammal)
        self.addCleanup(tidsbudget.stoppa)

    def test_mjuk_grans(self):
        self.assertEqual(tidsbudget.mjuk_grans(TID), TID + timedelta(hours=5))
        self.assertGreater(tidsbudget.mjuk_grans(None), TID + timedelta(days=9999))

    def test_hard_grans_raknas_fran_jobbets_start(self):
        nu = TID + timedelta(hours=1)
        tidsbudget.starta_hard_grans(TID, nu)
        self.assertEqual(signal.alarm(0), 4 * 3600 + 30 * 60)

    def test_passerad_hard_grans_avbryter_genast(self):
        tidsbudget.starta_hard_grans(TID, TID + timedelta(hours=6))
        self.assertEqual(signal.alarm(0), 1)


class TestSkrivningenAvbrytsInte(unittest.TestCase):
    def setUp(self):
        gammal = signal.signal(signal.SIGALRM, avbryt)
        self.addCleanup(signal.signal, signal.SIGALRM, gammal)

    def test_signalen_avbryter_utanfor_skrivningen(self):
        with self.assertRaises(Tidsgrans):
            os.kill(os.getpid(), signal.SIGALRM)

    def test_signalen_under_skrivningen_tas_bort(self):
        with utan_avbrott():
            os.kill(os.getpid(), signal.SIGALRM)
            skrivet = True
        self.assertTrue(skrivet)
        self.assertNotIn(signal.SIGALRM, signal.sigpending())


class TestDokumentetsGrans(unittest.TestCase):
    def setUp(self):
        katalog = tempfile.TemporaryDirectory()
        self.addCleanup(katalog.cleanup)
        self.data = Path(katalog.name)
        self.klient = Klient()
        self.klient.filer |= {"u1": "kort.pdf", "u2": "kort-begransad.pdf"}
        self.kandidater = [
            kandidat("s:1", "u1"),
            kandidat("s:2", "u2", "kallelse", "2.pdf"),
        ]

    def kor(self, version: str = "kommunhandlingar 0.1.0"):
        steg = Steg2(
            self.data,
            "exempelby",
            pool.las(self.data, "exempelby"),
            self.klient,
            frozenset(k.kallnyckel for k in self.kandidater),
            lambda: TID,
            version,
            omkonvertera=True,
        )
        return kor(steg, self.kandidater, TID + timedelta(hours=1))

    def falt(self, namn: str) -> dict[str, str]:
        md = self.data / "exempelby/ks/2025/2025-04-22" / f"{namn}.md"
        return frontmatter.las(md.read_text(encoding="utf-8"))

    def test_dokumentet_blir_ej_konverterat_och_nasta_tas(self):
        las_sidor = dokument.las_sidor

        def forsta_tar_for_lang_tid(pdf):
            if pdf.read_bytes() == (PDF / "kort.pdf").read_bytes():
                raise Dokumentgrans
            return las_sidor(pdf)

        with mock.patch(
            "kommunhandlingar.konvertering.dokument.las_sidor",
            side_effect=forsta_tar_for_lang_tid,
        ):
            utfall = self.kor()
        self.assertEqual(utfall, {"ej konverterad (tidsgrans)": 1, "konverterad": 1})
        falt = self.falt("protokoll")
        self.assertEqual(
            (falt["kvalitet"], falt["fel"]), ("ej-konverterad", "tidsgrans")
        )
        self.assertEqual(self.falt("kallelse")["fel"], "null")
        self.assertEqual(fel_i(self.data), [])

    def test_nasta_korning_tar_inte_dokumentet_igen(self):
        with mock.patch(
            "kommunhandlingar.konvertering.dokument.las_sidor",
            side_effect=Dokumentgrans,
        ):
            self.kor()
        self.assertEqual(self.kor(), {"oförändrad": 2})

    def test_en_omkonvertering_vid_gransen_lamnar_texten_orord(self):
        self.kor()
        md = self.data / "exempelby/ks/2025/2025-04-22/protokoll.md"
        fore = md.read_text(encoding="utf-8")
        with mock.patch(
            "kommunhandlingar.konvertering.dokument.las_sidor",
            side_effect=Dokumentgrans,
        ):
            utfall = self.kor("kommunhandlingar 0.2.0")
        orord = "ej konverterad (tidsgrans), fullständig .md orörd"
        self.assertEqual(utfall, {orord: 2})
        self.assertEqual(md.read_text(encoding="utf-8"), fore)

    def test_en_ny_version_vid_gransen_skrivs_over(self):
        self.kor()
        self.klient.filer["u1"] = "kort-begransad.pdf"
        with mock.patch(
            "kommunhandlingar.konvertering.dokument.las_sidor",
            side_effect=Dokumentgrans,
        ):
            utfall = self.kor("kommunhandlingar 0.2.0")
        orord = "ej konverterad (tidsgrans), fullständig .md orörd"
        self.assertEqual(utfall, {"ej konverterad (tidsgrans)": 1, orord: 1})
        self.assertEqual(self.falt("protokoll")["fel"], "tidsgrans")


class TestHogst(unittest.TestCase):
    def setUp(self):
        gammal = signal.signal(signal.SIGALRM, avbryt)
        self.addCleanup(signal.signal, signal.SIGALRM, gammal)
        self.addCleanup(tidsbudget.stoppa)

    def test_gransen_avbryter_blocket(self):
        with self.assertRaises(Dokumentgrans), tidsbudget.hogst(1):
            time.sleep(3)
        self.assertEqual(signal.alarm(0), 0)
        self.assertEqual(signal.getsignal(signal.SIGALRM), avbryt)

    def test_den_harda_gransen_stalls_tillbaka(self):
        signal.setitimer(signal.ITIMER_REAL, 3600)
        with tidsbudget.hogst(60):
            self.assertAlmostEqual(signal.getitimer(signal.ITIMER_REAL)[0], 60, 2)
            time.sleep(0.5)
        kvar = signal.getitimer(signal.ITIMER_REAL)[0]
        self.assertAlmostEqual(kvar, 3599.5, delta=0.2)

    def test_korta_konverteringar_drar_av_sin_tid(self):
        signal.setitimer(signal.ITIMER_REAL, 3600)
        for _ in range(10):
            with tidsbudget.hogst(60):
                time.sleep(0.1)
        kvar = signal.getitimer(signal.ITIMER_REAL)[0]
        self.assertAlmostEqual(kvar, 3599, delta=0.2)

    def test_den_harda_gransen_gar_fore(self):
        signal.alarm(30)
        with tidsbudget.hogst(60):
            self.assertEqual(signal.getsignal(signal.SIGALRM), avbryt)
        self.assertLessEqual(signal.alarm(0), 30)


if __name__ == "__main__":
    unittest.main()
