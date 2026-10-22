"""Krav: K35 i docs/02-KRAV.md, ADR-0056. Kod:
src/kommunhandlingar/webbplats/mal.py, malkontroll.py, malspar.py,
maltidslinje.py, malkort.py, malstatistik.py och malsida.py."""

import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from kommunhandlingar.fel import Datafel
from kommunhandlingar.webbplats import mal
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.malsida import malsida
from tests.test_mal import RUBRIK
from tests.test_webbplats import REPO, TID, dokument, exempelby, protokoll

BUDGET = "fsn/2024/2024-05-02/handlingar.md"
AR = "fsn/2025/2025-04-08/handlingar.md"
# Budgeten sätter målet i versaler; årsredovisningen har fokusområdena i en
# tabell där trendpilen hamnar mitt i texten och ett ord delas i cellen.
BUDGETTEXT = """<!-- sida 1 -->

EN ATTRAKTIV KOMMUN  ATT BO

Fokusområden
• Trygga miljöer för
alla.
• Goda bo­städer.

<!-- sida 2 -->

Direktiv – Civil beredskap
"""
ARTEXT = """<!-- sida 1 -->

Mål: En attraktiv kommun att bo

| Fokusområden Trend |  |
| --- | --- |
| Trygga miljöer för → alla. | → |
| Goda bo-<br>städer för fler. | – |

Den samlade bedömningen är att vi inte nått målet.
"""
MALET = "En attraktiv kommun att bo"
TRYGGA = "Trygga miljöer för alla."
RADER = (
    f"fsn,2024,kommunmål,{MALET},,,,,{BUDGET}#sida-1,,,\n"
    f"fsn,2024,fokusområde,Trygga miljöer för alla.,,,,,{BUDGET}#sida-1,,,{MALET}\n"
    f"fsn,2024,fokusområde,Goda bostäder.,,,,,{BUDGET}#sida-1,,,{MALET}\n"
    f"fsn,2024,direktiv,Civil beredskap,,,,,{BUDGET}#sida-2,,,\n"
    f"fsn,2024,kommunmål,{MALET},,Den samlade bedömningen är att vi inte nått "
    f"målet.,utfall,ej,{AR}#sida-1,,,\n"
    f"fsn,2024,fokusområde,Trygga miljöer för alla.,,,utfall,delvis,{AR}#sida-1,,,"
    f"{MALET}\n"
    f"fsn,2024,fokusområde,Goda bostäder för fler.,,,utfall,uppnatt,{AR}#sida-1,"
    f"Goda bostäder.,ja,{MALET}\n"
)


@contextmanager
def pool(rader: str = RADER):
    with tempfile.TemporaryDirectory() as tmp:
        fil, data = Path(tmp) / "exempelby.csv", Path(tmp) / "data"
        fil.write_text(RUBRIK + rader, encoding="utf-8")
        for kalla, text in ((BUDGET, BUDGETTEXT), (AR, ARTEXT)):
            (data / kalla).parent.mkdir(parents=True)
            (data / kalla).write_text(
                dokument(text=text, typ="handlingar", per_sida="[ok, ok]"),
                encoding="utf-8",
            )
        yield mal.las(fil, exempelby(), data)


def sida(rader: str = RADER) -> str:
    with pool(rader) as malen:
        mall = Mall([exempelby()], REPO, TID)
        return malsida(mall, exempelby(), malen, protokoll(2024, 2025))


