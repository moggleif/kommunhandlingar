"""Krav: K43 i docs/02-KRAV.md, ADR-0066. Kod: src/kommunhandlingar/webbplats/
granskningsslag.py."""

import tempfile
import unittest
from pathlib import Path

from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import las as las_kommun
from kommunhandlingar.webbplats import spar
from kommunhandlingar.webbplats.granskningsslag import GRANSKNINGAR
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.sparkort import Vy
from kommunhandlingar.webbplats.sparsida import sparsida
from tests.test_mal import ROT
from tests.test_webbplats import REPO, TID, dokument, exempelby

RUBRIK = "organ,granskning,ar,fas,varde,text,kalla,tolkad\n"
REVISION = "fsn/2025/2025-10-27/protokoll.md"
NAMND = "bun/2025/2025-12-10/protokoll.md"
TEXTER = {
    REVISION: "<!-- sida 1 -->\n\nGodkännande av granskning av köpta platser\n",
    NAMND: (
        "<!-- sida 1 -->\n\nVi bedömer att nämnden inte har säkerställt en\n"
        "ändamålsenlig uppföljning.\n\n<!-- sida 2 -->\n\n"
        "Yttrande över revisionens granskning av köpta platser\n"
    ),
}
GRANSKNING = "bun,Köpta platser"
RAPPORT = (
    f"{GRANSKNING},2025,rapport,,Godkännande av granskning av köpta platser,"
    f"{REVISION}#sida-1,\n"
)
SVAR = (
    f"{GRANSKNING},2025,svar,,Yttrande över revisionens granskning av köpta "
    f"platser,{NAMND}#sida-2,\n"
)


def bedomning(varde: str) -> str:
    return (
        f"{GRANSKNING},2025,bedomning,{varde},Vi bedömer att nämnden {varde} har "
        f"säkerställt,{NAMND}#sida-1,\n"
    )


def las(rader: str) -> list[spar.Steg]:
    with tempfile.TemporaryDirectory() as tmp:
        fil, data = Path(tmp) / "exempelby.csv", Path(tmp) / "data"
        fil.write_text(RUBRIK + rader, encoding="utf-8")
        for dok, text in TEXTER.items():
            organ, _, datum, _ = dok.split("/")
            (data / dok).parent.mkdir(parents=True, exist_ok=True)
            (data / dok).write_text(
                dokument(organ, datum, text=text, per_sida="[ok]"), encoding="utf-8"
            )
        return spar.las(fil, exempelby(), data, GRANSKNINGAR)


def sida() -> str:
    stegen = las(RAPPORT + bedomning("inte") + SVAR)
    vy = Vy.over(GRANSKNINGAR, exempelby(), stegen)
    return sparsida(Mall([exempelby()], REPO, TID), vy, stegen)


class TestSidan(unittest.TestCase):
    def test_granskningen_foljs_fran_revisionen_till_namndens_svar(self):
        html = sida()
        self.assertIn(">Köpta platser</a></th>", html)
        self.assertIn("<dt>rapporten godkänd av revisionen</dt><dd>1</dd>", html)
        self.assertIn("<dt>nämndens svar eller åtgärder</dt><dd>1</dd>", html)
        self.assertIn("revisionens bedömning (inte)", html)
        self.assertIn(REVISION.removesuffix(".md"), html)


class TestBedomningen(unittest.TestCase):
    def test_en_bedomning_som_inte_ar_revisorernas_ord_stoppar(self):
        with self.assertRaisesRegex(Datafel, "rad 2: värdet 'bra'"):
            las(bedomning("bra"))


class TestKungsbacka(unittest.TestCase):
    def test_filen_gar_ihop_med_kommunfilen_och_poolen(self):
        kungsbacka = las_kommun(ROT / "kommuner" / "kungsbacka.toml")
        fil = ROT / "granskningar" / "kungsbacka.csv"
        stegen = spar.las(fil, kungsbacka, ROT / "data" / "kungsbacka", GRANSKNINGAR)
        self.assertNotIn("revision", {s.organ for s in stegen})
        self.assertEqual(fil.read_bytes().count(b"\r"), 0)
