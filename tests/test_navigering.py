"""Krav: K39 i docs/02-KRAV.md, ADR-0060. Kod: src/kommunhandlingar/webbplats/
mall.py, flikar.py, oversikt.py, organsida.py, sparsida.py och malsida.py."""

import unittest
from collections import Counter
from dataclasses import replace

from kommunhandlingar.webbplats.flikar import SAMMANTRADEN, flikar
from kommunhandlingar.webbplats.mal import Mal
from kommunhandlingar.webbplats.mall import Mall, meny
from kommunhandlingar.webbplats.oversikt import kommunsida
from kommunhandlingar.webbplats.rakning import Organrad
from kommunhandlingar.webbplats.spar import Steg
from tests.test_webbplats import REPO, TID, exempelby


def steg(namn: str) -> Steg:
    return Steg("fsn", namn, 2025, "vackt", "", "", "", "")


def mal(rubrik: str, grupp: str = "") -> Mal:
    return Mal("fsn", 2025, "mål", rubrik, "", "", "", "", "", grupp, "", "")


def rad(organ: str, sammantraden: int) -> Organrad:
    return Organrad(organ, organ, sammantraden, Counter(), Counter(), 0, [], [])


def kommun_med_utskott():
    kommun = exempelby()
    utskott = replace(kommun.organ[0], id="bun-au", namn=("BUN:s utskott",))
    utskott = replace(utskott, hor_till="bun")
    return replace(kommun, organ=(*kommun.organ, utskott))


class TestNavigering(unittest.TestCase):
    def setUp(self):
        spar = {"initiativ": {"exempelby": [steg("Simskola"), steg("Öppettider")]}}
        malen = {"exempelby": [mal("Läsa", "Läsning"), mal("Läsning"), mal("Räkna")]}
        self.mall = Mall([exempelby()], REPO, TID, malen=malen, spar=spar)

    def test_menyn_har_kommunens_sidor(self):
        mall = replace(self.mall, kalendrar=frozenset({"exempelby"}))
        html = meny(mall, "exempelby/fsn.html")
        for adress in ("index", "exempelby", "exempelby/kalender", "exempelby/status"):
            self.assertIn(f'href="../{adress}.html"', html)
        self.assertIn('href="../avvikelser.html"', html)

    def test_oversikten_har_en_kolumn_per_sida_och_antalet(self):
        rader = [rad("bun", 0), rad("fsn", 4)]
        html = kommunsida(self.mall, exempelby(), rader, [])
        self.assertIn('<a href="exempelby/fsn.html">4</a>', html)
        self.assertIn('<a href="exempelby/fsn/mal-och-direktiv.html">2 mål</a>', html)
        self.assertIn('<a href="exempelby/fsn/initiativ.html">2 ärenden</a>', html)
        self.assertNotIn("exempelby/bun/", html)
        self.assertEqual(html.count('<td class="tom">'), 6 + 4)
        for rubrik in ("Mål och direktiv", "Lokalbehov", "Detaljplaner"):
            self.assertIn(f'<th scope="col">{rubrik}</th>', html)

    def test_utskottet_star_under_sin_namnd(self):
        rader = [rad("bun", 0), rad("fsn", 4), rad("bun-au", 1)]
        html = kommunsida(self.mall, kommun_med_utskott(), rader, [])
        bun, utskott, fsn = (
            html.index(f'"exempelby/{o}.html"') for o in ("bun", "bun-au", "fsn")
        )
        self.assertLess(bun, utskott)
        self.assertLess(utskott, fsn)
        self.assertIn('<th scope="row" class="utskott">', html)

    def test_oversikten_borjar_med_dokumenten(self):
        dokument = [{"datum": "2024-05-02"}, {"datum": "2013-08-13"}] * 600
        html = kommunsida(
            self.mall, exempelby(), [rad("bun", 0), rad("fsn", 0)], dokument
        )
        self.assertIn("<p>1 200 dokument från 2013-08-13 till 2024-05-02.", html)

    def test_organen_star_i_kommunfilens_grupper(self):
        kommun = kommun_med_utskott()
        bun, fsn, utskott = kommun.organ
        kommun = replace(
            kommun,
            grupper=("Nämnderna", "Övriga"),
            organ=(
                replace(bun, grupp="Övriga"),
                replace(fsn, grupp="Nämnderna"),
                utskott,
            ),
        )
        rader = [rad("bun", 0), rad("fsn", 4), rad("bun-au", 1)]
        html = kommunsida(self.mall, kommun, rader, [])
        ordning = [
            html.index(t)
            for t in (
                "Nämnderna",
                "exempelby/fsn.html",
                "Övriga",
                "exempelby/bun.html",
                "exempelby/bun-au.html",
            )
        ]
        self.assertEqual(ordning, sorted(ordning))
        self.assertEqual(html.count('<th scope="rowgroup" colspan="8">'), 2)
        self.assertEqual(html.count("<tbody>"), 2)

    def test_flikarna_pa_organets_sida(self):
        html = flikar(self.mall, "exempelby", "fsn", SAMMANTRADEN)
        self.assertIn('href="fsn.html" aria-current="page">Sammanträden', html)
        self.assertIn('href="fsn/mal-och-direktiv.html">Mål och direktiv', html)
        self.assertIn('href="fsn/initiativ.html">Initiativärenden', html)
        self.assertNotIn("lokalbehov", html)
        self.assertLess(html.index("Mål och direktiv"), html.index("Initiativ"))

    def test_flikarna_pa_en_sida_over_tid(self):
        html = flikar(self.mall, "exempelby", "fsn", "initiativ")
        self.assertIn('href="../fsn.html">Sammanträden', html)
        self.assertIn('href="../fsn/initiativ.html" aria-current="page"', html)

    def test_organ_utan_sidor_over_tid_har_bara_sammantradena(self):
        html = flikar(self.mall, "exempelby", "bun", SAMMANTRADEN)
        self.assertEqual(html.count("<li>"), 1)
