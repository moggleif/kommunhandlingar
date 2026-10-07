"""Krav: K10 i docs/02-KRAV.md, ADR-0013. Kod: src/kommunhandlingar/hamtning/."""

import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from kommunhandlingar.fel import Hamtfel, Konfigurationsfel
from kommunhandlingar.hamtning import klient
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
        if kod == "sov":
            time.sleep(0.5)
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
        Server.svar["/a"] = [
            (429, {"Retry-After": "30"}, ""),
            (429, {"Retry-After": "86400"}, ""),
            (429, {}, ""),
            (200, {}, "ok"),
        ]
        self.assertEqual(self.klient.text(self.bas + "/a"), "ok")
        self.assertEqual(self.vantat, [5, 30, 300, 20])

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

    def test_kapat_svar_forsoks_igen(self):
        Server.svar["/a"] = [(200, {"Content-Length": "100"}, "abc"), (200, {}, "ok")]
        self.assertEqual(self.klient.text(self.bas + "/a"), "ok")

    def test_tidsgrans_forsoks_igen(self):
        Server.svar["/a"] = [("sov", {}, ""), (200, {}, "ok")]
        with mock.patch.object(klient, "TIDSGRANS", 0.1):
            self.assertEqual(self.klient.text(self.bas + "/a"), "ok")

    def test_ingen_server_ger_anslutning(self):
        with self.assertRaisesRegex(Hamtfel, "^anslutning$"):
            self.klient.text("http://127.0.0.1:1/a")

    def test_okand_teckenkodning(self):
        Server.svar["/a"] = [(200, {"Content-Type": "text/html; charset=foo"}, "x")]
        with self.assertRaisesRegex(Hamtfel, "^teckenkodning$"):
            self.klient.text(self.bas + "/a")

    def test_omdirigering_foljs_inte(self):
        Server.svar["/a"] = [(302, {"Location": "/hemligt"}, "")]
        with self.assertRaisesRegex(Hamtfel, "^http-302$"):
            self.klient.text(self.bas + "/a")
        self.assertNotIn("/hemligt", [a for a, _ in Server.anrop])

    def test_429_pa_robots_stoppar(self):
        Server.svar["/robots.txt"] = [(429, {}, "")] * 4
        with self.assertRaisesRegex(Hamtfel, "^http-429$"):
            self.klient.text(self.bas + "/a")

    def test_robots_med_bom(self):
        Server.svar["/robots.txt"] = [(200, {}, "\ufeffUser-agent: *\nDisallow: /")]
        with self.assertRaisesRegex(Hamtfel, "^robots$"):
            self.klient.text(self.bas + "/a")

    def test_vardens_versaler_spelar_ingen_roll(self):
        Server.svar["/a"] = [(200, {}, "a")]
        Server.svar["/b"] = [(200, {}, "b")]
        self.klient.text(self.bas + "/a")
        self.klient.text(self.bas.replace("http", "HTTP") + "/b")
        self.assertEqual(self.vantat, [5, 5])


class TestInstallningar(unittest.TestCase):
    def test_hamtning_toml_lases(self):
        self.assertEqual(las(ROT / "hamtning.toml").intervall, 5)

    def stoppas(self, text: str):
        katalog = tempfile.TemporaryDirectory()
        self.addCleanup(katalog.cleanup)
        fil = Path(katalog.name) / "hamtning.toml"
        fil.write_text('user_agent = "x"\n' + text)
        with self.assertRaises(Konfigurationsfel):
            las(fil)

    def test_okant_falt_stoppar(self):
        self.stoppas("intervall = 5\ntakt = 1\n")

    def test_intervall_maste_vara_sekunder(self):
        self.stoppas("intervall = true\n")
        self.stoppas("intervall = -1\n")
