"""Krav: K54 i docs/02-KRAV.md, ADR-0078.
Kod: src/kommunhandlingar/webbplats/dagordning.py."""

import unittest

from kommunhandlingar.webbplats.dagordning import Punkt, dagordning

RAD = "| {} | {} | {} | {} |"
FORSLAG_1 = [
    "Förslag till beslut i kommunfullmäktige",
    "Kommunfullmäktige godkänner",
    "delårsrapporten.",
    "Förslag till beslut i kommunstyrelsen",
    "Kommunstyrelsen uppmanar",
    "nämnderna.",
]
RUBRIK_1 = "Delårsrapport för<br>Exempelby kommun<br>13.00–13.45<br>En Föredragande"
FORSLAG_3 = "Förslag till beslut i kommunfullmäktige<br>Taxan gäller från 1 januari"
KALLELSE = "\n".join(
    [
        RAD.format("", "Ärende", "Beteckning", "Förslag"),
        "| --- | --- | --- | --- |",
        RAD.format("", "Beslutsärenden", "", ""),
        RAD.format("1.", RUBRIK_1, "2026-00543", "<br>".join(FORSLAG_1)),
        RAD.format(
            "2.", "Svar på Kärnkrafts-<br>utredningens remiss", "2026-00534", ""
        ),
        RAD.format(
            "3.", "Taxa för VA-<br>verksamhet 2027 \\*", "2026-00124", FORSLAG_3
        ),
        "",
        "35\\. Fastställande av skattesats och 2025-00785 Förslag till beslut",
    ]
)


class TestDagordning(unittest.TestCase):
    def setUp(self):
        self.punkter = dagordning(KALLELSE)

    def test_punkterna_i_ordning_med_beteckningen(self):
        self.assertEqual([p.nummer for p in self.punkter], [1, 2, 3, 35])
        self.assertEqual(self.punkter[0].diarienummer, "2026-00543")

    def test_rubriken_slutar_fore_foredragningens_tid(self):
        self.assertEqual(self.punkter[0].rubrik, "Delårsrapport för Exempelby kommun")

    def test_ett_avstavat_ord_fogas_ihop_och_escapningen_tas_bort(self):
        self.assertEqual(
            self.punkter[1].rubrik, "Svar på Kärnkrafts-utredningens remiss"
        )
        self.assertEqual(self.punkter[2].rubrik, "Taxa för VA-verksamhet 2027 *")

    def test_forslaget_i_stycken_med_rubrikerna_for_sig(self):
        self.assertEqual(
            self.punkter[0].forslag,
            (
                "Förslag till beslut i kommunfullmäktige",
                "Kommunfullmäktige godkänner delårsrapporten.",
                "Förslag till beslut i kommunstyrelsen",
                "Kommunstyrelsen uppmanar nämnderna.",
            ),
        )
        self.assertEqual(self.punkter[2].forslag[-1], "Taxan gäller från 1 januari")

    def test_en_punkt_utan_forslag_har_inga_stycken(self):
        self.assertEqual(self.punkter[1].forslag, ())

    def test_en_punkt_i_loptext_har_varken_rubrik_eller_forslag(self):
        self.assertEqual(self.punkter[3], Punkt(35, "", "2025-00785", None))


NAMND = "\n".join(
    [
        RAD.format("1.", "Val av justerare", "", ""),
        RAD.format(
            "2.",
            "Årsrapport<br>Föredragande: En<br>Tjänsteperson<br>17.30-17.45",
            "GA-2026-<br>00059",
            "",
        ),
        RAD.format(
            "3.",
            "Uppföljning april",
            "TE-2026-<br>00368,<br>Föredragande:<br>En Person,<br>17:35 – 18:00",
            "",
        ),
        RAD.format("4.", "Förhandsbesked", "BN-2026<br>001234", ""),
        RAD.format("5.", "Anmälan", "BN-2026–<br>000170", ""),
        RAD.format("6.", "Ärendelista<br>Kl. 17:05-17:45", "VN-2026-00012", ""),
        RAD.format("7.", "Information Föredragare: En<br>Person", "", ""),
    ]
)


class TestNamndernasKallelser(unittest.TestCase):
    def setUp(self):
        self.punkter = dagordning(NAMND)

    def test_diarienumret_ur_en_delad_cell(self):
        self.assertEqual(
            [p.diarienummer for p in self.punkter],
            [
                "",
                "GA-2026-00059",
                "TE-2026-00368",
                "BN-2026-001234",
                "BN-2026-000170",
                "VN-2026-00012",
                "",
            ],
        )

    def test_rubriken_slutar_fore_foredragandena_och_klockslaget(self):
        self.assertEqual(self.punkter[1].rubrik, "Årsrapport")
        self.assertEqual(self.punkter[5].rubrik, "Ärendelista")
        self.assertEqual(self.punkter[6].rubrik, "Information")
