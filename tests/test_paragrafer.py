"""Krav: K48, ADR-0071. Kod: src/kommunhandlingar/paragrafer.py och
src/kommunhandlingar/diarienummer.py.

Protokollen här är påhittade, men byggda efter mallarna i poolen.
"""

import unittest

from kommunhandlingar.diarienummer import i_huvudet
from kommunhandlingar.paragrafer import paragrafer

MED_INNEHALL = """<!-- sida 1 -->

Närvarande
En tjänsteperson, utredare
§ 2

Innehåll

§ 1 Dnr XN-2026-00004
Val av justerare ............................ 2

§ 2 Dnr XN-2026-00067
Lokalbehov 2028-2032 ........................ 3

<!-- sida 2 -->

2026-10-22

§ 1                      Dnr XN-2026-00004
Val av justerare

Beslut

Nämnden väljer en ledamot till justerare.

Beslutsgång
Ordföranden finner att nämnden bifaller det.

<!-- sida 3 -->

§ 2                      Dnr XN-2026-00067
Lokalbehov 2028-2032

Beslut

Nämnden godkänner lokalbehovet.

Sammanfattning
Enligt beslutet i § 12 ska nämnden varje år redovisa behovet, och
§ 85/2016 om lokaler gäller fortfarande.
"""


class TestDelningen(unittest.TestCase):
    def test_innehallet_och_narvarolistan_blir_inga_paragrafer(self):
        funna = paragrafer(MED_INNEHALL)
        self.assertEqual([(p.nummer, p.sida) for p in funna], [(1, 2), (2, 3)])

    def test_rubrik_diarienummer_och_beslut(self):
        forsta = paragrafer(MED_INNEHALL)[0]
        self.assertEqual(forsta.rubrik, "Val av justerare")
        self.assertEqual(forsta.diarienummer, ["XN-2026-00004"])
        self.assertEqual(forsta.beslut, "Nämnden väljer en ledamot till justerare.")

    def test_organets_forkortning_och_inget_mellanslag(self):
        text = "BN § 1\n\nÄndringar\nBeslut\nInga.\n\n§2\nDnr KT/2016:5\nBeslut\nJa.\n"
        funna = paragrafer(text)
        self.assertEqual([p.nummer for p in funna], [1, 2])
        self.assertEqual(funna[1].diarienummer, ["KT/2016:5"])
        self.assertIsNone(funna[1].sida)

    def test_diarienumret_pa_raden_efter_rubriken(self):
        text = (
            "§ 2\n\nInvesteringsplan\nDnr SE/2016:5\n\nBeslut\n\nNämnden godkänner.\n"
        )
        (paragraf,) = paragrafer(text)
        self.assertEqual(paragraf.rubrik, "Investeringsplan")
        self.assertEqual(paragraf.diarienummer, ["SE/2016:5"])

    def test_ett_diarienummer_utan_dnr_pa_rubrikraden(self):
        (paragraf,) = paragrafer("§ 142                  GV/2014:4\nBidrag\n")
        self.assertEqual(paragraf.diarienummer, ["GV/2014:4"])

    def test_en_fortsattning_hor_till_paragrafen(self):
        text = "§ 270\nDispens\nBeslut\nJa.\n\nMotivering\n"
        text += "<!-- sida 2 -->\n\n§ 270, forts\n"
        (paragraf,) = paragrafer(text)
        self.assertEqual((paragraf.nummer, paragraf.sida), (270, None))
        self.assertEqual(paragraf.beslut, "Ja.")

    def test_hanvisningar_inleder_inga_paragrafer(self):
        text = "§ 5\nTillsyn\n\nBeslutet 2022-01-27\n§18\n\n§§ 6-9 gäller\n"
        self.assertEqual([p.nummer for p in paragrafer(text)], [5])

    def test_en_ensam_paragraf_efter_datumet_i_sidhuvudet(self):
        text = "Datum\n2014-06-09\n§ 7\nBudget\n"
        self.assertEqual([p.nummer for p in paragrafer(text)], [7])

    def test_ett_protokoll_utan_paragrafer(self):
        self.assertEqual(paragrafer("<!-- sida 1 -->\n\nAnteckningar\n"), [])


class TestBeslutet(unittest.TestCase):
    def test_utan_rubriken_beslut(self):
        (paragraf,) = paragrafer("§ 3\nInformation\n\nNämnden informeras.\n")
        self.assertIsNone(paragraf.beslut)

    def test_beslutet_slutar_vid_nasta_rubrik(self):
        text = "§ 3\nBygglov\nBeslut\nBeviljas.\n\nBeslutsmotivering\nDärför.\n"
        self.assertEqual(paragrafer(text)[0].beslut, "Beviljas.")

    def test_ett_beslut_som_nar_sidans_slut_blir_null(self):
        text = "§ 3\nBygglov\nBeslut\nBeviljas med\n\nJusterare   Expedierat\n"
        self.assertIsNone(paragrafer(text)[0].beslut)

    def test_ingen_rubrik_nar_paragrafen_borjar_med_ett_avsnitt(self):
        self.assertIsNone(paragrafer("§ 3\n\nBeslut\nJa.\n")[0].rubrik)


class TestDiarienummer(unittest.TestCase):
    def test_som_det_star(self):
        for text, vantat in (
            ("Dnr XN-2026-00004", ["XN-2026-00004"]),
            ("Dnr 2020-00327", ["2020-00327"]),
            ("Dnr KS/2016:375", ["KS/2016:375"]),
            ("Dnr 2015-P014", ["2015-P014"]),
            ("Dnr. IF-2024-00123. Personuppgifter", ["IF-2024-00123"]),
        ):
            with self.subTest(text):
                self.assertEqual(i_huvudet(text), vantat)

    def test_mellanslag_och_tankstreck_blir_bindestreck(self):
        self.assertEqual(i_huvudet("Dnr BN 2024-000123"), ["BN-2024-000123"])
        self.assertEqual(i_huvudet("Dnr MH-2021- 3122"), ["MH-2021-3122"])
        self.assertEqual(i_huvudet("Dnr BN 2016–000170"), ["BN-2016-000170"])

    def test_inget_nummer_utan_dnr(self):
        self.assertEqual(i_huvudet("Kyrkobyn 1:8 - Strandskyddsdispens, 2014-0849"), [])
