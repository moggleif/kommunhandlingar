"""Krav: K57 i docs/02-KRAV.md, ADR-0080.
Kod: src/kommunhandlingar/adaptrar/meetingsplus_html.py, moten(), och
meetingsplus.py, egna_moten().

Organsidan under tests/fixtures/meetingsplus/ är Region Hallands, sparad
2026-11-15."""

import unittest
from pathlib import Path

from kommunhandlingar.adaptrar import meetingsplus_html
from kommunhandlingar.adaptrar.meetingsplus import kalla_av, upptack

SIDOR = Path(__file__).parent / "fixtures" / "meetingsplus"
BAS = "https://politik.regionhalland.se/committees"
SJUKHUS = f"{BAS}/driftnamnden-hallands-sjukhus"
HEMSJUKVARD = f"{BAS}/gemensam-namnd-for-hemsjukvard-och-hjalpmedel"


class TestOrgansidan(unittest.TestCase):
    def test_alla_moten_i_sidans_ordning(self):
        sida = (SIDOR / "organsida.html").read_text(encoding="utf-8")
        moten = meetingsplus_html.moten(sida, SJUKHUS)
        self.assertEqual(len(moten), 73)
        self.assertEqual(moten[0], f"{SJUKHUS}/mote-2026-12-02")
        self.assertEqual(moten[-1], f"{SJUKHUS}/mote-2017-06-28")

    def test_bara_moten_direkt_under_en_organsida_bredvid(self):
        sida = (
            f'<a href="{SJUKHUS}/mote-2026-01-01">a</a>'
            f'<a href="{SJUKHUS}/mote-2026-01-01/agenda/x-2026-01-01pdf">b</a>'
            f'<a href="{SJUKHUS}/mote-2026-01-03?x=1">c</a>'
            '<a href="/committees/driftnamnden-hallands-sjukhus/mote-2026-01-04">d</a>'
            f'<a href="{BAS}/mote-2026-01-05">e</a>'
            '<a href="https://annan.se/committees/x/mote-2026-01-06">f</a>'
            f'<a href="{SJUKHUS}/arkiv">g</a>'
        )
        self.assertEqual(
            meetingsplus_html.moten(sida, SJUKHUS),
            [f"{SJUKHUS}/mote-2026-01-01", f"{SJUKHUS}/mote-2026-01-04"],
        )

    def test_moten_under_organets_tidigare_sida(self):
        moten = [
            f"{HEMSJUKVARD}-23088/mote-2026-12-02",
            f"{HEMSJUKVARD}-23088/mote-2022-02-11",
            f"{HEMSJUKVARD}/mote-2021-12-10",
        ]
        sida = "".join(f'<a href="{m}">Möte</a>' for m in moten)
        self.assertEqual(meetingsplus_html.moten(sida, HEMSJUKVARD), moten)


class TestUpptack(unittest.TestCase):
    def test_ett_annat_organs_moten_ar_det_organets(self):
        post = {
            "adapter": "meetingsplus",
            "sidor": {"hs": SJUKHUS, "gnhh": HEMSJUKVARD},
        }
        kalla = kalla_av(post, ["hs", "gnhh"], "kalla 1")
        egna = [f"{SJUKHUS}/mote-2026-01-01", f"{SJUKHUS}-1/mote-2016-01-01"]
        andras = f"{HEMSJUKVARD}/mote-2026-01-02"
        sidor = {
            SJUKHUS: "".join(f'<a href="{m}">Möte</a>' for m in [*egna, andras]),
            HEMSJUKVARD: "",
        }
        hamtade = []

        def hamta(adress: str) -> str:
            hamtade.append(adress)
            return sidor.get(adress, "")

        upptack(kalla, hamta)
        self.assertEqual(hamtade, [SJUKHUS, *egna, HEMSJUKVARD])
