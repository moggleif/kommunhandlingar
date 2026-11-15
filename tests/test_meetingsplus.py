"""Krav: K57 i docs/02-KRAV.md, ADR-0080.
Kod: src/kommunhandlingar/adaptrar/meetingsplus.py och meetingsplus_html.py.

Sidorna under tests/fixtures/meetingsplus/ är Region Hallands, sparade
2026-11-15."""

import copy
import unittest
from datetime import date
from pathlib import Path

from kommunhandlingar.adaptrar import meetingsplus_html
from kommunhandlingar.adaptrar.meetingsplus import kalla_av, las_mote, upptack
from kommunhandlingar.fel import Konfigurationsfel

SIDOR = Path(__file__).parent / "fixtures" / "meetingsplus"
BAS = "https://politik.regionhalland.se/committees"
SJUKHUS = f"{BAS}/driftnamnden-hallands-sjukhus"
SAMLING = f"{BAS}/regionfullmaktige/mote-2014-01-01"
POST = {
    "adapter": "meetingsplus",
    "sidor": {"rf": f"{BAS}/regionfullmaktige", "hs": SJUKHUS},
    "samlingsmoten": [SAMLING],
    "monster": [
        {"typ": "protokoll", "regex": r"(?P<ar>\d{4})-(?P<manad>\d{2})-(?P<dag>\d{2})"}
    ],
}
ORGAN = ["rf", "hs"]


def html(namn: str) -> str:
    return (SIDOR / namn).read_text(encoding="utf-8")


def kalla(post: dict = POST):
    return kalla_av(post, ORGAN, "kalla 1")


class TestOrgansidan(unittest.TestCase):
    def test_alla_moten_i_sidans_ordning(self):
        moten = meetingsplus_html.moten(html("organsida.html"), SJUKHUS)
        self.assertEqual(len(moten), 73)
        self.assertEqual(moten[0], f"{SJUKHUS}/mote-2026-12-02")
        self.assertEqual(moten[-1], f"{SJUKHUS}/mote-2017-06-28")

    def test_bara_adresser_direkt_under_organet(self):
        sida = (
            f'<a href="{SJUKHUS}/mote-2026-01-01">a</a>'
            f'<a href="{SJUKHUS}/mote-2026-01-01/agenda/x-2026-01-01pdf">b</a>'
            f'<a href="{BAS}/regionstyrelsen/mote-2026-01-02">c</a>'
            f'<a href="{SJUKHUS}/mote-2026-01-03?x=1">d</a>'
            '<a href="/committees/driftnamnden-hallands-sjukhus/mote-2026-01-04">e</a>'
        )
        self.assertEqual(
            meetingsplus_html.moten(sida, SJUKHUS),
            [f"{SJUKHUS}/mote-2026-01-01", f"{SJUKHUS}/mote-2026-01-04"],
        )


class TestMotessidan(unittest.TestCase):
    def setUp(self):
        self.mote = f"{SJUKHUS}/mote-2026-09-30"
        self.kandidater, self.avvisade = las_mote(
            kalla(), "hs", self.mote, html("mote-2026-09-30.html")
        )

    def test_kallelse_protokoll_och_bilagor(self):
        typer = [k.typ for k in self.kandidater]
        self.assertEqual(
            (typer.count("kallelse"), typer.count("protokoll"), typer.count("bilaga")),
            (2, 1, 7),
        )
        self.assertEqual(self.avvisade, [])

    def test_datumet_och_kallan_ar_motets(self):
        self.assertEqual({k.datum for k in self.kandidater}, {date(2026, 9, 30)})
        self.assertEqual({k.kalla for k in self.kandidater}, {self.mote})

    def test_kallnyckeln_ar_sokvagen_och_adressen_oppnar_filen(self):
        protokoll = next(k for k in self.kandidater if k.typ == "protokoll")
        sokvag = (
            "/committees/driftnamnden-hallands-sjukhus/mote-2026-09-30"
            "/protocol/protokoll-dn-hs-2026-09-30pdf"
        )
        self.assertEqual(protokoll.kallnyckel, f"meetingsplus:{sokvag}")
        self.assertEqual(
            protokoll.url,
            f"https://politik.regionhalland.se{sokvag}?downloadMode=open",
        )

    def test_filnamnet_ar_lanktexten_eller_adressens_sista_del(self):
        namn = {k.filnamn for k in self.kandidater}
        self.assertIn("Beslutsförslag uppföljning intern kontrollplan 2026.pdf", namn)
        self.assertIn("protokoll-dn-hs-2026-09-30pdf", namn)

    def test_protokollets_bilagor_bara_med_eget_filnamn(self):
        mote = f"{BAS}/driftnamnden-kollektivtrafik/mote-2023-01-20-12741"
        kandidater, _ = las_mote(
            kalla(), "hs", mote, html("mote-med-protokollets-bilagor.html")
        )
        bilagor = [k for k in kandidater if k.typ == "bilaga"]
        self.assertEqual(len(bilagor), 12)
        self.assertTrue(all("/agenda/" in k.kallnyckel for k in bilagor))
        self.assertEqual({k.datum for k in kandidater}, {date(2023, 1, 20)})

    def test_en_bilaga_bara_under_protokollet_blir_en_kandidat(self):
        mote = f"{SJUKHUS}/mote-2026-01-01"
        sida = (
            '<a href="/w/mote-2026-01-01/agenda/apdf?downloadMode=open">A.pdf</a>'
            '<a href="/w/mote-2026-01-01/protocol/apdf?downloadMode=open">A.pdf</a>'
            '<a href="/w/mote-2026-01-01/protocol/bpdf?downloadMode=open">B.pdf</a>'
        )
        kandidater, _ = las_mote(kalla(), "hs", mote, sida)
        self.assertEqual(
            [(k.typ, k.kallnyckel) for k in kandidater],
            [
                ("bilaga", "meetingsplus:/w/mote-2026-01-01/agenda/apdf"),
                ("bilaga", "meetingsplus:/w/mote-2026-01-01/protocol/bpdf"),
            ],
        )

    def test_en_fil_som_inte_ar_pdf_blir_ingen_kandidat(self):
        sida = f'<a href="{BAS}/x/agenda/lista-xlsx?downloadMode=open">Lista.xlsx</a>'
        kandidater, avvisade = las_mote(
            kalla(), "hs", f"{SJUKHUS}/mote-2026-01-01", sida
        )
        self.assertEqual(kandidater, [])
        self.assertEqual(
            [(a.filnamn, a.orsak) for a in avvisade], [("Lista.xlsx", "inte en PDF")]
        )


