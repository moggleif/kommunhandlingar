"""Krav: K62, ADR-0089. Kod: src/kommunhandlingar/webbplats/sokindex.py."""

import json

from tests.test_dokumentindex import Index
from tests.test_paragrafindex import TEXT
from tests.test_webbplats import dokument

ANDRA = "<!-- sida 1 -->\n\n§ 7 Dnr XN-2025-00003\nSkolskjuts\n\nBeslut\n\nBifalls.\n"


class TestSokindex(Index):
    def sokindex(self) -> dict:
        self.index()
        return json.loads((self.ut / "sok.json").read_text(encoding="utf-8"))

    def test_protokollens_paragrafer_nyast_forst_i_giffas_format(self):
        self.spara("protokoll.md", dokument(text=TEXT, tal="[2]"))
        nyare = self.rot / "data" / "exempelby" / "fsn" / "2025" / "2025-01-15"
        nyare.mkdir(parents=True)
        text = dokument(datum="2025-01-15", text=ANDRA)
        (nyare / "protokoll.md").write_text(text, encoding="utf-8")
        grupp = self.sokindex()["grupper"][0]
        self.assertEqual(grupp["rubrik"], "Protokollen i Exempelby kommun")
        self.assertEqual(
            [p["rubrik"] for p in grupp["poster"]], ["Skolskjuts", "Lokalbehov"]
        )
        self.assertEqual(
            grupp["poster"][1],
            {
                "rubrik": "Lokalbehov",
                "adress": "exempelby/fsn/2024/2024-05-02/protokoll.html#sida-2",
                "om": [
                    "Förskole- och skolnämnden",
                    "2 maj 2024",
                    "§ 4",
                    "Dnr XN-2024-00012",
                ],
                "traff": "lokalbehov xn-2024-00012 förskole- och skolnämnden",
            },
        )

    def test_utan_protokoll_en_tom_grupp(self):
        self.spara("kallelse.md", dokument(typ="kallelse"))
        self.assertEqual(self.sokindex()["grupper"][0]["poster"], [])
