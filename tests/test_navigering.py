"""Krav: K39, K58 och K59 i docs/02-KRAV.md, ADR-0060, ADR-0081 och ADR-0085. Kod:
src/kommunhandlingar/webbplats/meny.py, organordning.py, flikar.py, oversikt.py,
organsida.py, sparsida.py, malsida.py och kalendersida.py."""

import re
import unittest
from collections import Counter
from dataclasses import replace

from kommunhandlingar.webbplats.flikar import SAMMANTRADEN, flikar
from kommunhandlingar.webbplats.kalendersida import kalendersida
from kommunhandlingar.webbplats.mal import Mal
from kommunhandlingar.webbplats.mall import Mall, sida
from kommunhandlingar.webbplats.meny import kommunens, meny, oversiktsnamn
from kommunhandlingar.webbplats.oversikt import adresser, oversikt
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
        html = meny([exempelby()], frozenset({"exempelby"}), "exempelby/fsn.html")
        for adress in ("index", "exempelby/kalender", "exempelby/status"):
            self.assertIn(f'href="../{adress}.html"', html)
        self.assertIn('href="../avvikelser.html"', html)

    def test_en_kommuns_grupper_ar_menyns_poster(self):
        html = meny(
            [kommun_med_utskott()], frozenset({"exempelby"}), "exempelby/fsn.html"
        )
        self.assertTrue(
            html.startswith('<nav class="sajtmeny" aria-label="Webbplatsen">')
        )
        self.assertIn(
            '<a class="sajtnamn" href="../index.html">Exempelby kommun</a>', html
        )
        toppen = re.sub(r"</summary>.*?</details>", "</summary></details>", html)
        poster = re.findall(r"<li><(?:a [^>]*|details><summary)>([^<]+)<", toppen)
        self.assertEqual(
            poster, ["Handlingar och protokoll", "Kalender", "Organen", "Om poolen"]
        )
        self.assertNotIn(f"<summary>{exempelby().namn}</summary>", html)
        self.assertNotIn('class="grupp"', html)
        self.assertIn('href="../exempelby/fsn.html" aria-current="page"', html)
        self.assertNotIn("exempelby/bun-au.html", html)
        self.assertIn(
            '<summary>Om poolen</summary><ul><li><a href="../exempelby/status.html">'
            'Poolens status</a></li><li><a href="../avvikelser.html">Avvikelser</a>',
            html,
        )
        self.assertTrue(html.endswith("</ul></nav>"))

    def test_kalendern_har_ingen_stig_till_oversikten(self):
        kalender = kalendersida(self.mall, exempelby(), [])
        self.assertNotIn('aria-label="Här är du"', kalender)
        self.assertIn('<a href="../index.html">Handlingar och protokoll</a>', kalender)
        flera = Mall([exempelby(), replace(exempelby(), id="andraby")], REPO, TID)
        self.assertNotIn('aria-label="Här är du"', kalendersida(flera, exempelby(), []))

    def test_en_kommun_utan_kalender_har_ingen_kalenderpost(self):
        html = meny([exempelby()], frozenset(), "index.html")
        self.assertNotIn("kalender.html", html)

    def test_en_kommuns_oversikt_heter_inte_som_sajten(self):
        self.assertEqual(
            oversiktsnamn(self.mall.kommuner, exempelby()), "Handlingar och protokoll"
        )

    def test_varje_kommun_ar_en_post_i_menyn(self):
        andra = replace(exempelby(), id="andraby", namn="Andraby", grupper=())
        html = meny([exempelby(), andra], frozenset({"exempelby"}), "index.html")
        toppen = re.sub(r"</summary>.*?</details>", "</summary></details>", html)
        poster = re.findall(r"<li><(?:a [^>]*|details><summary)>([^<]+)<", toppen)
        self.assertEqual(poster, [exempelby().namn, "Andraby", "Avvikelser"])
        self.assertIn('href="andraby/status.html">Poolens status<', html)
        self.assertNotIn("andraby/kalender.html", html)
        self.assertIn('<p class="grupp">Organen</p>', html)
        self.assertNotIn('<p class="grupp"></p>', html)
        self.assertIn('aria-current="page">Kommunhandlingar</a>', html)
        self.assertIn(
            '<p class="grupp">Översikt</p><ul><li><a href="andraby.html">', html
        )

    def test_kommunens_namn_i_rubriken_bara_med_flera_kommuner(self):
        andra = replace(exempelby(), id="andraby", namn="Andraby")
        self.assertEqual(kommunens([andra], "Kalender", andra), "Kalender")
        self.assertEqual(
            kommunens([exempelby(), andra], "Kalender", andra), "Kalender – Andraby"
        )
        self.assertEqual(oversiktsnamn([andra], andra), "Handlingar och protokoll")
        self.assertEqual(oversiktsnamn([exempelby(), andra], andra), "Andraby")

    def test_sidan_heter_som_sin_enda_kommun(self):
        html = sida(self.mall, "exempelby/fsn.html", "Förskolan", "")
        self.assertIn("<title>Förskolan – Exempelby kommun</title>", html)
        html = sida(self.mall, "index.html", "Exempelby kommun", "")
        self.assertIn("<title>Exempelby kommun</title>", html)

    def test_en_enda_kommun_borjar_pa_sin_oversikt(self):
        self.assertEqual(
            adresser(self.mall, exempelby()), ["exempelby.html", "index.html"]
        )
        andra = replace(exempelby(), id="andraby")
        mall = Mall([exempelby(), andra], REPO, TID)
        self.assertEqual(adresser(mall, andra), ["andraby.html"])

    def test_sidan_laddar_den_gemensamma_menyn_fran_giffa(self):
        html = sida(self.mall, "index.html", "Start", "")
        self.assertIn('<link rel="stylesheet" href="/giffa/sajter.css">', html)
        self.assertIn('<script src="/giffa/sajter.js" defer></script>', html)
        tema = html.index('<script src="/giffa/tema.js"></script>')
        self.assertLess(tema, html.index("</head>"))
        self.assertLess(html.index("/giffa/sajter.css"), html.index("<style>"))

    def test_oversikten_har_en_kolumn_per_sida_kommunen_har_och_antalet(self):
        rader = [rad("bun", 0), rad("fsn", 4)]
        html = oversikt(self.mall, exempelby(), rader, [])
        self.assertIn('<a href="exempelby/fsn.html">4</a>', html)
        self.assertIn('<a href="exempelby/fsn/mal-och-direktiv.html">2 mål</a>', html)
        self.assertIn('<a href="exempelby/fsn/initiativ.html">2 ärenden</a>', html)
        self.assertNotIn("exempelby/bun/", html)
        self.assertEqual(html.count('<td class="tom">'), 2)
        for rubrik in ("Mål och direktiv", "Initiativ och motioner"):
            self.assertIn(f'<th scope="col">{rubrik}</th>', html)
        for rubrik in ("Lokalbehov", "Detaljplaner", "Lokaler och investeringar"):
            self.assertNotIn(f'<th scope="col">{rubrik}</th>', html)

    def test_utskottet_star_under_sin_namnd(self):
        rader = [rad("bun", 0), rad("fsn", 4), rad("bun-au", 1)]
        html = oversikt(self.mall, kommun_med_utskott(), rader, [])
        bun, utskott, fsn = (
            html.index(f'"exempelby/{o}.html"') for o in ("bun", "bun-au", "fsn")
        )
        self.assertLess(bun, utskott)
        self.assertLess(utskott, fsn)
        self.assertIn('<th scope="row" class="utskott">', html)

    def test_oversikten_borjar_med_dokumenten(self):
        dokument = [{"datum": "2024-05-02"}, {"datum": "2013-08-13"}] * 600
        html = oversikt(
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
        html = oversikt(self.mall, kommun, rader, [])
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
        self.assertEqual(html.count('<th scope="rowgroup" colspan="4">'), 2)
        self.assertEqual(html.count("<tbody>"), 2)

    def test_flikarna_pa_organets_sida(self):
        html = flikar(self.mall, "exempelby", "fsn", SAMMANTRADEN)
        self.assertIn('href="fsn.html" aria-current="page">Sammanträden', html)
        self.assertIn('href="fsn/mal-och-direktiv.html">Mål och direktiv', html)
        self.assertIn('href="fsn/initiativ.html">Initiativ och motioner', html)
        self.assertNotIn("lokalbehov", html)
        self.assertLess(html.index("Mål och direktiv"), html.index("Initiativ"))

    def test_flikarna_pa_en_sida_over_tid(self):
        html = flikar(self.mall, "exempelby", "fsn", "initiativ")
        self.assertIn('href="../fsn.html">Sammanträden', html)
        self.assertIn('href="../fsn/initiativ.html" aria-current="page"', html)

    def test_organ_utan_sidor_over_tid_har_bara_sammantradena(self):
        html = flikar(self.mall, "exempelby", "bun", SAMMANTRADEN)
        self.assertEqual(html.count("<li>"), 1)