class TestSamlingsmoten(unittest.TestCase):
    def test_typ_och_datum_ur_filnamnet(self):
        kandidater, avvisade = las_mote(
            kalla(), "rf", SAMLING, html("samlingsmote.html")
        )
        self.assertEqual({k.typ for k in kandidater}, {"protokoll"})
        self.assertEqual(
            [k.datum for k in kandidater],
            [date(2014, 4, 16), date(2014, 6, 18), date(2014, 10, 8),
             date(2014, 11, 5), date(2014, 12, 10)],
        )  # fmt: skip
        self.assertEqual(avvisade, [])

    def test_en_fil_utan_datum_blir_ingen_kandidat(self):
        sida = f'<a href="{SAMLING}x/agenda/manualpdf?downloadMode=open">Manual.pdf</a>'
        _, avvisade = las_mote(kalla(), "rf", SAMLING, sida)
        self.assertEqual([a.filnamn for a in avvisade], ["Manual.pdf"])


class TestUpptack(unittest.TestCase):
    def test_organsidan_och_varje_mote_hamtas(self):
        mote = f"{SJUKHUS}/mote-2026-09-30"
        sidor = {
            POST["sidor"]["rf"]: "",
            SJUKHUS: f'<a href="{mote}">Möte</a>',
            mote: html("mote-2026-09-30.html"),
        }
        kandidater, _ = upptack(kalla(), sidor.__getitem__)
        self.assertEqual(len(kandidater), 10)
        self.assertEqual({k.organ for k in kandidater}, {"hs"})


class TestKallan(unittest.TestCase):
    def test_samlingsmote_utan_organsida_stoppar(self):
        post = copy.deepcopy(POST)
        post["samlingsmoten"] = [f"{BAS}/regionstyrelsen/mote-2013-01-01"]
        with self.assertRaises(Konfigurationsfel):
            kalla(post)

    def test_samlingsmotet_skrivs_som_upptackten_skriver_det(self):
        post = copy.deepcopy(POST)
        post["samlingsmoten"] = [f"{SAMLING}/"]
        self.assertEqual(kalla(post).samlingsmoten, (SAMLING,))

    def test_samlingsmote_som_inte_ar_ett_mote_under_organsidan_stoppar(self):
        for adress in (f"{SAMLING}/agenda", f"{BAS}/regionfullmaktige/arkiv"):
            post = copy.deepcopy(POST)
            post["samlingsmoten"] = [adress]
            with self.subTest(adress), self.assertRaises(Konfigurationsfel):
                kalla(post)

    def test_okant_falt_och_okant_organ_stoppar(self):
        for andring in ({"rubrik": "x"}, {"sidor": {"okand": SJUKHUS}}):
            with self.subTest(andring), self.assertRaises(Konfigurationsfel):
                kalla(copy.deepcopy(POST) | andring)

    def test_samlingsmoten_och_monster_kan_utelamnas(self):
        post = {"adapter": "meetingsplus", "sidor": {"hs": SJUKHUS}}
        self.assertEqual(kalla(post).samlingsmoten, ())
