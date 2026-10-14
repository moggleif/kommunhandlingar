"""Krav: K29 i docs/02-KRAV.md, ADR-0050 och ADR-0051. Kod:
src/kommunhandlingar/webbplats/maltidslinje.py, malkort.py,
malsida.py, malstatistik.py och mal.js."""

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


def rad(html: str, nr: int, rubrik: str) -> list[str]:
    tr = re.search(rf'<a href="#mal-{nr}">{rubrik}</a>.*?</th>(.*?)</tr>', html)
    return re.findall(r"<td( class=\"[^\"]*\")?>", tr.group(1))


def kort(html: str, nr: int) -> str:
    return html.split(f'<article id="mal-{nr}"')[1].split("</article>")[0]


class TestTidslinjen(unittest.TestCase):
    def test_en_rad_per_rubrik_med_sitt_band(self):
        html = sida()
        self.assertEqual(
            rad(html, 0, "Trygga miljöer"),
            [' class="band start slut"', "", "", ' class="band start slut"', ""],
        )
        self.assertEqual(
            rad(html, 0, "Läsfrämjande"), ["", "", "", "", ' class="band start slut"']
        )
        self.assertEqual(
            rad(html, 1, "Läsfrämjande"),
            ["", "", ' class="band start"', ' class="band slut"', ""],
        )

    def test_ny_rubrik_star_under_den_forra(self):
        html = sida()
        self.assertLess(
            html.index('<a href="#mal-0">Trygga miljöer</a>'),
            html.index('<span class="dold">Ny rubrik 2026: </span>'),
        )
        self.assertIn(
            '<a href="#mal-0">Läsfrämjande</a> <small>tolkad</small></th>', html
        )

    def test_ny_formulering_under_samma_rubrik(self):
        rader = GRUPPER.replace(
            f"Trygga miljöer,,,,,{BUDGET}#sida-1-2",
            f"Trygga miljöer,Alla ska känna sig,,,,{BUDGET}#sida-1-2",
        )
        with pool(rader) as malen:
            html = malsida(
                Mall([exempelby()], REPO, TID), exempelby(), malen, protokoll(2022)
            )
        self.assertIn('aria-label="Ny formulering: Alla ska känna sig trygga."', html)
        self.assertEqual(html.count('<span class="ny-formulering" role="img"'), 1)
        self.assertNotIn('class="ny-formulering" role="img"', sida())

    def test_ar_utan_dokument_och_mal_ar_en_lucka(self):
        html = sida()
        self.assertIn(
            '<th scope="col" class="lucka">2023<br><small>lucka</small>', html
        )
        # 2025 och 2026 har mål ur ett senare dokument, men inga egna.
        self.assertIn('<th scope="col">2025</th>', html)
        self.assertNotIn('class="lucka">2026', html)
        self.assertIn('<li class="lucka" title="2023: lucka i poolen">', html)

    def test_namndmal_och_direktiv_var_for_sig(self):
        html = sida()
        self.assertLess(html.index(">Nämndmål</th>"), html.index(">Direktiv</th>"))
        self.assertEqual(html.count("<tr data-mal"), 3)

    def test_ar_med_dokument_men_utan_mal(self):
        self.assertIn("2023<br><small>inga mål</small>", sida((2022, 2023)))

    def test_dokument_fran_ar_fore_malen(self):
        self.assertIn(
            "Poolen har dokument från organet sedan 2020, men inga av nämndens mål "
            "före 2022.",
            sida((2020, 2024)),
        )
        self.assertNotIn("Poolen har dokument", sida())

    def test_spar_med_bada_slagen(self):
        rader = GRUPPER + f"fsn,2027,direktiv,Trygga miljöer,,,,,{BUDGET}#sida-1,,\n"
        with pool(rader) as malen:
            html = malsida(
                Mall([exempelby()], REPO, TID), exempelby(), malen, protokoll(2022)
            )
        self.assertIn("Trygga miljöer</a> <small>nämndmål</small>", html)
        self.assertIn('data-slag="nämndmål direktiv"', html)
        self.assertIn("<span>nämndmål och direktiv</span>", html)
        self.assertIn("<b>2026</b> Läsfrämjande <small>tolkad</small> (nämndmål)", html)

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
        with pool(RADER.replace("direktiv", "nämndmål")) as malen:
            bara = malsida(
                Mall([exempelby()], REPO, TID), exempelby(), malen, protokoll(2024)
            )
        self.assertNotIn('data-urval="direktiv"', bara)
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
