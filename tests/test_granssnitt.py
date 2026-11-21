"""Krav: K74 i docs/02-KRAV.md. Gränssnittet mot ett datarepo står under
"Gränssnittet mot datarepon" i docs/03-ARKITEKTUR.md."""

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from datetime import UTC, datetime
from importlib import resources
from pathlib import Path
from unittest import mock

from kommunhandlingar import hamta, upptack
from kommunhandlingar.konfiguration import las
from tests.test_konfiguration import FIXTURER, ROT

START = "1795284000"  # som nattkörningarnas `date +%s`


def tolkat(modul, *argument: str):
    with mock.patch.object(sys, "argv", ["prog", *argument]):
        return modul.argument()


class Kommandona(unittest.TestCase):
    def test_upptackten_som_nattkorningarna_anropar_den(self):
        arg = tolkat(upptack, "kommuner/k.toml", "/arbete", "--arkiv", "--start", START)
        self.assertEqual(arg.kommunfil, Path("kommuner/k.toml"))
        self.assertEqual(arg.arbetskatalog, Path("/arbete"))
        self.assertTrue(arg.arkiv)
        self.assertEqual(arg.start, datetime.fromtimestamp(int(START), UTC))

    def test_steg_2_som_nattkorningarna_anropar_det(self):
        arg = tolkat(
            hamta, "kommuner/k.toml", "/arbete", "--start", START, "--del", "15",
            "--utan-omkonvertering", "--arkiv",
        )  # fmt: skip
        self.assertEqual(arg.kommunfil, Path("kommuner/k.toml"))
        self.assertEqual(arg.arbetskatalog, Path("/arbete"))
        self.assertEqual(arg.start, datetime.fromtimestamp(int(START), UTC))
        self.assertEqual(arg.del_, 15)
        self.assertTrue(arg.utan_omkonvertering)
        self.assertTrue(arg.arkiv)

    def test_slutkoderna_som_nattkorningarna_laser(self):
        self.assertEqual(hamta.MER_I_NASTA_DEL, 4)
        self.assertEqual(upptack.KALLAN_STOPPADE, 3)

    def test_datakontrollen_provar_katalogen_den_far(self):
        with tempfile.TemporaryDirectory() as data:
            (Path(data) / "exempelby").mkdir()
            (Path(data) / "exempelby" / "kvar.tmp").write_text("")
            kontroll = subprocess.run(
                [sys.executable, "-m", "kommunhandlingar.datakontroll", data],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(kontroll.returncode, 1, kontroll.stderr)
        self.assertIn("kvar.tmp", kontroll.stdout)

    def test_webbplatsen_ar_ett_kommando(self):
        # Modulen bygger när den importeras; argumenten låses när den får en
        # main (#356).
        spec = importlib.util.find_spec("kommunhandlingar.webbplats.__main__")
        self.assertIsNotNone(spec)


class Katalogerna(unittest.TestCase):
    def test_steg_2_laser_hamtningen_och_poolen_bredvid_kommunfilens_katalog(self):
        with tempfile.TemporaryDirectory() as katalog:
            rot = Path(katalog).resolve()
            (rot / "kommuner").mkdir()
            kommunfil = rot / "kommuner" / "exempelby.toml"
            shutil.copy(FIXTURER / "exempelby.toml", kommunfil)
            shutil.copy(ROT / "hamtning.toml", rot / "hamtning.toml")
            arg = tolkat(hamta, str(kommunfil), "/arbete")
            steg = hamta.bygg_steg(arg, las(kommunfil), [])
        self.assertEqual(steg.data, rot / "data")


class Paketdatat(unittest.TestCase):
    def test_varje_fil_utom_koden_foljer_med_paketet(self):
        with (ROT / "pyproject.toml").open("rb") as fil:
            paketdata = tomllib.load(fil)["tool"]["setuptools"]["package-data"]
        monster = paketdata["kommunhandlingar.webbplats"]
        paket = Path(str(resources.files("kommunhandlingar.webbplats")))
        medtagna = {f for m in monster for f in paket.glob(m)}
        filer = {
            f
            for f in paket.rglob("*")
            if f.is_file() and f.suffix not in (".py", ".pyc")
        }
        self.assertTrue(filer)
        self.assertEqual(filer - medtagna, set())
