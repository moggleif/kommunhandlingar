"""Krav: K23 och K30 i docs/02-KRAV.md, ADR-0039 och ADR-0048.
Kod: src/kommunhandlingar/arkivluckor.py och src/kommunhandlingar/behandla.py."""

from kommunhandlingar import frontmatter
from tests.test_hamta import kandidat
from tests.test_hamta_arkiv import LUCKOR, W1, W2, Arkivbas

SAMRE = "lika eller lägre kvalitet; det befintliga behålls"
W3 = "https://web.archive.org/web/3id_/https://k.se/3.pdf"


class TestPlattformar(Arkivbas):
    """Arkivets kandidater från två plattformar: `s:` och `e:`."""

    def test_lika_kvalitet_fran_en_annan_plattform_behaller_det_befintliga(self):
        self.klient.filer |= {W1: "begransad.pdf", W2: "sidor.pdf"}
        resultat = self.kor(
            kandidat("s:1", W1), kandidat("e:1", W2, filnamn="Protokoll 2.pdf")
        )
        self.assertEqual(resultat, ["konverterad", SAMRE])
        self.assertEqual(self.klient.anrop, [W1, W2])
        self.assertEqual(self.falt()["kallnyckel"], "s:1")
        self.assertEqual(
            frontmatter.lista(self.falt()["tidigare_kallnycklar"]), ["e:1"]
        )
        self.assertEqual(len(list(self.data.rglob("*.md"))), 1)

    def test_hogre_kvalitet_fran_en_annan_plattform_tar_platsen(self):
        self.klient.filer |= {W1: "begransad.pdf", W2: "skarvar.pdf"}
        resultat = self.kor(kandidat("s:1", W1), kandidat("e:1", W2))
        self.assertEqual(resultat, ["konverterad", "konverterad"])
        falt = self.falt()
        self.assertEqual((falt["kallnyckel"], falt["kvalitet"]), ("e:1", "full"))
        self.assertEqual(frontmatter.lista(falt["tidigare_kallnycklar"]), ["s:1"])
        self.assertEqual(len(list(self.data.rglob("*.md"))), 1)

    def test_lagre_kvalitet_fran_en_annan_plattform_tar_inte_platsen(self):
        self.klient.filer |= {W1: "skarvar.pdf", W2: "begransad.pdf"}
        self.assertEqual(
            self.kor(kandidat("s:1", W1), kandidat("e:1", W2)), ["konverterad", SAMRE]
        )
        self.assertEqual(self.falt()["kvalitet"], "full")

    def test_ingen_av_de_tva_hamtas_igen(self):
        self.klient.filer |= {W1: "begransad.pdf", W2: "skarvar.pdf"}
        self.kor(kandidat("s:1", W1), kandidat("e:1", W2))
        self.assertEqual(
            self.kor(kandidat("s:1", W1), kandidat("e:1", W2)),
            ["tidigare källnyckel", LUCKOR],
        )

    def test_den_som_forlorade_hamtas_inte_igen(self):
        self.klient.filer |= {W1: "skarvar.pdf", W2: "begransad.pdf"}
        self.kor(kandidat("s:1", W1), kandidat("e:1", W2))
        self.assertEqual(
            self.kor(kandidat("s:1", W1), kandidat("e:1", W2)),
            [LUCKOR, "tidigare källnyckel"],
        )

    def test_ett_misslyckat_forsok_lamnar_det_befintliga_orort(self):
        self.klient.filer |= {W1: "skarvar.pdf", W2: "kapad:begransad.pdf"}
        resultat = self.kor(kandidat("s:1", W1), kandidat("e:1", W2))
        self.assertEqual(resultat[1], "ej hämtad (kapad), fullständig .md orörd")
        self.assertEqual(self.falt()["kallnyckel"], "s:1")

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

    def test_ett_forsok_fran_en_levande_kalla_tas_inte_over(self):
        self.klient.filer |= {"u1": "fel:404", W2: "begransad.pdf"}
        self.kor(kandidat("s:1", "u1"), arkiv=False)
        self.assertEqual(self.falt()["kvalitet"], "ej-hamtad")
        self.assertEqual(self.kor(kandidat("e:1", W2)), [LUCKOR])
        self.assertEqual(self.falt()["kallnyckel"], "s:1")

    def test_flera_dokument_av_typen_provas_inte(self):
        self.klient.filer |= {W1: "begransad.pdf", W2: "begransad.pdf"}
        self.klient.filer |= {W3: "skarvar.pdf"}
        resultat = self.kor(
            kandidat("s:1", W1),
            kandidat("s:2", W2, filnamn="Protokoll § 5.pdf"),
            kandidat("e:3", W3),
        )
        self.assertEqual(resultat, ["konverterad", "konverterad", LUCKOR])
        self.assertEqual(self.falt()["kallnyckel"], "s:1")

    def test_plattformen_som_redan_provats_provas_inte_igen(self):
        self.klient.filer |= {W1: "begransad.pdf", W2: "skarvar.pdf"}
        self.klient.filer |= {W3: "skarvar.pdf"}
        self.kor(kandidat("s:1", W1), kandidat("e:1", W2))
        resultat = self.kor(kandidat("s:3", W3, filnamn="Annat.pdf"))
        self.assertEqual(resultat, [LUCKOR])
        self.assertEqual(self.falt()["kallnyckel"], "e:1")

    def test_bilagor_provas_inte(self):
        self.klient.filer |= {W1: "begransad.pdf", W2: "skarvar.pdf"}
        resultat = self.kor(
            kandidat("s:1", W1, "bilaga"), kandidat("e:1", W2, "bilaga")
        )
        self.assertEqual(resultat, ["konverterad", LUCKOR])

    def test_levande_kallor_provas_inte(self):
        self.klient.filer |= {"u1": "skarvar.pdf", "u2": "begransad.pdf"}
        resultat = self.kor(
            kandidat("e:1", "u1"),
            kandidat("s:1", "u2", filnamn="Annat.pdf"),
            arkiv=False,
        )
        self.assertEqual(resultat, ["konverterad", "konverterad"])
        self.assertEqual(self.falt()["kallnyckel"], "e:1")
        self.assertEqual(self.falt("protokoll-annat")["kallnyckel"], "s:1")

    def test_flera_kandidater_fran_plattformen_provas_inte(self):
        self.klient.filer |= {W1: "begransad.pdf", W2: "skarvar.pdf"}
        self.klient.filer |= {W3: "skarvar.pdf"}
        self.kor(kandidat("e:1", W1))
        resultat = self.kor(
            kandidat("s:2", W2, filnamn="Protokoll § 78.pdf"),
            kandidat("s:3", W3, filnamn="Protokoll § 1-77.pdf"),
        )
        self.assertEqual(resultat, [LUCKOR, LUCKOR])
        self.assertEqual(self.falt()["kallnyckel"], "e:1")
