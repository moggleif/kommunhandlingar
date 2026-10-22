"""Krav: K26 och K27 i docs/02-KRAV.md, ADR-0044 och ADR-0045. Kod:
src/kommunhandlingar/webbplats/mal.py, malsida.py, malkort.py,
statusikon.py och bygg.py. Grupperna och antalet: tests/test_malgrupper.py.
Tidslinjen och korten: tests/test_malkort.py."""

import shutil
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import las as las_kommun
from kommunhandlingar.webbplats import mal
from kommunhandlingar.webbplats.bygg import bygg
from kommunhandlingar.webbplats.malkort import kallank
from kommunhandlingar.webbplats.mall import Mall
from kommunhandlingar.webbplats.malsida import malsida
from tests.test_webbplats import FIXTURER, REPO, TID, dokument, exempelby, protokoll

ROT = Path(__file__).parent.parent
RUBRIK = (
    "organ,ar,slag,rubrik,formulering,status,uppfoljning,bedomning,"
    "kalla,grupp,tolkad,huvudmal\n"
)
BUDGET = "fsn/2024/2024-05-02/protokoll.md"
HANDLINGAR = "fsn/2024/2024-05-02/handlingar.md"
TEXT = """<!-- sida 1 -->

5.1 Trygga
miljöer
Beslutats av
Nämnd
Nämndens formulering
\\- Alla ska
känna sig trygga.

<!-- sida 2 -->

Status direktiv Läsfrämjande        Delvis uppnått

<!-- sida 3 -->

läsfrämjande
"""
RADER = (
    "fsn,2025,nämndmål,Trygga miljöer,Alla ska känna sig trygga.,,,,"
    f"{BUDGET}#sida-1,,,\n"
    "fsn,2024,direktiv,Läsfrämjande,,Delvis uppnått,prognos,delvis,"
    f"{BUDGET}#sida-2,,,\n"
    f"fsn,2025,direktiv,läsfrämjande,,,,,{BUDGET}#sida-3,,,\n"
)


def budget() -> str:
    return dokument(text=TEXT, per_sida="[ok, ok, ok]")


@contextmanager
def pool(rader: str = RADER, rubrik: str = RUBRIK):
    """Läser en målfil mot en pool med ett dokument, i en temporär katalog."""
    with tempfile.TemporaryDirectory() as tmp:
        fil, data = Path(tmp) / "exempelby.csv", Path(tmp) / "data"
        fil.write_text(rubrik + rader, encoding="utf-8")
        (data / BUDGET).parent.mkdir(parents=True)
        (data / BUDGET).write_text(budget(), encoding="utf-8")
        (data / HANDLINGAR).write_text(budget(), encoding="utf-8")
        yield mal.las(fil, exempelby(), data)


class TestLasning(unittest.TestCase):
    def test_raderna_lases(self):
        with pool() as malen:
            self.assertEqual(len(malen), 3)
            self.assertEqual(malen[0].ar, 2025)
            self.assertEqual(malen[1].status, "Delvis uppnått")

    def test_samma_mal_utan_hansyn_till_versaler(self):
        with pool() as malen:
            self.assertEqual(malen[1].spar, malen[2].spar)

    def stoppas(self, rader: str, rubrik: str = RUBRIK) -> str:
        with self.assertRaises(Datafel) as fel, pool(rader, rubrik):
            pass
        return str(fel.exception)

    def test_fel_rubriker(self):
        self.assertIn("rubrikerna", self.stoppas(RADER, "organ,ar\n"))

    def test_fel_antal_falt(self):
        self.assertIn("rad 2", self.stoppas("fsn,2025,nämndmål\n"))

    def test_okant_organ(self):
        fel = self.stoppas(f"kun,2025,nämndmål,Trygga miljöer,,,,,{BUDGET}#sida-1,,,\n")
        self.assertIn("'kun'", fel)

    def test_ar_som_inte_ar_fyra_siffror(self):
        fel = self.stoppas(f"fsn,25,nämndmål,Trygga miljöer,,,,,{BUDGET}#sida-1,,,\n")
        self.assertIn("'25'", fel)

    def test_okant_slag(self):
        fel = self.stoppas(f"fsn,2025,mål,Trygga miljöer,,,,,{BUDGET}#sida-1,,,\n")
        self.assertIn("'mål'", fel)

    def test_kalla_utan_sida(self):
        fel = self.stoppas(f"fsn,2025,nämndmål,Trygga miljöer,,,,,{BUDGET},,,\n")
        self.assertIn("ingen sida", fel)

    def test_kalla_i_ett_annat_organs_dokument(self):
        kalla = BUDGET.replace("fsn/", "bun/")
        fel = self.stoppas(f"fsn,2025,nämndmål,Trygga miljöer,,,,,{kalla}#sida-1,,,\n")
        self.assertIn("ingen sida", fel)

    def test_dokument_som_inte_finns(self):
        kalla = BUDGET.replace("protokoll", "kallelse")
        fel = self.stoppas(f"fsn,2025,nämndmål,Trygga miljöer,,,,,{kalla}#sida-1,,,\n")
        self.assertIn("inget dokument", fel)

    def test_sida_som_inte_finns(self):
        fel = self.stoppas(f"fsn,2025,nämndmål,Trygga miljöer,,,,,{BUDGET}#sida-4,,,\n")
        self.assertIn("ingen sida i dokumentet", fel)

    def test_rubrik_som_inte_star_pa_sidan(self):
        fel = self.stoppas(f"fsn,2025,nämndmål,Trygga miljöer,,,,,{BUDGET}#sida-2,,,\n")
        self.assertIn("rubriken", fel)

    def test_versalerna_raknas(self):
        fel = self.stoppas(f"fsn,2025,nämndmål,trygga miljöer,,,,,{BUDGET}#sida-1,,,\n")
        self.assertIn("rubriken", fel)

    def test_ett_mal_over_tva_sidor(self):
        rad = (
            "fsn,2026,nämndmål,Trygga miljöer,,Delvis uppnått,prognos,delvis,"
            f"{BUDGET}#sida-1-2,,,\n"
        )
        with pool(rad) as malen:
            self.assertEqual(malen[0].status, "Delvis uppnått")
        self.assertIn("ingen sida", self.stoppas(rad.replace("1-2", "2-4")))

    def test_formulering_som_inte_star_pa_sidan(self):
        rad = (
            f"fsn,2025,nämndmål,Trygga miljöer,Alla ska må bra.,,,,{BUDGET}#sida-1,,,\n"
        )
        self.assertIn("formuleringen", self.stoppas(rad))

    def test_status_som_inte_star_pa_sidan(self):
        rad = "fsn,2024,direktiv,Läsfrämjande,,Uppnått,utfall,uppnatt,"
        rad += f"{BUDGET}#sida-2,,,\n"
        self.assertIn("statusen", self.stoppas(rad))

    def test_samma_mal_tva_ganger_ur_samma_kalla(self):
        rad = f"fsn,2026,direktiv,Läsfrämjande,,,,,{BUDGET}#sida-2,,,\n"
        self.assertIn("rad 5", self.stoppas(RADER + rad))


