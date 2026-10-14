"""Krav: K33, ADR-0054. Kod: src/kommunhandlingar/webbplats/avvikelser.py och
avvikelsesida.py.

Påhittade issues i mallens form (.github/ISSUE_TEMPLATE/avvikelse.md).
"""

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from kommunhandlingar.konfiguration import las as las_kommun
from kommunhandlingar.webbplats import avvikelser
from kommunhandlingar.webbplats.avvikelsesida import avvikelsesida
from kommunhandlingar.webbplats.mall import Mall

FIXTURER = Path(__file__).parent / "fixtures"
REPO = "https://github.com/exempel/kommunhandlingar"
MALL = Mall(
    [las_kommun(FIXTURER / "exempelby.toml")], REPO, datetime(2026, 10, 14, tzinfo=UTC)
)


def issue(status: str, nummer: int = 7, **andra) -> dict:
    text = (
        "**Kommun:** Exempelby\r\n**Organ och möte:** Nämnden, 2024-05-02\r\n"
        f"**Status:** {status}\r\n\r\n<!-- Mallens hjälptext. -->\r\n"
        "## Vad som skiljer sig\r\n\r\nRubriken säger 2023.\r\n\r\n"
        "## Belägg\r\n\r\n- Sida 1.\r\n\r\n## Att undersöka\r\n\r\nInget.\r\n"
    )
    return {
        "number": nummer,
        "title": "Avvikelse: Nämnden 2024-05-02 – fel år",
        "html_url": f"https://github.com/exempel/kommunhandlingar/issues/{nummer}",
        "body": text,
    } | andra


class TestTolka(unittest.TestCase):
    def test_falten_och_avsnitten_ur_mallen(self):
        a = avvikelser.tolka(issue("att undersöka 2026-10-13"))
        self.assertEqual(
            (a.nummer, a.rubrik, a.kommun, a.mote),
            (7, "Nämnden 2024-05-02 – fel år", "Exempelby", "Nämnden, 2024-05-02"),
        )
        self.assertIn("#### Vad som skiljer sig", a.beskrivning)
        self.assertIn("#### Belägg", a.beskrivning)
        self.assertNotIn("Att undersöka", a.beskrivning)
        self.assertNotIn("hjälptext", a.beskrivning)

    def test_det_senaste_steget_pa_statusraden_avgor(self):
        fall = {
            "att undersöka 2026-10-13": "Att undersöka",
            "att undersöka 2026-10-13, undersökt – fel hos kommunen 2026-10-14": (
                "Ska meddelas kommunen"
            ),
            "att undersöka 2026-10-13, undersökt – fel hos kommunen 2026-10-14, "
            "e-post skickad 2026-10-20": "Väntar på kommunen",
        }
        for status, lage in fall.items():
            with self.subTest(status):
                self.assertEqual(avvikelser.tolka(issue(status)).lage, lage)

    def test_status_som_inte_gar_att_lasa_marks(self):
        for status in ("att undersöka", "något annat 2026-10-13", ""):
            with self.subTest(status):
                self.assertEqual(avvikelser.tolka(issue(status)).lage, avvikelser.OKANT)

    def test_issue_utan_text(self):
        a = avvikelser.tolka(issue("", body=None))
        self.assertEqual((a.kommun, a.lage, a.beskrivning), ("", avvikelser.OKANT, ""))

    def test_filen_har_ett_issue_per_rad(self):
        with tempfile.TemporaryDirectory() as tmp:
            fil = Path(tmp) / "avvikelser.jsonl"
            rader = [json.dumps(issue("att undersöka 2026-10-13", n)) for n in (1, 2)]
            fil.write_text("\n".join(rader) + "\n", encoding="utf-8")
            self.assertEqual([a.nummer for a in avvikelser.las(fil)], [1, 2])


class TestSidan(unittest.TestCase):
    def sida(self, *issues: dict) -> str:
        return avvikelsesida(MALL, [avvikelser.tolka(i) for i in issues])

    def test_avvikelserna_grupperas_efter_lage(self):
        html = self.sida(
            issue("att undersöka 2026-10-13", 1),
            issue("undersökt – fel hos kommunen 2026-10-14", 2),
        )
        self.assertLess(
            html.index("Ska meddelas kommunen (1)"), html.index("/issues/2")
        )
        self.assertLess(html.index("/issues/2"), html.index("Väntar på kommunen (0)"))
        self.assertLess(html.index("Att undersöka (1)"), html.index("/issues/1"))
        self.assertIn("<h4>Belägg</h4>", html)
        self.assertNotIn(avvikelser.OKANT, html)

    def test_status_som_inte_gar_att_lasa_far_ett_eget_avsnitt(self):
        self.assertIn(f"{avvikelser.OKANT} (1)", self.sida(issue("")))

    def test_text_ur_issuet_blir_aldrig_markup(self):
        html = self.sida(
            issue(
                "att undersöka 2026-10-13",
                title="<script>x</script>",
                body="**Kommun:** <b>A</b>\n## Belägg\n<img src=x> [l](javascript:x)\n"
                "![bild](https://example.com/p.png)\n",
            )
        )
        self.assertNotIn("<script>", html)
        self.assertNotIn("<b>A", html)
        self.assertNotIn("<img", html)
        self.assertNotIn('href="javascript', html)

    def test_menyn_har_sidan(self):
        self.assertIn('href="avvikelser.html" aria-current="page"', self.sida())


if __name__ == "__main__":
    unittest.main()
