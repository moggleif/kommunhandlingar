"""Krav: K31 i docs/02-KRAV.md, ADR-0049. Kod:
src/kommunhandlingar/adaptrar/episerver_arkiv.py, src/kommunhandlingar/original.py
och src/kommunhandlingar/behandla.py."""

import unittest
from dataclasses import replace
from datetime import date

from kommunhandlingar import frontmatter
from kommunhandlingar.adaptrar.episerver_arkiv import upptack
from tests.test_episerver import MAPP, kalla
from tests.test_episerver_arkiv import PDF, G
from tests.test_hamta import kandidat
from tests.test_hamta_arkiv import W1, W2, Arkivbas
from tests.test_sitevision_arkiv import Klient

W3 = "https://web.archive.org/web/3id_/https://k.se/3.pdf"


def i_delar(*adresser: str):
    return replace(kandidat("e:mote", adresser[0]), delar=adresser)


class TestMotenIDelar(unittest.TestCase):
    def test_ett_motes_filer_av_samma_typ_blir_en_kandidat(self):
        svar = [
            ["20140703000000", f"{G}/Handlingar/2014/H%20140219%20del%2010.pdf", "9"],
            ["20140703000000", f"{G}/Handlingar/2014/H%20140219%20del%202.pdf", "9"],
            ["20140703000000", f"{G}/Protokoll/2014/Protokoll%20140219.pdf", "9"],
        ]
        kandidater, _, _ = upptack(kalla(), Klient({(MAPP, PDF): svar}, {}))
        handlingar = next(k for k in kandidater if k.typ == "handlingar")
        self.assertEqual(len(kandidater), 2)
        self.assertEqual(handlingar.kallnyckel, "episerver:bun/2014-02-19/handlingar")
        self.assertEqual(handlingar.datum, date(2014, 2, 19))
        self.assertEqual(
            [d.rsplit("/", 1)[1] for d in handlingar.delar],
            ["H%20140219%20del%202.pdf", "H%20140219%20del%2010.pdf"],
        )

    def test_en_ensam_fil_har_inga_delar(self):
        svar = [["20140703000000", f"{G}/Protokoll/2014/Protokoll%20140219.pdf", "9"]]
        kandidater, _, _ = upptack(kalla(), Klient({(MAPP, PDF): svar}, {}))
        self.assertEqual(kandidater[0].delar, ())


class TestHamtningIDelar(Arkivbas):
    def test_delarna_blir_ett_dokument(self):
        self.klient.filer |= {W1: "skarvar.pdf", W2: "delade.pdf"}
        self.assertEqual(self.kor(i_delar(W1, W2)), ["konverterad"])
        falt = self.falt()
        self.assertEqual(frontmatter.lista(falt["kalla_url"]), [W1, W2])
        self.assertEqual(len(frontmatter.lista(falt["sha256"])), 2)
        self.assertEqual(len(frontmatter.lista(falt["bytes"])), 2)
        self.assertEqual(falt["sidor"], "20")
        self.assertEqual(len(list(self.data.rglob("*.md"))), 1)

    def test_samma_delar_igen_ar_oforandrat(self):
        self.klient.filer |= {W1: "skarvar.pdf", W2: "delade.pdf"}
        self.kor(i_delar(W1, W2))
        self.assertEqual(
            self.kor(i_delar(W1, W2)), ["finns redan; arkivet fyller bara luckor"]
        )

    def test_en_kapad_del_gor_hela_dokumentet_ej_hamtat(self):
        self.klient.filer |= {W1: "skarvar.pdf", W2: "kapad:delade.pdf"}
        self.assertEqual(self.kor(i_delar(W1, W2)), ["ej hämtad (kapad)"])
        falt = self.falt()
        self.assertEqual((falt["kvalitet"], falt["fel"]), ("ej-hamtad", "kapad"))
        self.assertEqual(frontmatter.lista(falt["kalla_url"]), [W1, W2])

    def test_en_del_som_inte_gar_att_oppna_markerar_dokumentet(self):
        self.klient.filer |= {W1: "skarvar.pdf", W2: "krypterad.pdf"}
        self.kor(i_delar(W1, W2))
        falt = self.falt()
        self.assertEqual(
            (falt["kvalitet"], falt["fel"]), ("ej-konverterad", "krypterad")
        )

    def test_ett_ej_hamtat_i_delar_ar_en_kopia_ur_arkivet(self):
        self.klient.filer |= {W1: "skarvar.pdf", W2: "kapad:delade.pdf"}
        self.klient.filer |= {W3: "skarvar.pdf"}
        self.kor(i_delar(W1, W2))
        self.assertEqual(self.kor(kandidat("s:1", W3)), ["konverterad"])
        self.assertEqual(self.falt()["kallnyckel"], "s:1")
