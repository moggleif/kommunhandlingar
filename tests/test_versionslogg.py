"""Krav: K53 i docs/02-KRAV.md, ADR-0077. Kod: src/kommunhandlingar/versionslogg.py
och hamta.py."""

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from unittest import mock

from kommunhandlingar import hamta, tidsbudget, versionslogg
from kommunhandlingar.pool import Pool
from tests.test_hamta import TID, Steg2Fall, kandidat

SEDD = datetime(2026, 11, 15, 1, 40, tzinfo=UTC)
P = "kungsbacka/ga/2026/2026-10-22/protokoll.md"


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


def pool(f: dict[str, str]) -> Pool:
    resultat = Pool()
    resultat.satt(PurePosixPath(P), f)
    return resultat


def nya(fore: dict[str, str] | None, efter: dict[str, str]) -> list[list[str]]:
    versioner = versionslogg.versioner(pool(fore)) if fore else {}
    return versionslogg.nya(versioner, pool(efter), SEDD)


class TestNya(unittest.TestCase):
    def test_inget_nytt_ger_inga_rader(self):
        self.assertEqual(nya(falt("s:1", "u/1"), falt("s:1", "u/1")), [])

    def test_nytt_dokument_ger_en_rad(self):
        rad = ["2026-11-15T01:40:00+00:00", "ga", "2026-10-22", "protokoll"]
        rad += ["s:1", "u/1", "abc", P]
        self.assertEqual(nya(None, falt("s:1", "u/1")), [rad])

    def test_ny_adress_for_samma_kallnyckel_ger_en_rad(self):
        [rad] = nya(falt("s:1", "u/1"), falt("s:1", "u/2", "def"))
        self.assertEqual(rad[5:7], ["u/2", "def"])

    def test_ny_sha256_under_samma_adress_ger_en_rad(self):
        [rad] = nya(falt("s:1", "u/1", "null"), falt("s:1", "u/1", "def"))
        self.assertEqual(rad[5:7], ["u/1", "def"])

    def test_ej_hamtad_har_tom_sha256(self):
        [rad] = nya(None, falt("s:1", "u/1", "null"))
        self.assertEqual(rad[6], "")

    def test_ny_kallnyckel_pa_samma_plats_ger_en_rad(self):
        [rad] = nya(falt("s:1", "u/1"), falt("s:2", "u/9"))
        self.assertEqual(rad[4], "s:2")


class TestSkriv(unittest.TestCase):
    def setUp(self):
        katalog = tempfile.TemporaryDirectory()
        self.addCleanup(katalog.cleanup)
        self.fil = Path(katalog.name) / "versioner" / "exempelby.csv"

    def test_inga_rader_skriver_ingen_fil(self):
        versionslogg.skriv(self.fil, [])
        self.assertFalse(self.fil.exists())

    def test_rubrik_en_gang_och_rader_laggs_till_sist(self):
        versionslogg.skriv(self.fil, [["a", "b,c"]])
        versionslogg.skriv(self.fil, [["d", "e"]])
        rubrik = "sedd,organ,datum,typ,kallnyckel,kalla_url,sha256,dokument"
        text = self.fil.read_text(encoding="utf-8")
        self.assertEqual(text, f'{rubrik}\na,"b,c"\nd,e\n')


class TestSteg2(Steg2Fall):
    """Steg 2 med en källa som inte går att nå, så att inget konverteras."""

    def kor_med_logg(self, logg: Path | None, *kandidater) -> None:
        mjuk = tidsbudget.mjuk_grans(None)
        hamta.steg2(self.steg(list(kandidater)), list(kandidater), mjuk, logg)

    def test_levande_steg_2_loggar_det_nya(self):
        self.klient.filer["u1"] = "fel:404"
        logg = self.data / "logg.csv"
        self.kor_med_logg(logg, kandidat("s:1", "u1"))
        rader = logg.read_text(encoding="utf-8").splitlines()
        dokument = "exempelby/ks/2025/2025-04-22/protokoll.md"
        rad = f"{TID.isoformat()},ks,2025-04-22,protokoll,s:1,u1,,{dokument}"
        self.assertEqual(rader[1], rad)

    def test_samma_adress_igen_ger_ingen_rad(self):
        self.klient.filer["u1"] = "fel:404"
        logg = self.data / "logg.csv"
        self.kor_med_logg(logg, kandidat("s:1", "u1"))
        self.kor_med_logg(logg, kandidat("s:1", "u1"))
        self.assertEqual(len(logg.read_text(encoding="utf-8").splitlines()), 2)

    def test_arkivet_skriver_ingen_logg(self):
        self.klient.filer["u1"] = "fel:404"
        self.kor_med_logg(None, kandidat("s:1", "u1"))
        self.assertEqual(sorted(p.name for p in self.data.iterdir()), ["exempelby"])

    def test_loggen_skrivs_ocksa_nar_steg_2_stoppas(self):
        self.klient.filer["u1"] = "fel:404"
        logg = self.data / "logg.csv"
        k1, k2 = kandidat("s:1", "u1"), kandidat("s:2", "u2", "kallelse", "K.pdf")
        riktig = hamta.behandla

        def forst_riktig_sedan_fel(steg, k):
            if k is k2:
                raise RuntimeError
            return riktig(steg, k)

        fel = mock.patch.object(hamta, "behandla", forst_riktig_sedan_fel)
        with fel, self.assertRaises(RuntimeError):
            self.kor_med_logg(logg, k1, k2)
        self.assertEqual(len(logg.read_text(encoding="utf-8").splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