class TestSidan(unittest.TestCase):
    def sida(self, dokumentar: set[int] = frozenset({2023, 2025})) -> str:
        with pool() as malen:
            mall = Mall([exempelby()], REPO, TID)
            return malsida(mall, exempelby(), malen, protokoll(*dokumentar))

    def test_ett_spar_per_rad_och_ett_ar_per_kolumn_med_mal(self):
        html = self.sida()
        self.assertEqual(html.count("<tr data-mal"), 2)
        self.assertEqual(html.count("<article"), 2)
        for ar in ("2024", "2025"):
            self.assertIn(f'<th scope="col">{ar}</th>', html)
        self.assertNotIn('<th scope="col">2023', html)

    def test_status_som_ikon_i_tidslinjen_och_historiken(self):
        html = self.sida()
        ikon = 'class="status delvis prognos" role="img" title="delvis uppnått'
        self.assertIn(f'<td class="band start"><span {ikon}', html)
        self.assertIn(f"Status: <span {ikon}", html)
        self.assertIn("</span> Delvis uppnått (prognos)", html)
        self.assertIn('<ul class="teckenforklaring">', html)

    def test_budgeten_har_ingen_status(self):
        html = self.sida()
        kort = html.split('<article id="mal-1"')[1].split("</article>")[0]
        self.assertIn("<h3>Trygga miljöer</h3>", kort)
        self.assertNotIn("Status:", kort)

    def test_kallan_lankar_till_sidan_i_dokumentet(self):
        self.assertIn(
            'href="2024/2024-05-02/protokoll.html#sida-1">protokoll 2024-05-02, sida 1',
            self.sida(),
        )
        self.assertIn(
            'protokoll.html#sida-1">protokoll 2024-05-02, sida 1–2',
            kallank(f"{BUDGET}#sida-1-2"),
        )

    def test_sidan_har_skriptet_och_stilen(self):
        html = self.sida()
        self.assertIn("<script>", html)
        self.assertIn("table.tidslinje", html)


class TestBygg(unittest.TestCase):
    def bygg(self, rader: str | None, namn: str = "exempelby") -> Path:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        rot, ut = tmp / "repo", tmp / "ut"
        (rot / "kommuner").mkdir(parents=True)
        shutil.copy(FIXTURER / "exempelby.toml", rot / "kommuner")
        fil = rot / "data" / "exempelby" / BUDGET
        fil.parent.mkdir(parents=True)
        fil.write_text(budget(), encoding="utf-8")
        if rader is not None:
            (rot / "mal").mkdir()
            (rot / "mal" / f"{namn}.csv").write_text(RUBRIK + rader, encoding="utf-8")
        bygg(rot, ut, REPO, TID)
        return ut / "exempelby"

    def test_sidan_byggs_och_lankas_fran_organets_sida(self):
        ut = self.bygg(RADER)
        sidan = (ut / "fsn" / "mal-och-direktiv.html").read_text()
        self.assertIn("Trygga miljöer", sidan)
        self.assertIn('href="fsn/mal-och-direktiv.html"', (ut / "fsn.html").read_text())
        self.assertNotIn("mal-och-direktiv", (ut / "bun.html").read_text())

    def test_malfil_utan_kommunfil_stoppar_bygget(self):
        with self.assertRaises(Datafel):
            self.bygg(RADER, namn="exempelbyn")

    def test_utan_malfil_ingen_sida(self):
        ut = self.bygg(None)
        self.assertFalse((ut / "fsn" / "mal-och-direktiv.html").exists())
        self.assertNotIn("mal-och-direktiv", (ut / "fsn.html").read_text())


class TestKungsbacka(unittest.TestCase):
    def test_filen_gar_ihop_med_kommunfilen_och_poolen(self):
        kungsbacka = las_kommun(ROT / "kommuner" / "kungsbacka.toml")
        fil = ROT / "mal" / "kungsbacka.csv"
        malen = mal.las(fil, kungsbacka, ROT / "data" / "kungsbacka")
        self.assertEqual({m.organ for m in malen}, {"ga", "kf"})
        self.assertEqual(fil.read_bytes().count(b"\r"), 0)
