"""Krav: K54 i docs/02-KRAV.md, ADR-0078. Kod: src/kommunhandlingar/webbplats/
sammantrade.py, sammantradessida.py, punktkort.py och organsida.py."""

import unittest

from kommunhandlingar.webbplats.bygg import bygg
from kommunhandlingar.webbplats.dagordning import Punkt
from kommunhandlingar.webbplats.punktkort import Lankar, punktkort, sammanfattning
from kommunhandlingar.webbplats.sammantrade import Arende
from kommunhandlingar.webbplats.sammantradessida import dagordningen
from tests.test_dokumentindex import Index
from tests.test_webbplats import REPO, TID, dokument

FORSLAG = "Förslag till beslut<br>Nämnden godkänner<br>lokalbehovet."
KALLELSE = f"""<!-- sida 1 -->

| | Ärende | Beteckning | Förslag |
| --- | --- | --- | --- |
| 1. | Ny skola i<br>Exempelby | 2024-00012 | {FORSLAG} |
| 2. | Information | 2024-00004 |  |

3\\. Budget för 2024-00020 Förslag till beslut
"""
HANDLINGAR = (
    KALLELSE
    + """
<!-- sida 2 -->

TJÄNSTESKRIVELSE
Diarienummer
FSN-2024-00012

Sammanfattning av ärendet

Skolan behöver fler platser.
1 (1)
"""
)
PROTOKOLL = """<!-- sida 1 -->

§ 4 Dnr FSN-2024-00012
Ny skola i Exempelby

Beslut

Nämnden godkänner lokalbehovet.

Expediering

<!-- sida 2 -->

§ 5 Dnr FSN-2024-00004
Information

Beslut

Nämnden noterar informationen.

Expediering

§ 6 Dnr FSN-2024-00020
Budget för 2025

Beslut

Nämnden antar budgeten.

Expediering
"""
TIDIGARE = "<!-- sida 1 -->\n\n§ 9 Dnr FSN-2024-00012\nLokalbehovet anmäls\n"


class TestSammantradessida(Index):
    def setUp(self):
        super().setUp()
        toml = self.rot / "kommuner" / "exempelby.toml"
        text = toml.read_text(encoding="utf-8")
        text = text.replace(
            'foregangare = ["bun"]', 'foregangare = ["bun"]\nsammantradessidor = 2024'
        )
        toml.write_text(text, encoding="utf-8")

    def bygg(self) -> str:
        self.spara(
            "kallelse.md", dokument(typ="kallelse", text=KALLELSE, per_sida="[ok]")
        )
        self.spara("handlingar.md", dokument(typ="handlingar", text=HANDLINGAR))
        self.spara("protokoll.md", dokument(text=PROTOKOLL))
        tidigare = self.rot / "data" / "exempelby" / "fsn" / "2024" / "2024-03-01"
        tidigare.mkdir(parents=True)
        (tidigare / "protokoll.md").write_text(
            dokument(datum="2024-03-01", text=TIDIGARE, per_sida="[ok]"),
            encoding="utf-8",
        )
        bygg(self.rot, self.ut, REPO, TID)
        sidan = self.ut / "exempelby" / "fsn" / "2024" / "2024-05-02.html"
        return sidan.read_text(encoding="utf-8")

    def punkt(self, nummer: int) -> str:
        html = self.bygg()
        return html.split(f'<article id="punkt-{nummer}">')[1].split("</article>")[0]

    def test_en_rad_per_dokument_och_en_punkt_i_taget(self):
        html = self.bygg()
        self.assertIn(
            'href="../../../exempelby/fsn/2024/2024-05-02/kallelse.html"', html
        )
        self.assertIn("Dagordningen, 3 punkter", html)
        self.assertLess(html.index('id="punkt-1"'), html.index('id="punkt-2"'))

    def test_punkten_med_forslag_handling_sammanfattning_och_beslut(self):
        kort = self.punkt(1)
        self.assertIn("Dnr FSN-2024-00012", kort)
        self.assertIn("<h3>Ny skola i Exempelby</h3>", kort)
        self.assertIn("<blockquote>Nämnden godkänner lokalbehovet.</blockquote>", kort)
        self.assertIn("Skolan behöver fler platser.", kort)
        self.assertIn('2024-05-02/handlingar.html#sida-2">sidan 2 i handlingarna', kort)
        self.assertIn("§ 4</a>: Nämnden godkänner lokalbehovet.", kort)

    def test_historiken_har_andra_sammantraden_men_inte_det_egna(self):
        kort = self.punkt(1)
        self.assertIn("Historik: 1 paragraf, 0 kort", kort)
        self.assertIn("<b>2024-03-01</b>", kort)
        self.assertIn("§ 9</a> Lokalbehovet anmäls", kort)

    def test_det_som_inte_hittades_sags(self):
        kort = self.punkt(2)
        self.assertIn("Inget förslag till beslut i kallelsen.", kort)
        self.assertIn("ingen egen handling hittad för punkten", kort)
        self.assertIn("inga andra paragrafer med diarienumret i poolen", kort)
        self.assertIn("§ 5</a>: Nämnden noterar informationen.", kort)

    def test_en_punkt_i_loptext_far_rubriken_ur_protokollet(self):
        kort = self.punkt(3)
        self.assertIn("<h3>Budget för 2025</h3>", kort)
        self.assertIn("Förslaget gick inte att läsa ur kallelsen.", kort)

    def test_organets_sida_lankar_till_sammantradet(self):
        self.bygg()
        organsida = (self.ut / "exempelby" / "fsn.html").read_text(encoding="utf-8")
        self.assertIn('2024-05-02 – <a href="fsn/2024/2024-05-02.html">', organsida)
        self.assertNotIn("2024-03-01 – <a", organsida)

    def test_utan_kallelse_ingen_sida(self):
        self.spara("protokoll.md", dokument(text=PROTOKOLL))
        bygg(self.rot, self.ut, REPO, TID)
        self.assertFalse(
            (self.ut / "exempelby" / "fsn" / "2024" / "2024-05-02.html").exists()
        )

    def test_fore_det_forsta_aret_ingen_sida(self):
        toml = self.rot / "kommuner" / "exempelby.toml"
        text = toml.read_text(encoding="utf-8")
        toml.write_text(
            text.replace("sammantradessidor = 2024", "sammantradessidor = 2025"),
            encoding="utf-8",
        )
        with self.assertRaises(FileNotFoundError):
            self.bygg()


class TestDagordningen(unittest.TestCase):
    def test_utan_punkter_sags_det(self):
        html = dagordningen([], Lankar("", "", {}))
        self.assertIn("Dagordningen gick inte att läsa ur kallelsen.", html)

    def test_en_handling_utan_sammanfattning_sags(self):
        self.assertIn(
            "Ingen sammanfattning av ärendet", sammanfattning((), range(2, 3))
        )
        self.assertEqual(sammanfattning((), None), "")

    def test_en_punkt_utan_diarienummer_sags(self):
        punkt = Punkt(1, "Val av justerare", "", ())
        kort = punktkort(Arende(punkt, "", None, (), None, [], []), Lankar("", "", {}))
        self.assertNotIn("Dnr", kort)
        self.assertIn("inget diarienummer i kallelsen", kort)
        self.assertNotIn("Beslut", kort)
