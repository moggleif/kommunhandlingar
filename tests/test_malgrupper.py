"""Krav: K27 i docs/02-KRAV.md, ADR-0045. Kod: src/kommunhandlingar/webbplats/
malkontroll.py, malsida.py, malavsnitt.py, malstatistik.py och malgraf.py."""

import re
import unittest

from kommunhandlingar.fel import Datafel
from kommunhandlingar.webbplats import malgraf
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.malsida import malsida
from tests.test_mal import BUDGET, HANDLINGAR, RADER, pool
from tests.test_webbplats import REPO, TID, exempelby


class TestGrupper(unittest.TestCase):
    def stoppas(self, rader: str) -> str:
        with self.assertRaises(Datafel) as fel, pool(rader):
            pass
        return str(fel.exception)

    def test_grupp_och_tolkad_lases(self):
        rad = f"fsn,2023,nämndmål,Läsfrämjande,,,{BUDGET}#sida-2,Trygga miljöer,ja\n"
        with pool(RADER + rad) as malen:
            self.assertEqual(malen[3].spar, malen[0].spar)
            self.assertNotEqual(malen[3].spar, malen[1].spar)

    def test_grupp_som_inte_ar_en_rubrik(self):
        rad = f"fsn,2023,nämndmål,Läsfrämjande,,,{BUDGET}#sida-2,Trygga,\n"
        self.assertIn("'Trygga' är ingen rubrik", self.stoppas(RADER + rad))

    def test_tolkad_utan_grupp_eller_med_annat_varde(self):
        rad = f"fsn,2023,nämndmål,Läsfrämjande,,,{BUDGET}#sida-2,,ja\n"
        self.assertIn("tolkad", self.stoppas(RADER + rad))
        rad = rad.replace(",,ja", ",Trygga miljöer,nej")
        self.assertIn("'nej'", self.stoppas(RADER + rad))

    def test_samma_rubrik_med_tva_grupper(self):
        rad = f"fsn,2023,direktiv,Läsfrämjande,,,{BUDGET}#sida-1-2,Trygga miljöer,\n"
        self.assertIn("rad 5: rubriken har en annan grupp", self.stoppas(RADER + rad))

    def test_status_utan_ikon(self):
        rad = f"fsn,2024,direktiv,Läsfrämjande,,Status,{BUDGET}#sida-2,,\n"
        fel = self.stoppas(rad)
        self.assertIn("'Status' har ingen ikon", fel)

    def test_protokollet_gar_fore_handlingarna(self):
        rad = f"fsn,2025,nämndmål,Trygga miljöer,,,{HANDLINGAR}#sida-1,,\n"
        self.assertIn("bara protokollets rad", self.stoppas(RADER + rad))
        rad = rad.replace("2025", "2026")
        with pool(RADER + rad) as malen:
            self.assertEqual(len(malen), 4)


class TestStatistik(unittest.TestCase):
    RADER = RADER + (
        f"fsn,2026,nämndmål,Läsfrämjande,,,{BUDGET}#sida-2,Trygga miljöer,ja\n"
        f"fsn,2022,nämndmål,Trygga miljöer,,,{BUDGET}#sida-1-2,,\n"
    )

    def sida(self) -> str:
        with pool(self.RADER) as malen:
            mall = Mall([exempelby()], REPO, TID)
            return malsida(mall, exempelby(), malen, {2022})

    def test_omdopta_rubriker_under_varandra(self):
        html = self.sida()
        grupp = html[html.index("<tbody>") : html.index("</tbody>")]
        self.assertIn("Trygga miljöer</button> (nämndmål)</th>", grupp)
        self.assertIn("↳ <button", grupp)
        self.assertIn("Läsfrämjande</button> (nämndmål) <small>tolkad</small>", grupp)
        self.assertIn("Samma spår som Trygga miljöer, tolkad", html)

    def test_antal_per_ar_med_lucka(self):
        html = self.sida()
        tabell = html[html.index('id="antal"') : html.index('id="ar-')]
        rader = re.findall(r'<tr><th scope="row">(\d+)</th>(.*?)</tr>', tabell)
        tal = {ar: re.findall(r'"tal">(.*?)<', celler) for ar, celler in rader}
        self.assertEqual(tal["2022"], ["1", "0", "1", "0"])
        self.assertEqual(tal["2023"], ["–"] * 4)
        self.assertEqual(tal["2024"], ["0", "1", "1", "1"])
        self.assertEqual(tal["2025"], ["1", "1", "0", "0"])

    def test_grafen_bryts_vid_ar_utan_varden(self):
        graf = malgraf.graf([2022, 2023, 2024, 2025], [("A", [1, None, 2, 3])])
        self.assertEqual(graf.count("<polyline"), 2)
        self.assertEqual(graf.count('r="4"'), 3 + 1)
        self.assertIn('role="img"', graf)
