"""Krav: K10 i docs/02-KRAV.md, ADR-0013. Kod: src/kommunhandlingar/hamtning/."""

import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from kommunhandlingar.fel import Hamtfel, Konfigurationsfel
from kommunhandlingar.hamtning.installningar import Installningar, las
from kommunhandlingar.hamtning.klient import Klient

ROT = Path(__file__).parent.parent
UA = "kommunhandlingar (+https://exempelby.se)"


class Server(BaseHTTPRequestHandler):
    """Svarar med nästa svar i `svar[sokvag]`; `None` stänger utan svar."""

    svar: dict[str, list] = {}
    anrop: list[tuple[str, str]] = []

    def do_GET(self):
        Server.anrop.append((self.path, self.headers["User-Agent"]))
        kod, rubriker, kropp = Server.svar[self.path].pop(0)
        if kod is None:
            self.close_connection = True
            return
        self.send_response(kod)
        for namn, varde in rubriker.items():
            self.send_header(namn, varde)
        self.end_headers()
        self.wfile.write(kropp.encode())

    def log_message(self, *_):
        pass


class TestKlient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Server)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.bas = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        Server.anrop = []
        Server.svar = {"/robots.txt": [(404, {}, "")]}
        self.tid = 100.0
        self.vantat: list[float] = []
        self.klient = Klient(Installningar(UA, 5), lambda: self.tid, self.sov)

    def sov(self, sekunder: float):
        self.vantat.append(sekunder)
        self.tid += sekunder

    def test_hamtar_text_med_var_user_agent(self):
        Server.svar["/sida"] = [(200, {"Content-Type": "text/html"}, "<h3>Möte</h3>")]
        self.assertEqual(self.klient.text(self.bas + "/sida"), "<h3>Möte</h3>")
        self.assertEqual(Server.anrop[-1], ("/sida", UA))

    def test_intervallet_mellan_anrop_till_samma_vard(self):
        Server.svar["/a"] = [(200, {}, "a")]
        Server.svar["/b"] = [(200, {}, "b")]
        self.klient.text(self.bas + "/a")
        self.klient.text(self.bas + "/b")
        self.assertEqual(self.vantat, [5, 5])

    def test_robots_stanger(self):
        Server.svar["/robots.txt"] = [(200, {}, "User-agent: *\nDisallow: /*91.*")]
        with self.assertRaisesRegex(Hamtfel, "^robots$"):
            self.klient.text(self.bas + "/protokoll-76-91.pdf")
        self.assertEqual([a for a, _ in Server.anrop], ["/robots.txt"])

    def test_robots_hamtas_en_gang_per_vard(self):
        Server.svar["/a"] = [(200, {}, "a"), (200, {}, "a")]
        self.klient.text(self.bas + "/a")
        self.klient.text(self.bas + "/a")
        self.assertEqual([a for a, _ in Server.anrop], ["/robots.txt", "/a", "/a"])

    def test_robots_som_inte_gar_att_hamta_stoppar(self):
        Server.svar["/robots.txt"] = [(503, {}, "")] * 4
        with self.assertRaisesRegex(Hamtfel, "^http-503$"):
            self.klient.text(self.bas + "/a")

    def test_nytt_forsok_efter_tomt_svar_och_5xx(self):
        Server.svar["/a"] = [(None, {}, ""), (503, {}, ""), (200, {}, "ok")]
        self.assertEqual(self.klient.text(self.bas + "/a"), "ok")
        self.assertEqual(self.vantat, [5, 5, 10])

    def test_retry_after_foljs(self):
        Server.svar["/a"] = [(429, {"Retry-After": "30"}, ""), (200, {}, "ok")]
        self.assertEqual(self.klient.text(self.bas + "/a"), "ok")
        self.assertIn(30, self.vantat)

    def test_ger_upp_efter_fyra_forsok(self):
        Server.svar["/a"] = [(None, {}, "")] * 4
        with self.assertRaisesRegex(Hamtfel, "^tomt-svar$"):
            self.klient.text(self.bas + "/a")
        self.assertEqual(len(Server.anrop), 5)

    def test_404_forsoks_inte_igen(self):
        Server.svar["/a"] = [(404, {}, "")]
        with self.assertRaisesRegex(Hamtfel, "^http-404$"):
            self.klient.text(self.bas + "/a")
        self.assertEqual(len(Server.anrop), 2)


class TestInstallningar(unittest.TestCase):
    def test_hamtning_toml_lases(self):
        installningar = las(ROT / "hamtning.toml")
        self.assertIn("github.com/moggleif/kommunhandlingar", installningar.user_agent)
        self.assertEqual(installningar.intervall, 5)

    def test_okant_falt_stoppar(self):
        katalog = tempfile.TemporaryDirectory()
        self.addCleanup(katalog.cleanup)
        fil = Path(katalog.name) / "hamtning.toml"
        fil.write_text('user_agent = "x"\nintervall = 5\ntakt = 1\n')
        with self.assertRaises(Konfigurationsfel):
            las(fil)
