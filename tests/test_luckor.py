"""Krav: K7 i docs/02-KRAV.md, ADR-0020. Kod: src/kommunhandlingar/webbplats/."""

import unittest
from datetime import date

from kommunhandlingar.webbplats.luckor import Lucka, luckor

IDAG = date(2026, 10, 9)


def dok(datum: str, typ: str, lopnr: str = "null", kvalitet: str = "full") -> dict:
    return {"datum": datum, "typ": typ, "lopnr": lopnr, "kvalitet": kvalitet}


def mote(datum: str, *typer: str, lopnr: str = "null") -> list[dict]:
    return [dok(datum, typ, lopnr) for typ in typer]


class TestLuckor(unittest.TestCase):
    def test_typ_som_organet_har_vid_annat_mote_saknas(self):
        dokument = mote("2026-01-10", "kallelse", "protokoll") + mote(
            "2026-02-10", "protokoll"
        )
        self.assertEqual(
            luckor(dokument, IDAG), [Lucka("2026-02-10", "null", ("kallelse",))]
        )

    def test_typ_som_organet_aldrig_har_vantas_inte(self):
        dokument = mote("2026-01-10", "protokoll") + mote("2026-02-10", "protokoll")
        self.assertEqual(luckor(dokument, IDAG), [])

    def test_bilagor_vantas_inte(self):
        dokument = mote("2026-01-10", "protokoll", "bilaga") + mote(
            "2026-02-10", "protokoll"
        )
        self.assertEqual(luckor(dokument, IDAG), [])

    def test_typerna_i_dokumentordning(self):
        dokument = mote("2026-01-10", "protokoll", "handlingar", "kallelse") + mote(
            "2026-02-10", "bilaga"
        )
        self.assertEqual(
            luckor(dokument, IDAG)[0].saknas, ("kallelse", "handlingar", "protokoll")
        )

    def test_protokoll_saknas_forst_efter_21_dagar(self):
        dokument = (
            mote("2026-01-10", "kallelse", "protokoll")
            + mote("2026-09-18", "kallelse")
            + mote("2026-09-19", "kallelse")
        )
        self.assertEqual(
            luckor(dokument, IDAG), [Lucka("2026-09-18", "null", ("protokoll",))]
        )

    def test_mote_som_inte_passerat_ar_ingen_lucka(self):
        dokument = mote("2026-01-10", "kallelse", "protokoll") + mote(
            "2026-10-09", "protokoll"
        )
        self.assertEqual(luckor(dokument, IDAG), [])

    def test_ej_hamtad_ar_ingen_lucka(self):
        dokument = mote("2026-01-10", "kallelse", "protokoll") + [
            dok("2026-02-10", "kallelse", kvalitet="ej-hamtad"),
            dok("2026-02-10", "protokoll"),
        ]
        self.assertEqual(luckor(dokument, IDAG), [])

    def test_moten_samma_dag_skiljs_pa_lopnummer(self):
        dokument = mote("2026-01-10", "kallelse", "protokoll") + mote(
            "2026-01-10", "protokoll", lopnr="2"
        )
        self.assertEqual(
            luckor(dokument, IDAG), [Lucka("2026-01-10", "2", ("kallelse",))]
        )
