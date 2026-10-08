"""Krav: K8, K9 och K13, ADR-0019.
Kod: src/kommunhandlingar/behandla.py och hamta.py."""

from kommunhandlingar.hamta import ordna
from tests.test_hamta import Steg2Fall, kandidat


class TestOmkonvertering(Steg2Fall):
    def test_annan_version_konverteras_om(self):
        self.klient.filer["u1"] = "sidor.pdf"
        self.kor(kandidat("s:1", "u1"), version="kommunhandlingar 0.1.0")
        self.assertEqual(self.kor(kandidat("s:1", "u1")), ["konverterad om"])
        self.assertEqual(self.klient.anrop, ["u1", "u1"])
        self.assertTrue(self.falt()["pipeline"].startswith("kommunhandlingar 0.2.0 /"))
        self.assertEqual(self.falt()["figurer"], "[17]")
        self.assertEqual(self.kor(kandidat("s:1", "u1")), ["oförändrad"])

    def test_annan_version_som_inte_gar_att_hamta_star_kvar(self):
        self.klient.filer["u1"] = "sidor.pdf"
        self.kor(kandidat("s:1", "u1"), version="kommunhandlingar 0.1.0")
        fore = self.md().read_text()
        self.klient.filer["u1"] = "fel:http-404"
        self.assertEqual(
            self.kor(kandidat("s:1", "u1")),
            ["ej hämtad (http-404), fullständig .md orörd"],
        )
        self.assertEqual(self.md().read_text(), fore)

    def test_annan_version_under_ny_adress_konverteras_om(self):
        self.klient.filer |= {"u1": "sidor.pdf", "u3": "sidor.pdf"}
        self.kor(kandidat("s:1", "u1"), version="kommunhandlingar 0.1.0")
        self.assertEqual(self.kor(kandidat("s:1", "u3")), ["konverterad om"])
        falt = self.falt()
        self.assertEqual(falt["kalla_url"], "u3")
        self.assertTrue(falt["pipeline"].startswith("kommunhandlingar 0.2.0 /"))

    def test_annan_version_och_annat_innehall_blir_ny_version(self):
        self.klient.filer["u1"] = "sidor.pdf"
        self.kor(kandidat("s:1", "u1"), version="kommunhandlingar 0.1.0")
        fore = self.falt()["sha256"]
        self.klient.filer["u1"] = "begransad.pdf"
        self.assertEqual(self.kor(kandidat("s:1", "u1")), ["konverterad"])
        self.assertNotEqual(self.falt()["sha256"], fore)

    def test_omkonverteringen_tas_sist(self):
        gamla = [kandidat("s:1", "u1"), kandidat("s:3", "u3", "kallelse")]
        self.klient.filer |= {"u1": "sidor.pdf", "u3": "sidor.pdf"}
        self.kor(*gamla, version="kommunhandlingar 0.1.0")
        ny = kandidat("s:2", "u2", "bilaga")
        lista = [*gamla, ny]
        self.assertEqual(ordna(self.steg(lista), lista), [ny, *gamla])
        nuvarande = self.steg(lista, "kommunhandlingar 0.1.0")
        self.assertEqual(ordna(nuvarande, lista), lista)
        flyttad = [kandidat("s:1", "u9"), ny]
        self.assertEqual(ordna(self.steg(flyttad), flyttad), flyttad)

    def test_ej_hamtad_flyttas_inte_sist(self):
        self.klient.filer["u1"] = "fel:http-404"
        self.kor(kandidat("s:1", "u1"), version="kommunhandlingar 0.1.0")
        lista = [kandidat("s:1", "u1"), kandidat("s:2", "u2", "bilaga")]
        self.assertEqual(ordna(self.steg(lista), lista), lista)
