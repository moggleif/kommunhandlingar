"""Krav: K17 i docs/02-KRAV.md, ADR-0022. Kod: src/kommunhandlingar/webbplats/."""

import shutil
import tempfile
import unittest
from pathlib import Path

from kommunhandlingar import frontmatter
from kommunhandlingar.webbplats import rakning
from kommunhandlingar.webbplats.bygg import bygg
from kommunhandlingar.webbplats.dokumentsida import dokumentsida
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.organsida import organsida
from tests.test_webbplats import FIXTURER, REPO, TID, dokument, exempelby

TABELL = """<!-- sida 1 -->

Text

[Tabell 1-1](protokoll.tabeller/1-1.csv)

| Belopp | År |
| --- | --- |
| 1 200 | 2024 |

<!-- sida 2 -->

````osaker-tabell
Exempel   86%
````
"""


def las(text: str, adress: str = "fsn/2024/2024-05-02/protokoll.html") -> dict:
    return frontmatter.las(text) | {"adress": adress}


class TestOrgansida(unittest.TestCase):
    def organsida(self, *dok: dict) -> str:
        kommun = exempelby()
        rad = next(
            r for r in rakning.rakna(kommun, list(dok), TID.date()) if r.id == "fsn"
        )
        return organsida(Mall([kommun], REPO, TID), kommun, rad, list(dok))

    def test_sammantraden_per_ar_nyast_forst(self):
        html = self.organsida(
            las(dokument(datum="2023-02-01")),
            las(dokument(datum="2024-05-02")),
            las(dokument(datum="2024-05-02", lopnr="2")),
        )
        ordning = [
            html.index(t)
            for t in ("<h2>2024", '"2024-05-02-2"', '"2024-05-02"', "<h2>2023")
        ]
        self.assertEqual(ordning, sorted(ordning))

    def test_dokumenten_lankas_med_typ_och_kvalitet(self):
        html = self.organsida(las(dokument(kvalitet="ocr", tal="[1, 2]")))
        self.assertIn(
            '<a href="fsn/2024/2024-05-02/protokoll.html">protokoll</a>', html
        )
        self.assertIn("kvalitet ocr, obekräftade tal på 2 sidor", html)

    def test_dokument_utan_namn_fore_de_namngivna(self):
        html = self.organsida(
            las(
                dokument(namn="a-bilaga"), "fsn/2024/2024-05-02/protokoll-a-bilaga.html"
            ),
            las(dokument()),
        )
        self.assertLess(html.index(">protokoll<"), html.index(">protokoll – a-bilaga<"))

    def test_luckan_star_vid_sammantradet(self):
        html = self.organsida(
            las(dokument(datum="2024-05-02", typ="kallelse")),
            las(dokument(datum="2024-06-01", typ="kallelse")),
            las(dokument(datum="2024-06-01", typ="protokoll")),
        )
        motet = html[html.index('id="2024-05-02"') :]
        self.assertIn("<li>protokoll saknas</li>", motet)

    def test_ej_hamtad_syns_med_felet(self):
        html = self.organsida(las(dokument(kvalitet="ej-hamtad", fel="robots")))
        self.assertIn(
            'kvalitet ej-hamtad, fel robots, <a href="https://exempelby.se/protokoll.pdf">'
            "källan</a>",
            html,
        )

    def test_organ_utan_dokument(self):
        self.assertIn("Inget hämtat än.", self.organsida())


class TestDokumentsida(unittest.TestCase):
    def dokumentsida(self, text: str) -> str:
        kommun = exempelby()
        return dokumentsida(Mall([kommun], REPO, TID), kommun, las(text), text)

    def test_harkomsten_med_kallan_och_filen_i_repot(self):
        html = self.dokumentsida(dokument())
        self.assertIn('<a href="https://exempelby.se/protokoll.pdf">', html)
        md = f"{REPO}/blob/main/data/exempelby/fsn/2024/2024-05-02/protokoll.md"
        self.assertIn(f'<a href="{md}">', html)
        self.assertIn("Förskole- och skolnämnden 2024-05-02: protokoll", html)

    def test_varje_sida_har_rubrik_och_kvalitet(self):
        html = self.dokumentsida(dokument(per_sida="[ok, ocr]", tal="[2]"))
        self.assertIn(
            '<h2 id="sida-1">Sida 1</h2><p class="markering">Kvalitet: ok.</p>', html
        )
        self.assertIn("Kvalitet: ocr. Talen på sidan är obekräftade.", html)
        self.assertIn('<a href="#sida-2">2</a>', html)

    def test_saker_tabell_med_lank_till_csv(self):
        html = self.dokumentsida(dokument(text=TABELL))
        self.assertIn('<a href="protokoll.tabeller/1-1.csv">Tabell 1-1</a>', html)
        self.assertIn("<td>1 200</td>", html)

    def test_osaker_tabell_marks(self):
        html = self.dokumentsida(dokument(text=TABELL))
        self.assertIn("Osäker tabell, med uppställningen som på sidan:", html)
        self.assertIn("Exempel   86%", html)

    def test_html_i_texten_blir_text(self):
        text = "<!-- sida 1 -->\n\n<script>alert(1)</script>\n\n<!-- sida 2 -->\n"
        html = self.dokumentsida(dokument(text=text))
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_kalla_som_inte_ar_webbadress_lankas_inte(self):
        html = self.dokumentsida(dokument(url="javascript:alert(1)"))
        self.assertNotIn('href="javascript', html)

    def test_ej_hamtad_utan_text(self):
        html = self.dokumentsida(
            dokument(
                kvalitet="ej-hamtad", fel="robots", per_sida="null", tal="null", text=""
            )
        )
        self.assertIn("Dokumentet har ingen text.", html)
        self.assertIn("<dt>fel</dt><dd>robots</dd>", html)


class TestBygg(unittest.TestCase):
    def test_organsidor_dokumentsidor_och_tabeller(self):
        with tempfile.TemporaryDirectory() as tmp:
            rot, ut = Path(tmp) / "repo", Path(tmp) / "ut"
            (rot / "kommuner").mkdir(parents=True)
            shutil.copy(FIXTURER / "exempelby.toml", rot / "kommuner")
            mote = rot / "data" / "exempelby" / "fsn" / "2024" / "2024-05-02"
            (mote / "protokoll.tabeller").mkdir(parents=True)
            (mote / "protokoll.md").write_text(dokument(text=TABELL), encoding="utf-8")
            (mote / "protokoll.tabeller" / "1-1.csv").write_text("Belopp,År\n")
            bygg(rot, ut, REPO, TID)
            sida = ut / "exempelby" / "fsn" / "2024" / "2024-05-02"
            self.assertIn(
                'href="../../../../index.html"', (sida / "protokoll.html").read_text()
            )
            self.assertEqual(
                (sida / "protokoll.tabeller" / "1-1.csv").read_text(), "Belopp,År\n"
            )
            self.assertIn(
                "Inget hämtat än.", (ut / "exempelby" / "bun.html").read_text()
            )
            self.assertIn(
                'href="exempelby/fsn.html"', (ut / "exempelby.html").read_text()
            )
