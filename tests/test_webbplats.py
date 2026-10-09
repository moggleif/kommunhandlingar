"""Krav: K7 och K14 i docs/02-KRAV.md. Kod: src/kommunhandlingar/webbplats/."""

import shutil
import tempfile
import unittest
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from kommunhandlingar import frontmatter
from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import las
from kommunhandlingar.webbplats import luckavsnitt, rakning, sidor
from kommunhandlingar.webbplats.bygg import bygg

FIXTURER = Path(__file__).parent / "fixtures"
REPO = "https://github.com/exempel/kommunhandlingar"
TID = datetime(2026, 10, 7, 20, 15, tzinfo=UTC)

DOKUMENT = """---
kommun: exempelby
organ: {organ}
datum: {datum}
lopnr: {lopnr}
typ: {typ}
namn: null
kvalitet: {kvalitet}
fel: null
tal_obekraftade: {tal}
---

# Text
"""


def dokument(organ="fsn", datum="2024-05-02", typ="protokoll", **andra) -> str:
    falt = {"lopnr": "null", "kvalitet": "full", "tal": "[]"} | andra
    return DOKUMENT.format(organ=organ, datum=datum, typ=typ, **falt)


def exempelby():
    return las(FIXTURER / "exempelby.toml")


class TestFrontMatter(unittest.TestCase):
    def test_falten_lases(self):
        falt = frontmatter.las(dokument(tal="[3, 5]"))
        self.assertEqual(falt["organ"], "fsn")
        self.assertEqual(falt["lopnr"], "null")
        self.assertEqual(frontmatter.lista(falt["tal_obekraftade"]), ["3", "5"])

    def test_tom_lista_och_null_ar_inga_sidor(self):
        self.assertEqual(frontmatter.lista("[]"), [])
        self.assertEqual(frontmatter.lista("null"), [])


class TestRakning(unittest.TestCase):
    def rader(self, *texter: str) -> dict:
        dok = [frontmatter.las(text) for text in texter]
        return {rad.id: rad for rad in rakning.rakna(exempelby(), dok, TID.date())}

    def test_organ_i_kommunfilens_ordning(self):
        rader = rakning.rakna(exempelby(), [], TID.date())
        self.assertEqual([rad.id for rad in rader], ["bun", "fsn"])

    def test_dokument_och_sammantraden_raknas_per_organ(self):
        rader = self.rader(
            dokument(typ="protokoll"),
            dokument(typ="kallelse"),
            dokument(datum="2024-06-01"),
            dokument(datum="2024-06-01", lopnr="2"),
        )
        self.assertEqual(rader["fsn"].sammantraden, 3)
        self.assertEqual(rader["fsn"].typer["protokoll"], 3)
        self.assertEqual(rader["fsn"].typer["kallelse"], 1)
        self.assertEqual(rader["bun"].dokument, 0)

    def test_kvalitet_och_obekraftade_sidor(self):
        rader = self.rader(
            dokument(kvalitet="ocr", tal="[1, 2]"),
            dokument(kvalitet="ej-hamtad", tal="null"),
            dokument(kvalitet="full"),
        )
        fsn = rader["fsn"]
        self.assertEqual(fsn.kvaliteter["ocr"], 1)
        self.assertEqual(fsn.kvaliteter["ej-hamtad"], 1)
        self.assertEqual(fsn.kvaliteter["full"], 1)
        self.assertEqual(fsn.obekraftade_sidor, 2)


class TestSidor(unittest.TestCase):
    def statussida(self, *texter: str) -> str:
        kommun = exempelby()
        dok = [frontmatter.las(text) for text in texter]
        mall = sidor.Mall([kommun], REPO, TID)
        return sidor.statussida(mall, kommun, dok)

    def test_organ_utan_dokument_star_med(self):
        html = self.statussida(dokument())
        self.assertIn("Barn- och ungdomsnämnden", html)
        self.assertIn("inget hämtat än", html)

    def test_sammanfattningen(self):
        html = self.statussida(dokument(datum="2023-02-01"), dokument())
        self.assertIn("Dokument: 2", html)
        self.assertIn("2023-02-01", html)
        self.assertIn("2024-05-02", html)

    def test_tom_pool(self):
        html = self.statussida()
        self.assertIn("Dokument: 0", html)
        self.assertEqual(html.count("inget hämtat än"), 4)

    def test_meny_sidfot_och_tid_pa_varje_sida(self):
        mall = sidor.Mall([exempelby()], REPO, TID)
        for html in (sidor.startsida(mall), self.statussida()):
            self.assertIn('href="index.html"', html)
            self.assertIn('href="exempelby.html"', html)
            self.assertIn(f'href="{REPO}"', html)
            self.assertIn("2026-10-07 20:15 UTC", html)

    def test_luckorna_per_organ_med_kallor(self):
        html = self.statussida(
            dokument(typ="kallelse"),
            dokument(typ="protokoll"),
            dokument(datum="2024-06-01", typ="protokoll"),
        )
        self.assertIn('<td class="tal">1</td></tr>', html)
        self.assertIn('<a href="https://exempelby.se/fsn">mötessidan</a>', html)
        self.assertIn("<li>2024-06-01: kallelse och handlingar saknas</li>", html)
        self.assertNotIn("Inga luckor", html)

    def test_arkivet_ar_en_kalla(self):
        kommun = exempelby()
        kalla = replace(kommun.kallor[0], wayback=True)
        html = luckavsnitt.kallor(replace(kommun, kallor=(kalla,)), "fsn")
        self.assertEqual(
            html,
            '<a href="https://exempelby.se/fsn">mötessidan</a> och Internet Archive',
        )

    def test_inga_luckor(self):
        self.assertIn("<p>Inga luckor.</p>", self.statussida(dokument()))

    def test_text_ur_poolen_escapas(self):
        html = self.statussida(dokument(datum="<script>"))
        self.assertNotIn("<script>", html)


class TestBygg(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.rot, self.ut = Path(tmp.name) / "repo", Path(tmp.name) / "ut"
        (self.rot / "kommuner").mkdir(parents=True)
        shutil.copy(FIXTURER / "exempelby.toml", self.rot / "kommuner")

    def spara(self, text: str) -> None:
        mote = self.rot / "data" / "exempelby" / "fsn" / "2024" / "2024-05-02"
        mote.mkdir(parents=True)
        (mote / "protokoll.md").write_text(text, encoding="utf-8")

    def test_webbplatsen_byggs_ur_kommunfilerna_och_poolen(self):
        self.spara(dokument())
        bygg(self.rot, self.ut, REPO, TID)
        self.assertIn("Exempelby kommun", (self.ut / "index.html").read_text())
        self.assertIn("Dokument: 1", (self.ut / "exempelby.html").read_text())

    def test_okant_organ_typ_eller_kvalitet_stoppar_bygget(self):
        self.spara(dokument(organ="nedlagd", typ="beslut", kvalitet="bra"))
        with self.assertRaisesRegex(
            Datafel, r"protokoll\.md.*'nedlagd'.*'beslut'.*'bra'"
        ):
            bygg(self.rot, self.ut, REPO, TID)
