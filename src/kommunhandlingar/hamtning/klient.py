"""Krav: K10 i docs/02-KRAV.md, ADR-0013. Test: tests/test_klient.py.

Håller intervallet per värd, följer robots.txt och försöker igen vid 429,
5xx, tidsgräns och en anslutning som stängs utan svar.
"""

import time
from collections.abc import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from kommunhandlingar.fel import Hamtfel
from kommunhandlingar.hamtning import robots
from kommunhandlingar.hamtning.installningar import Installningar

FORSOK = 4
FORSTA_VANTAN = 5
TIDSGRANS = 60


class NyttForsok(Exception):
    def __init__(self, orsak: str, vantan: int | None = None):
        super().__init__(orsak)
        self.vantan = vantan


class Klient:
    def __init__(
        self,
        installningar: Installningar,
        klocka: Callable[[], float] = time.monotonic,
        sov: Callable[[float], None] = time.sleep,
    ):
        self.installningar = installningar
        self.klocka, self.sov = klocka, sov
        self.senast: dict[str, float] = {}
        self.regler: dict[str, tuple[robots.Regel, ...]] = {}

    def text(self, url: str) -> str:
        if not robots.tillater(self.robotregler(url), url):
            raise Hamtfel("robots")
        return self.med_forsok(url)

    def robotregler(self, url: str) -> tuple[robots.Regel, ...]:
        varden = vard(url)
        if varden not in self.regler:
            self.regler[varden] = self.las_robots(varden)
        return self.regler[varden]

    def las_robots(self, varden: str) -> tuple[robots.Regel, ...]:
        try:
            text = self.med_forsok(f"{varden}/robots.txt")
        except Hamtfel as fel:
            if not str(fel).startswith("http-4"):
                raise
            return ()
        return robots.tolka(text, produkt(self.installningar.user_agent))

    def med_forsok(self, url: str) -> str:
        for forsok in range(1, FORSOK):
            try:
                return self.anrop(url)
            except NyttForsok as fel:
                self.sov(fel.vantan or FORSTA_VANTAN * 2 ** (forsok - 1))
        try:
            return self.anrop(url)
        except NyttForsok as fel:
            raise Hamtfel(str(fel)) from fel

    def anrop(self, url: str) -> str:
        self.vanta_pa(vard(url))
        fraga = Request(url, headers={"User-Agent": self.installningar.user_agent})
        try:
            with urlopen(fraga, timeout=TIDSGRANS) as svar:
                return svar.read().decode(svar.headers.get_content_charset() or "utf-8")
        except HTTPError as fel:
            raise http_fel(fel) from fel
        except OSError as fel:
            raise natfel(fel) from fel
        finally:
            self.senast[vard(url)] = self.klocka()

    def vanta_pa(self, varden: str) -> None:
        if varden in self.senast:
            kvar = self.senast[varden] + self.installningar.intervall - self.klocka()
            if kvar > 0:
                self.sov(kvar)


def http_fel(fel: HTTPError) -> Exception:
    orsak = f"http-{fel.code}"
    if fel.code == 429 or fel.code >= 500:
        efter = fel.headers.get("Retry-After", "")
        return NyttForsok(orsak, int(efter) if efter.isdigit() else None)
    return Hamtfel(orsak)


def natfel(fel: OSError) -> Exception:
    # urllib slår in fel vid sändningen i URLError, men inte vid svaret.
    grund = fel.reason if isinstance(fel, URLError) else fel
    if isinstance(grund, ConnectionResetError):
        return NyttForsok("tomt-svar")
    if isinstance(grund, TimeoutError):
        return NyttForsok("tidsgrans")
    return Hamtfel("anslutning")


def vard(url: str) -> str:
    delar = urlsplit(url)
    return f"{delar.scheme}://{delar.netloc}"


def produkt(user_agent: str) -> str:
    return user_agent.split("/")[0].split()[0]
