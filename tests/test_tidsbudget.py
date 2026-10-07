"""Krav: K11, ADR-0006. Kod: src/kommunhandlingar/tidsbudget.py och hamta.py."""

import os
import signal
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest import mock

from kommunhandlingar import pool
from kommunhandlingar.behandla import Steg2
from kommunhandlingar.datakontroll import fel_i
from kommunhandlingar.hamta import kor
from kommunhandlingar.tidsbudget import Tidsgrans, avbryt, utan_avbrott
from tests.test_hamta import TID, Klient, kandidat


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
        self.klient.filer |= {f"u{n}": "sidor.pdf" for n in range(1, 5)}
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
        self.klient.filer["u1"] = "sidor.pdf"
        with mock.patch(
            "kommunhandlingar.konvertering.dokument.las_sidor", side_effect=Tidsgrans
        ):
            utfall = self.kor(TID + timedelta(hours=1))
        self.assertEqual(utfall["lagd åt sidan vid tidsgränsen"], 1)
        self.assertEqual(list(self.data.rglob("*")), [])


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


if __name__ == "__main__":
    unittest.main()
