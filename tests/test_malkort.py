"""Krav: K29 i docs/02-KRAV.md, ADR-0047. Kod: src/kommunhandlingar/webbplats/
maltidslinje.py, malkort.py, malsida.py, malstatistik.py och mal.js."""

import re
import unittest
from dataclasses import replace

from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.malsida import malsida
from kommunhandlingar.webbplats.maltidslinje import arets
from kommunhandlingar.webbplats.uppfoljningar import Uppfoljning
from tests.test_mal import BUDGET, RADER, pool
from tests.test_webbplats import REPO, TID, exempelby, protokoll

# Trygga miljöer 2022 och 2025 byter rubrik till Läsfrämjande 2026; direktivet
# Läsfrämjande står 2024 och 2025.
GRUPPER = RADER + (
    f"fsn,2026,nämndmål,Läsfrämjande,,,,,{BUDGET}#sida-2,Trygga miljöer,ja\n"
    f"fsn,2022,nämndmål,Trygga miljöer,,,,,{BUDGET}#sida-1-2,,\n"
)
UPPFOLJDA = [
    Uppfoljning("fsn", "2024-05-02", "5", "uppföljning", "Trygga miljöer", BUDGET),
    Uppfoljning("fsn", "2024-05-02", "6", "dragning", "Läsfrämjande", BUDGET),
]


def sida(dokumentar: tuple[int, ...] = (2022, 2024), uppfoljda=()) -> str:
    with pool(GRUPPER) as malen:
        mall = Mall([exempelby()], REPO, TID, uppfoljningar={"exempelby": uppfoljda})
        return malsida(mall, exempelby(), malen, protokoll(*dokumentar))


def rad(html: str, rubrik: str) -> list[str]:
    tr = re.search(
        rf"<tr data-mal[^>]*><th[^>]*><a [^>]*>{rubrik}</a></th>(.*?)</tr>", html
    )
    return re.findall(r"<td( class=\"[^\"]*\")?>", tr.group(1))


def kort(html: str, nr: int) -> str:
    return html.split(f'<article id="mal-{nr}"')[1].split("</article>")[0]


class TestTidslinjen(unittest.TestCase):
    def test_ett_band_per_spar_och_ar_med_ny_rubrik(self):
        html = sida()
        self.assertEqual(
            rad(html, "Läsfrämjande"),
            [
                ' class="band start slut"',
                "",
                "",
                ' class="band start"',
                ' class="band slut"',
            ],
        )
        self.assertIn('aria-label="Ny rubrik: Läsfrämjande"', html)
        self.assertEqual(html.count('class="ny-rubrik"'), 1)

    def test_ar_utan_dokument_och_mal_ar_en_lucka(self):
        html = sida()
        self.assertIn('<th scope="col" class=lucka>2023<br><small>lucka</small>', html)
        self.assertNotIn("class=lucka>2024", html)
        self.assertIn('<li class="lucka" title="2023: lucka i poolen">', html)

    def test_namndmal_och_direktiv_var_for_sig(self):
        html = sida()
        self.assertLess(html.index(">Nämndmål</th>"), html.index(">Direktiv</th>"))
        self.assertEqual(html.count("<tr data-mal"), 2)

    def test_namnden_om_malen_med_streck_for_ar_utan_protokoll(self):
        html = sida((2022, 2024), UPPFOLJDA)
        namnden = html[
            html.index('class="namnden"') : html.index(
                "</tbody>", html.index('class="namnden"')
            )
        ]
        self.assertIn('aria-label="2024-05-02 § 5: Trygga miljöer"', namnden)
        self.assertIn('<span class="dragning" role="img"', namnden)
        self.assertEqual(namnden.count('class="saknas"'), 3)
        self.assertNotIn('class="namnden"', sida())

    def test_utfallet_gar_fore_prognosen_och_beslutet(self):
        with pool() as malen:
            prognos = malen[1]
        utfall = replace(
            prognos, uppfoljning="utfall", bedomning="uppnatt", status="Klart"
        )
        beslut = replace(prognos, uppfoljning="", bedomning="", status="")
        self.assertIn('class="status uppnatt"', arets([beslut, prognos, utfall]))
        self.assertIn('class="status delvis prognos"', arets([beslut, prognos]))
        self.assertIn('class="status beslutat"', arets([beslut]))


class TestKorten(unittest.TestCase):
    def test_de_som_galler_sist_aret_forst(self):
        html = sida()
        ordning = re.findall(r'<article id="mal-(\d)"[^>]*data-aktiv="(\w+)"', html)
        self.assertEqual(ordning, [("0", "ja"), ("1", "nej")])

    def test_kortet_har_slag_ar_rubriker_och_remsa(self):
        html = kort(sida(), 0)
        self.assertIn("<span>nämndmål</span> <span>2022–2026</span>", html)
        self.assertIn("<h3>Läsfrämjande <small>tolkad</small></h3>", html)
        self.assertIn("Tidigare: Trygga miljöer", html)
        self.assertIn("<blockquote><q>Alla ska känna sig trygga.</q> (2025)", html)
        self.assertEqual(html.count("<li title=") + html.count("<li class="), 5)
        self.assertIn("Hela historiken, 3 rader", html)

    def test_urvalet_och_skriptet(self):
        html = sida()
        self.assertIn('<div class="urval" role="group" aria-label="Visa" hidden>', html)
        self.assertIn('data-urval="aktiv">Gäller 2026</button>', html)
        self.assertIn('data-urval="bytt">Har bytt rubrik', html)
        self.assertIn('kort.querySelector("details").open = true', html)


class TestSammandraget(unittest.TestCase):
    def test_det_senaste_arets_antal(self):
        html = sida((2022, 2026), UPPFOLJDA)
        ruta = html[html.index('<div class="ruta"><h3>') : html.index("</dl>")]
        self.assertIn("<h3>2026</h3>", ruta)
        self.assertIn("<dt>nämndmål</dt><dd>1</dd>", ruta)
        self.assertIn("<dt>direktiv</dt><dd>0</dd>", ruta)
        self.assertIn("<dt>dragningar om målen</dt><dd>0</dd>", ruta)
        self.assertNotIn(
            "dragningar om målen", sida((2022,), UPPFOLJDA).split("</dl>")[0]
        )
