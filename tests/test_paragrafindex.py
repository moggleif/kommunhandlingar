"""Krav: K48, ADR-0071. Kod: src/kommunhandlingar/webbplats/paragrafindex.py och
länken i src/kommunhandlingar/webbplats/llms.py."""

import json

from tests.test_dokumentindex import MOTE, TestIndex
from tests.test_webbplats import dokument

TEXT = "<!-- sida 1 -->\n\nFörsättsblad\n\n<!-- sida 2 -->\n\n"
TEXT += "§ 4 Dnr XN-2024-00012\nLokalbehov\n\nBeslut\n\nNämnden godkänner.\n"


class TestParagrafindex(TestIndex):
    def paragrafer(self) -> list[dict]:
        self.index()
        fil = self.ut / "exempelby" / "paragrafer.jsonl"
        return [json.loads(rad) for rad in fil.read_text(encoding="utf-8").splitlines()]

    def test_en_rad_per_paragraf_med_var_den_star(self):
        self.spara("protokoll.md", dokument(text=TEXT, tal="[2]"))
        self.assertEqual(
            self.paragrafer(),
            [
                {
                    "organ": "fsn",
                    "datum": "2024-05-02",
                    "lopnr": None,
                    "paragraf": 4,
                    "rubrik": "Lokalbehov",
                    "diarienummer": ["XN-2024-00012"],
                    "beslut": "Nämnden godkänner.",
                    "sidnummer": 2,
                    "kvalitet": "ok",
                    "tal_obekraftade": True,
                    "fil": f"data/exempelby/{MOTE.as_posix()}/protokoll.md",
                    "sida": f"exempelby/{MOTE.as_posix()}/protokoll.html#sida-2",
                }
            ],
        )

    def test_bara_protokoll(self):
        self.spara("kallelse.md", dokument(typ="kallelse", text=TEXT))
        self.assertEqual(self.paragrafer(), [])

    def test_llms_lankar_till_paragraferna(self):
        self.spara("protokoll.md", dokument())
        self.assertIn("(exempelby/paragrafer.jsonl)", self.llms())
