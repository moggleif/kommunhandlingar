"""Krav: K74 i docs/02-KRAV.md. Gränssnittet mot ett datarepo står under
"Gränssnittet mot datarepon" i docs/03-ARKITEKTUR.md."""

import importlib.util
import subprocess
import sys
import tempfile
import tomllib
import unittest
from importlib import resources
from pathlib import Path

from kommunhandlingar import hamta, upptack
from kommunhandlingar.konfiguration import las
from tests.test_konfiguration import FIXTURER, ROT


def kommando(modul: str, *argument: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", f"kommunhandlingar.{modul}", *argument],
        capture_output=True,
        text=True,
        check=False,
    )


class Kommandona(unittest.TestCase):
    def test_upptackten_tar_kommunfil_arbetskatalog_och_flaggorna(self):
        hjalp = kommando("upptack", "--help")
        self.assertEqual(hjalp.returncode, 0, hjalp.stderr)
        for del_ in ("kommunfil", "arbetskatalog", "--arkiv", "--start"):
            self.assertIn(del_, hjalp.stdout)

    def test_steg_2_tar_kommunfil_arbetskatalog_och_flaggorna(self):
        hjalp = kommando("hamta", "--help")
        self.assertEqual(hjalp.returncode, 0, hjalp.stderr)
        for del_ in ("kommunfil", "arbetskatalog", "--arkiv", "--start", "--del"):
            self.assertIn(del_, hjalp.stdout)

    def test_slutkoderna_som_nattkorningarna_laser(self):
        self.assertEqual(hamta.MER_I_NASTA_DEL, 4)
        self.assertEqual(upptack.KALLAN_STOPPADE, 3)

    def test_datakontrollen_tar_en_datakatalog(self):
        with tempfile.TemporaryDirectory() as data:
            kontroll = kommando("datakontroll", data)
        self.assertEqual(kontroll.returncode, 0, kontroll.stderr)

    def test_webbplatsen_ar_ett_kommando(self):
        self.assertIsNotNone(
            importlib.util.find_spec("kommunhandlingar.webbplats.__main__")
        )


class Importen(unittest.TestCase):
    def test_kommunfilen_lases_med_konfiguration_las(self):
        self.assertEqual(las(FIXTURER / "exempelby.toml").id, "exempelby")


class Paketdatat(unittest.TestCase):
    def test_varje_skript_och_stil_foljer_med_paketet(self):
        with (ROT / "pyproject.toml").open("rb") as fil:
            paketdata = tomllib.load(fil)["tool"]["setuptools"]["package-data"]
        monster = paketdata["kommunhandlingar.webbplats"]
        filer = resources.files("kommunhandlingar.webbplats").iterdir()
        skript = [Path(f.name) for f in filer if Path(f.name).suffix in (".js", ".css")]
        self.assertTrue(skript)
        for fil in skript:
            self.assertTrue(any(fil.match(m) for m in monster), fil)
