"""Krav: K53 i docs/02-KRAV.md, ADR-0077. Kod: src/kommunhandlingar/versioner.py."""

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

from kommunhandlingar import versioner
from kommunhandlingar.pool import Pool

SEDD = datetime(2026, 11, 15, 1, 40, tzinfo=UTC)


def falt(nyckel: str, url: str, sha256: str = "abc") -> dict[str, str]:
    return {
        "organ": "ga",
        "datum": "2026-10-22",
        "typ": "protokoll",
        "kallnyckel": nyckel,
        "tidigare_kallnycklar": "[]",
        "kalla_url": url,
        "sha256": sha256,
    }


def pool(*dokument: tuple[str, dict[str, str]]) -> Pool:
    resultat = Pool()
    for sokvag, f in dokument:
        resultat.satt(PurePosixPath(sokvag), f)
    return resultat


P = "kungsbacka/ga/2026/2026-10-22/protokoll.md"


class TestNya(unittest.TestCase):
    def test_inget_nytt_ger_inga_rader(self):
        fore = pool((P, falt("s:1", "u/1")))
        self.assertEqual(versioner.nya(versioner.adresser(fore), fore, SEDD), [])

    def test_nytt_dokument_ger_en_rad(self):
        efter = pool((P, falt("s:1", "u/1")))
        rad = ["2026-11-15T01:40:00+00:00", "ga", "2026-10-22", "protokoll"]
        rad += ["s:1", "u/1", "abc", P]
        self.assertEqual(versioner.nya({}, efter, SEDD), [rad])

    def test_ny_adress_for_samma_kallnyckel_ger_en_rad(self):
        fore = versioner.adresser(pool((P, falt("s:1", "u/1"))))
        efter = pool((P, falt("s:1", "u/2", "def")))
        [rad] = versioner.nya(fore, efter, SEDD)
        self.assertEqual(rad[5:7], ["u/2", "def"])

    def test_ej_hamtad_har_tom_sha256(self):
        efter = pool((P, falt("s:1", "u/1", "null")))
        [rad] = versioner.nya({}, efter, SEDD)
        self.assertEqual(rad[6], "")

    def test_ny_kallnyckel_pa_samma_plats_ger_en_rad(self):
        fore = versioner.adresser(pool((P, falt("s:1", "u/1"))))
        efter = pool((P, falt("s:2", "u/9")))
        [rad] = versioner.nya(fore, efter, SEDD)
        self.assertEqual(rad[4], "s:2")


class TestSkriv(unittest.TestCase):
    def setUp(self):
        katalog = tempfile.TemporaryDirectory()
        self.addCleanup(katalog.cleanup)
        self.fil = Path(katalog.name) / "versioner" / "exempelby.csv"

    def test_inga_rader_skriver_ingen_fil(self):
        versioner.skriv(self.fil, [])
        self.assertFalse(self.fil.exists())

    def test_rubrik_en_gang_och_rader_laggs_till_sist(self):
        versioner.skriv(self.fil, [["a", "b,c"]])
        versioner.skriv(self.fil, [["d", "e"]])
        rubrik = "sedd,organ,datum,typ,kallnyckel,kalla_url,sha256,dokument"
        text = self.fil.read_text(encoding="utf-8")
        self.assertEqual(text, f'{rubrik}\na,"b,c"\nd,e\n')


if __name__ == "__main__":
    unittest.main()
