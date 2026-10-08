"""Krav: K16 i docs/02-KRAV.md, ADR-0018. Kod: src/kommunhandlingar/behandla.py."""

import tempfile
import unittest
from pathlib import Path

from kommunhandlingar import frontmatter, pool
from kommunhandlingar.behandla import Steg2, behandla
from kommunhandlingar.kandidat import Kandidat
from tests.test_hamta import PDF, TID, Klient, kandidat

LUCKOR = "finns redan; arkivet fyller bara luckor"


class KapandeKlient(Klient):
    """Som Klient, men `kapad:<fixtur>` ger bara filens första halva."""

    def fil(self, url: str, mal: Path) -> None:
        if not self.filer[url].startswith("kapad:"):
            return super().fil(url, mal)
        self.anrop.append(url)
        innehall = (PDF / self.filer[url][6:]).read_bytes()
        mal.write_bytes(innehall[: len(innehall) // 2])


class TestArkivet(unittest.TestCase):
    def setUp(self):
        katalog = tempfile.TemporaryDirectory()
        self.addCleanup(katalog.cleanup)
        self.data = Path(katalog.name)
        self.klient = KapandeKlient()

    def kor(self, *kandidater: Kandidat, arkiv: bool = True) -> list[str]:
        steg = Steg2(
            self.data,
            "exempelby",
            pool.las(self.data, "exempelby"),
            self.klient,
            frozenset(k.kallnyckel for k in kandidater),
            lambda: TID,
            "kommunhandlingar 0.2.0",
            arkiv,
        )
        return [behandla(steg, k) for k in kandidater]

    def md(self, namn: str = "protokoll") -> Path:
        return self.data / "exempelby/ks/2025/2025-04-22" / f"{namn}.md"

    def falt(self, namn: str = "protokoll") -> dict[str, str]:
        return frontmatter.las(self.md(namn).read_text(encoding="utf-8"))

    def test_ett_dokument_i_poolen_andras_inte(self):
        self.klient.filer |= {"u1": "begransad.pdf", "w1": "sidor.pdf"}
        self.kor(kandidat("s:1", "u1"), arkiv=False)
        self.assertEqual(self.kor(kandidat("s:1", "w1")), [LUCKOR])
        self.assertEqual(self.klient.anrop, ["u1"])
        self.assertEqual(self.falt()["kalla_url"], "u1")

    def test_en_upptagen_plats_tas_inte(self):
        self.klient.filer |= {"u1": "begransad.pdf", "w2": "sidor.pdf"}
        self.kor(kandidat("s:1", "u1"), arkiv=False)
        self.assertEqual(self.kor(kandidat("s:2", "w2")), [LUCKOR])
        self.assertEqual(self.falt()["kallnyckel"], "s:1")
        self.assertEqual(len(list(self.data.rglob("*.md"))), 1)

    def test_tva_filer_ur_arkivet_pa_samma_plats_blir_tva_dokument(self):
        self.klient.filer |= {"w1": "begransad.pdf", "w2": "begransad.pdf"}
        resultat = self.kor(
            kandidat("s:1", "w1"), kandidat("s:2", "w2", filnamn="Protokoll § 5.pdf")
        )
        self.assertEqual(resultat, ["konverterad", "konverterad"])
        self.assertEqual(self.falt("protokoll-protokoll-5")["kallnyckel"], "s:2")

    def test_ett_ej_hamtat_fylls_ur_arkivet(self):
        self.klient.filer |= {"u1": "fel:robots", "w1": "begransad.pdf"}
        self.kor(kandidat("s:1", "u1"), arkiv=False)
        self.assertEqual(self.kor(kandidat("s:1", "w1")), ["konverterad"])
        self.assertEqual(self.falt()["kalla_url"], "w1")

    def test_kapad_kopia(self):
        self.klient.filer["w1"] = "kapad:begransad.pdf"
        self.assertEqual(self.kor(kandidat("s:1", "w1")), ["ej hämtad (kapad)"])
        falt = self.falt()
        self.assertEqual((falt["kvalitet"], falt["fel"]), ("ej-hamtad", "kapad"))
        self.assertEqual(
            self.kor(kandidat("s:1", "w1")), ["ej hämtad (kapad), oförändrad"]
        )

    def test_kapningen_provas_bara_for_arkivet(self):
        self.klient.filer["u1"] = "kapad:begransad.pdf"
        self.assertEqual(self.kor(kandidat("s:1", "u1"), arkiv=False), ["konverterad"])

    def test_den_levande_kallans_forsok_skrivs_inte_om(self):
        self.klient.filer |= {"u1": "fel:robots", "w1": "kapad:begransad.pdf"}
        self.kor(kandidat("s:1", "u1"), arkiv=False)
        fore = self.md().read_text()
        self.assertEqual(
            self.kor(kandidat("s:1", "w1")),
            ["ej hämtad (kapad), den levande källans försök orört"],
        )
        self.assertEqual(self.md().read_text(), fore)


if __name__ == "__main__":
    unittest.main()
