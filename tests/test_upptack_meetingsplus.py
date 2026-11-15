"""Krav: K13 och K57 i docs/02-KRAV.md, ADR-0080.
Kod: src/kommunhandlingar/upptack.py."""

import unittest

from kommunhandlingar.konfiguration import tolka
from kommunhandlingar.upptack import upptack
from tests.test_konfiguration import exempelby
from tests.test_upptack import BUN, FSN, Klient


def motessida(mote: str, fil: str) -> str:
    return f'<a href="{mote}/protocol/{fil}?downloadMode=open">Öppna protokoll</a>'


class TestMeetingsPlus(unittest.TestCase):
    def test_kallan_tas_nyast_forst_over_alla_organ(self):
        data = {
            "namn": "Exempelby kommun",
            "organ": [{"id": "bun", "namn": ["Bun"]}, {"id": "fsn", "namn": ["Fsn"]}],
            "kalla": [
                {
                    "adapter": "meetingsplus",
                    "sidor": {"bun": "https://m.se/c/bun", "fsn": "https://m.se/c/fsn"},
                }
            ],
        }
        kommun = tolka("exempelby", data)
        sidor = {
            "https://m.se/c/bun": '<a href="/c/bun/mote-2023-01-01">1</a>'
            '<a href="/c/bun/mote-2025-01-01">2</a>',
            "https://m.se/c/fsn": '<a href="/c/fsn/mote-2024-01-01">3</a>',
        }
        for adress in (
            "bun/mote-2023-01-01",
            "bun/mote-2025-01-01",
            "fsn/mote-2024-01-01",
        ):
            mote = f"https://m.se/c/{adress}"
            sidor[mote] = motessida(mote, "protokollpdf")
        kandidater, _ = upptack(kommun, Klient(sidor))
        self.assertEqual(
            [(k.organ, k.datum.year) for k in kandidater],
            [("bun", 2025), ("fsn", 2024), ("bun", 2023)],
        )

    def test_kallan_star_efter_ovriga_levande_kandidater(self):
        data = exempelby()
        data["kalla"].append(
            {"adapter": "meetingsplus", "sidor": {"bun": "https://m.se/c/bun"}}
        )
        mote = "https://m.se/c/bun/mote-2030-01-01"
        sidor = {
            "https://exempelby.se/bun": BUN,
            "https://exempelby.se/fsn": FSN,
            "https://m.se/c/bun": f'<a href="{mote}">1</a>',
            mote: motessida(mote, "protokollpdf"),
        }
        kandidater, _ = upptack(tolka("exempelby", data), Klient(sidor))
        self.assertEqual(
            [k.kallnyckel.split(":")[0] for k in kandidater],
            ["sitevision"] * 3 + ["meetingsplus"],
        )
