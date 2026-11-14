"""Krav: K47 i docs/02-KRAV.md. Kod: src/kommunhandlingar/webbplats/dokumentindex.py,
src/kommunhandlingar/webbplats/llms.py."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from kommunhandlingar.frontmatter import FALT
from kommunhandlingar.webbplats.bygg import bygg
from kommunhandlingar.webbplats.llms import handskrivna
from kommunhandlingar.webbplats.mall import Mall
from tests.test_webbplats import FIXTURER, REPO, TID, dokument

MOTE = Path("fsn") / "2024" / "2024-05-02"


class TestIndex(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.rot, self.ut = Path(tmp.name) / "repo", Path(tmp.name) / "ut"
        (self.rot / "kommuner").mkdir(parents=True)
        shutil.copy(FIXTURER / "exempelby.toml", self.rot / "kommuner")
        self.mote = self.rot / "data" / "exempelby" / MOTE
        self.mote.mkdir(parents=True)

    def spara(self, namn: str, text: str) -> None:
        (self.mote / namn).write_text(text, encoding="utf-8")

    def index(self) -> list[dict]:
        bygg(self.rot, self.ut, REPO, TID)
        text = (self.ut / "exempelby" / "index.jsonl").read_text(encoding="utf-8")
        return [json.loads(rad) for rad in text.splitlines()]

    def llms(self) -> str:
        bygg(self.rot, self.ut, REPO, TID)
        return (self.ut / "llms.txt").read_text(encoding="utf-8")

    def test_en_rad_per_dokument_i_sokvagarnas_ordning(self):
        self.spara("protokoll.md", dokument())
        self.spara("kallelse.md", dokument(typ="kallelse"))
        self.assertEqual([r["typ"] for r in self.index()], ["kallelse", "protokoll"])

    def test_hela_front_matter_med_json_typer(self):
        self.spara("protokoll.md", dokument(lopnr="2", tal="[1, 2]"))
        rad = self.index()[0]
        self.assertEqual(rad["lopnr"], 2)
        self.assertEqual(rad["sidor"], 2)
        self.assertEqual(rad["tal_obekraftade"], [1, 2])
        self.assertEqual(rad["kvalitet_per_sida"], ["ok", "ok"])
        self.assertEqual(rad["tidigare_kallnycklar"], [])
        self.assertIsNone(rad["arenden"])
        self.assertIsNone(rad["figurer"])
        self.assertEqual(rad["datum"], "2024-05-02")
        self.assertEqual(list(rad), [*FALT, "fil", "sida", "tabeller"])

    def test_ett_dokument_i_delar_har_listor(self):
        text = dokument().replace("bytes: 1000", "bytes: [600, 400]")
        self.spara("protokoll.md", text.replace("sha256: 3f9a", "sha256: [3f9a, 4e1b]"))
        rad = self.index()[0]
        self.assertEqual(rad["bytes"], [600, 400])
        self.assertEqual(rad["sha256"], ["3f9a", "4e1b"])

    def test_sokvagen_sidan_och_tabellerna(self):
        self.spara("protokoll.md", dokument())
        tabeller = self.mote / "protokoll.tabeller"
        tabeller.mkdir()
        for namn in ("2-1.csv", "1-1.csv"):
            (tabeller / namn).write_text("a\n", encoding="utf-8")
        rad = self.index()[0]
        self.assertEqual(rad["fil"], f"data/exempelby/{MOTE.as_posix()}/protokoll.md")
        self.assertEqual(rad["sida"], f"exempelby/{MOTE.as_posix()}/protokoll.html")
        self.assertEqual(rad["tabeller"], ["1-1.csv", "2-1.csv"])

    def test_dokument_utan_tabeller(self):
        self.spara("protokoll.md", dokument())
        self.assertEqual(self.index()[0]["tabeller"], [])

    def test_llms_txt_pekar_in_i_poolen(self):
        text = self.llms()
        self.assertTrue(text.startswith("# kommunhandlingar\n\n> "))
        self.assertIn("`tal_obekraftade`", text)
        self.assertIn(f"{REPO}/blob/main/docs/03-ARKITEKTUR.md#front-matter", text)
        self.assertIn("## Exempelby kommun", text)
        self.assertIn("(exempelby/index.jsonl)", text)
        self.assertIn("[Översikt](exempelby.html)", text)
        self.assertLess(
            text.index("[Barn- och ungdomsnämnden](exempelby/bun.html)"),
            text.index("[Förskole- och skolnämnden](exempelby/fsn.html)"),
        )

    def test_llms_txt_lankar_filerna_skrivna_for_hand_som_finns(self):
        (self.rot / "kalender").mkdir()
        (self.rot / "kalender" / "exempelby.csv").write_text(
            "organ,datum,tid,plats,kalla,osakert\n", encoding="utf-8"
        )
        text = self.llms()
        self.assertIn(f"({REPO}/raw/main/kalender/exempelby.csv)", text)
        self.assertNotIn("/raw/main/mal/", text)


class TestHandskrivna(unittest.TestCase):
    def test_alla_slag_i_ordning_och_bara_de_som_finns(self):
        alla = {"exempelby": []}
        mall = Mall(
            [],
            REPO,
            TID,
            kalendrar=frozenset({"exempelby"}),
            malen=alla,
            uppfoljningar=alla,
            spar={"lokalbehov": alla, "granskningar": alla, "initiativ": {}},
            projekt=alla,
        )
        self.assertEqual(
            [katalog for katalog, _ in handskrivna(mall, "exempelby")],
            [
                "kalender",
                "mal",
                "uppfoljningar",
                "lokalbehov",
                "granskningar",
                "projekt",
            ],
        )
        self.assertEqual(handskrivna(mall, "annanby"), [])


if __name__ == "__main__":
    unittest.main()
