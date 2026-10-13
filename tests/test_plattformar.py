"""Krav: K23 i docs/02-KRAV.md, ADR-0039.
Kod: src/kommunhandlingar/luckor.py och src/kommunhandlingar/behandla.py."""

from kommunhandlingar import frontmatter
from tests.test_hamta import kandidat
from tests.test_hamta_arkiv import LUCKOR, W1, W2, TestArkivet

W3 = "https://web.archive.org/web/3id_/https://k.se/3.pdf"


class TestPlattformar(TestArkivet):
    """Arkivets kandidater från två plattformar: `s:` och `e:`."""

    def test_mot_med_typen_fran_en_annan_plattform_hamtas_inte(self):
        self.klient.filer |= {W1: "begransad.pdf", W2: "sidor.pdf"}
        resultat = self.kor(
            kandidat("s:1", W1), kandidat("e:1", W2, filnamn="Protokoll 2.pdf")
        )
        self.assertEqual(resultat, ["konverterad", LUCKOR])
        self.assertEqual(self.klient.anrop, [W1])
        self.assertEqual(len(list(self.data.rglob("*.md"))), 1)

    def test_en_annan_typ_samma_dag_hamtas(self):
        self.klient.filer |= {W1: "begransad.pdf", W2: "sidor.pdf"}
        resultat = self.kor(kandidat("s:1", W1), kandidat("e:1", W2, "kallelse"))
        self.assertEqual(resultat, ["konverterad", "konverterad"])

    def test_samma_plattform_far_flera_filer_av_typen(self):
        self.klient.filer |= {W1: "begransad.pdf", W2: "begransad.pdf"}
        resultat = self.kor(
            kandidat("e:1", W1), kandidat("e:2", W2, filnamn="Protokoll § 5.pdf")
        )
        self.assertEqual(resultat, ["konverterad", "konverterad"])

    def test_ett_forsok_fran_en_annan_plattform_tas_over(self):
        self.klient.filer |= {W1: "kapad:begransad.pdf", W2: "begransad.pdf"}
        self.kor(kandidat("s:1", W1))
        self.assertEqual(
            self.kor(kandidat("s:1", W1), kandidat("e:1", W2)),
            [
                "ej hämtad (kapad), oförändrad",
                "konverterad",
            ],
        )
        falt = self.falt()
        self.assertEqual(falt["kallnyckel"], "e:1")
        self.assertNotEqual(falt["kvalitet"], "ej-hamtad")
        self.assertEqual(frontmatter.lista(falt["tidigare_kallnycklar"]), ["s:1"])
        self.assertEqual(len(list(self.data.rglob("*.md"))), 1)

    def test_den_overtagna_nyckeln_hamtas_inte_igen(self):
        self.klient.filer |= {W1: "kapad:begransad.pdf", W2: "begransad.pdf"}
        self.kor(kandidat("s:1", W1))
        self.kor(kandidat("s:1", W1), kandidat("e:1", W2))
        self.assertEqual(
            self.kor(kandidat("s:1", W1), kandidat("e:1", W2)),
            ["tidigare källnyckel", LUCKOR],
        )

    def test_ett_forsok_fran_samma_plattform_tas_inte_over(self):
        self.klient.filer |= {W1: "kapad:begransad.pdf", W3: "begransad.pdf"}
        self.kor(kandidat("s:1", W1))
        self.assertEqual(self.kor(kandidat("s:3", W3)), [LUCKOR])
        self.assertEqual(self.falt()["kallnyckel"], "s:1")