class TestLasning(unittest.TestCase):
    def stoppas(self, rader: str) -> str:
        with self.assertRaises(Datafel) as fel, pool(rader):
            pass
        return str(fel.exception)

    def test_raderna_lases_med_versaler_pilar_och_delade_ord(self):
        with pool() as malen:
            self.assertEqual(len(malen), 7)
            self.assertEqual(malen[1].huvudmal, MALET)

    def test_versaler_i_en_del_av_rubriken_raknas(self):
        rad = f"fsn,2024,kommunmål,EN attraktiv kommun att bo,,,,,{AR}#sida-1,,,\n"
        self.assertIn("rubriken", self.stoppas(rad))

    def test_fokusomrade_utan_huvudmal(self):
        rad = f"fsn,2024,fokusområde,Goda bostäder.,,,,,{BUDGET}#sida-1,,,\n"
        self.assertIn("huvudmål", self.stoppas(rad))

    def test_huvudmal_pa_annat_an_ett_fokusomrade(self):
        rad = f"fsn,2024,direktiv,Civil beredskap,,,,,{BUDGET}#sida-2,,,{MALET}\n"
        self.assertIn("huvudmål", self.stoppas(rad))

    def test_huvudmal_som_inte_star_pa_sidan(self):
        rad = f"fsn,2024,fokusområde,Civil beredskap,,,,,{BUDGET}#sida-2,,,{MALET}\n"
        self.assertIn("huvudmålet står inte", self.stoppas(rad))

    def test_huvudmal_som_inte_ar_ett_kommunmal(self):
        rad = (
            f"fsn,2024,nämndmål,Trygga miljöer för alla.,,,,,{BUDGET}#sida-1,,,\n"
            f"fsn,2024,fokusområde,Goda bostäder.,,,,,{BUDGET}#sida-1,,,"
            "Trygga miljöer för alla.\n"
        )
        self.assertIn("inget kommunmål", self.stoppas(rad))

    def test_samma_rubrik_med_annat_huvudmal(self):
        andra = "Goda bostäder för fler."
        rader = (
            f"fsn,2024,kommunmål,{MALET},,,,,{BUDGET}#sida-1,,,\n"
            f"fsn,2024,kommunmål,{andra},,,,,{AR}#sida-1,,,\n"
            f"fsn,2024,fokusområde,{TRYGGA},,,,,{BUDGET}#sida-1,,,{MALET}\n"
            f"fsn,2024,fokusområde,{TRYGGA},,,,,{AR}#sida-1,,,{andra}\n"
        )
        self.assertIn("huvudmål tidigare", self.stoppas(rader))

    def test_tva_rubriker_i_samma_spar_ur_samma_dokument(self):
        rader = (
            f"fsn,2024,kommunmål,{MALET},,,,,{BUDGET}#sida-1,,,\n"
            f"fsn,2024,fokusområde,Goda bostäder.,,,,,{BUDGET}#sida-1,,,{MALET}\n"
            f"fsn,2024,fokusområde,Trygga miljöer för alla.,,,,,{BUDGET}#sida-1,"
            f"Goda bostäder.,ja,{MALET}\n"
        )
        self.assertIn("samma dokument", self.stoppas(rader))


class TestSidan(unittest.TestCase):
    def test_fokusomradena_star_under_sitt_mal_i_tidslinjen(self):
        html = sida()
        malet = html.index(f'<a href="#mal-0">{MALET}</a>')
        trygga = html.index('<th scope="row" class="fokus">', malet)
        direktiv = html.index("Civil beredskap</a>")
        self.assertLess(trygga, direktiv)
        self.assertNotIn(">Fokusområde</th>", html)
        self.assertIn('<span class="dold">Fokusområde: </span>', html)

    def test_budgetens_och_uppfoljningens_rubrik_har_var_sin_rad(self):
        html = sida()
        self.assertIn(">Goda bostäder.</a></th>", html)
        self.assertIn(">Goda bostäder för fler.</a> <small>tolkad</small></th>", html)

    def test_malets_kort_har_fokusomradenas_kort(self):
        html = sida()
        kort = html.split('<article id="mal-0"')[1]
        fokus = kort.split('<div class="fokusomraden">')[1].split(
            '<article id="mal-3"'
        )[0]
        self.assertEqual(fokus.count("<article"), 2)
        self.assertEqual(html.count('<div class="fokusomraden">'), 1)

    def test_farg_utan_status(self):
        html = sida()
        self.assertIn("delvis uppnått eller på väg, enligt färgen i källan", html)
        self.assertIn("Den samlade bedömningen är att vi inte nått målet.", html)

    def test_antal_per_slag_som_finns(self):
        html = sida()
        for rubrik in ("Kommunmål", "Fokusområden", "Direktiv"):
            self.assertIn(f'<th scope="col">{rubrik}</th>', html)
        self.assertNotIn('<th scope="col">Nämndmål</th>', html)
        self.assertIn("<dt>fokusområden</dt><dd>2</dd>", html)

    def test_fyra_slag_har_var_sin_linje(self):
        rad = f"fsn,2025,nämndmål,Civil beredskap,,,,,{BUDGET}#sida-2,,,\n"
        graf = sida(RADER + rad).split('<svg class="graf"')[1].split("</svg>")[0]
        self.assertEqual(graf.count("<polyline"), 4)
        self.assertIn('stroke-dasharray="8 3 2 3"', graf)

    def test_om_sidan_forklarar_fargen(self):
        self.assertIn("Färgen följer inte med in i texten", sida())
