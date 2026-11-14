"""Krav: K50 i docs/02-KRAV.md, ADR-0073. Kod: src/kommunhandlingar/webbplats/
malar.py, malsida.py och mal.js."""

import unittest

from tests.test_malkort import UPPFOLJDA, sida

# Trygga miljöer står 2022 och 2025 och heter Läsfrämjande 2026; direktivet
# Läsfrämjande står 2024 och 2025. 2023 är en lucka.


def aret(html: str, ar: int) -> str:
    return html.split(f'<section class="aret" data-ar="{ar}">')[1].split("</section>")[
        0
    ]


class TestEttArITaget(unittest.TestCase):
    def test_aren_nyast_forst_med_en_knapp_per_ar(self):
        html = sida()
        avsnitt = [
            html.index(f'class="aret" data-ar="{a}">') for a in range(2026, 2021, -1)
        ]
        self.assertEqual(avsnitt, sorted(avsnitt))
        for ar in range(2022, 2027):
            self.assertIn(f'<button type="button" data-ar="{ar}">{ar}</button>', html)

    def test_arets_antal_och_kort(self):
        html = aret(sida(), 2024)
        self.assertIn("<h3>2024</h3>", html)
        self.assertIn("<dt>direktiv</dt><dd>1</dd>", html)
        self.assertIn("<h4>Läsfrämjande</h4>", html)
        self.assertIn("Delvis uppnått (prognos)", html)
        self.assertIn('<a href="2024/2024-05-02/protokoll.html#sida-2">', html)

    def test_formuleringen_en_gang_och_beslutet_utan_status(self):
        html = aret(sida(), 2025)
        self.assertEqual(html.count("<q>Alla ska känna sig trygga.</q>"), 1)
        self.assertIn('<li>Beslutat<br>Källa: <a href="2024/', html)

    def test_kortet_har_aret_rubrik_och_urvalets_egenskaper(self):
        html = aret(sida(), 2026)
        self.assertIn("<h4>Läsfrämjande <small>tolkad</small></h4>", html)
        self.assertIn('<article data-mal="0" data-slag="nämndmål"', html)
        self.assertNotIn("Trygga miljöer</h4>", html)

    def test_nytt_och_forsvunnet_jamfort_med_aret_innan(self):
        html = sida()
        self.assertIn("<span>nytt</span>", aret(html, 2025))
        self.assertEqual(aret(html, 2025).count("<span>nytt</span>"), 1)
        self.assertIn("Inget mål försvann sedan 2024.", aret(html, 2025))
        forsvann = aret(html, 2026)
        self.assertIn("Försvann sedan 2025:", forsvann)
        self.assertIn('<a href="#mal-1">Läsfrämjande</a>', forsvann)
        self.assertNotIn("<span>nytt</span>", forsvann)

    def test_forsta_aret_jamfors_inte(self):
        html = aret(sida(), 2022)
        self.assertIn("Det första året med mål på sidan.", html)
        self.assertNotIn("<span>nytt</span>", html)

    def test_luckan_och_aret_efter(self):
        html = sida()
        self.assertIn(
            "Lucka i poolen: inga dokument från organet 2023.", aret(html, 2023)
        )
        efter = aret(html, 2024)
        self.assertIn("Året innan är en lucka i poolen", efter)
        self.assertNotIn("<span>nytt</span>", efter)

    def test_ar_med_dokument_men_utan_mal(self):
        html = aret(sida(dokumentar=(2022, 2023, 2024)), 2023)
        self.assertIn("Poolens dokument från organet 2023 har inga mål.", html)

    def test_protokollen_det_aret(self):
        html = sida(uppfoljda=UPPFOLJDA)
        self.assertIn("2024-05-02 § 5, uppföljning: Trygga miljöer", aret(html, 2024))
        self.assertIn("2024-05-02 § 6, dragning: Läsfrämjande", aret(html, 2024))
        self.assertIn("Protokollen 2022 tar inte upp målen.", aret(html, 2022))
        self.assertIn("Inga protokoll med text i poolen 2025.", aret(html, 2025))

    def test_utan_uppfoljningsfil_inget_om_protokollen(self):
        self.assertNotIn("Protokollen", aret(sida(), 2022))


class TestPerspektiven(unittest.TestCase):
    def test_vaeljaren_och_de_tre_perspektiven(self):
        html = sida()
        self.assertIn(
            '<div class="perspektiv" role="group" aria-label="Perspektiv" hidden>'
            '<button type="button" data-vy="tidslinje">Tidslinje</button>'
            '<button type="button" data-vy="ar">Ett år i taget</button>'
            '<button type="button" data-vy="kort">Målkort</button></div>',
            html,
        )
        vyer = [
            html.index(f'<section data-vy="{v}">') for v in ("tidslinje", "ar", "kort")
        ]
        self.assertEqual(vyer, sorted(vyer))
        self.assertLess(html.index('class="urval"'), vyer[0])
        self.assertIn('<div class="arval" role="group" aria-label="År" hidden>', html)
