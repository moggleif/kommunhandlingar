"""Krav: K10 i docs/02-KRAV.md, ADR-0013. Test: tests/test_klient.py.

Håller intervallet per värd, följer robots.txt, följer inga omdirigeringar
och försöker igen vid 429, 5xx, tidsgräns och svar som bryts av.
"""

import time
from collections.abc import Callable
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from kommunhandlingar.fel import Hamtfel
from kommunhandlingar.hamtning import robots
from kommunhandlingar.hamtning.installningar import Installningar

FORSOK = 4
FORSTA_VANTAN = 5
LANGSTA_VANTAN = 300
TIDSGRANS = 60


class NyttForsok(Exception):
    def __init__(self, orsak: str, vantan: int | None = None):
        super().__init__(orsak)
        self.orsak, self.vantan = orsak, vantan


class IngenOmdirigering(HTTPRedirectHandler):
    def redirect_request(self, *_):
        return None


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
        self.oppnare = build_opener(IngenOmdirigering)

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
            if not fel.orsak.startswith("http-4") or fel.orsak == "http-429":
                raise
            return ()
        return robots.tolka(text, produkt(self.installningar.user_agent))

    def med_forsok(self, url: str) -> str:
        for forsok in range(FORSOK):
            try:
                return self.anrop(url)
            except NyttForsok as fel:
                if forsok == FORSOK - 1:
                    raise Hamtfel(fel.orsak) from fel
                self.sov(fel.vantan or FORSTA_VANTAN * 2**forsok)

    def anrop(self, url: str) -> str:
        self.vanta_pa(vard(url))
        fraga = Request(url, headers={"User-Agent": self.installningar.user_agent})
        try:
            with self.oppnare.open(fraga, timeout=TIDSGRANS) as svar:
                return avkoda(svar.read(), svar.headers.get_content_charset())
        except HTTPError as fel:
            raise http_fel(fel) from fel
        except OSError as fel:
            raise natfel(fel) from fel
        except HTTPException as fel:
            raise NyttForsok("avbrutet-svar") from fel
        finally:
            self.senast[vard(url)] = self.klocka()

    def vanta_pa(self, varden: str) -> None:
        if varden in self.senast:
            kvar = self.senast[varden] + self.installningar.intervall - self.klocka()
            if kvar > 0:
                self.sov(kvar)


def avkoda(innehall: bytes, teckenkodning: str | None) -> str:
    try:
        return innehall.decode(teckenkodning or "utf-8")
    except (LookupError, UnicodeDecodeError) as fel:
        raise Hamtfel("teckenkodning") from fel


def http_fel(fel: HTTPError) -> Exception:
    orsak = f"http-{fel.code}"
    if fel.code == 429 or fel.code >= 500:
        efter = fel.headers.get("Retry-After", "")
        return NyttForsok(
            orsak, min(int(efter), LANGSTA_VANTAN) if efter.isdigit() else None
        )
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
    return f"{delar.scheme}://{delar.netloc}".lower()


def produkt(user_agent: str) -> str:
    return user_agent.split("/")[0].split()[0]
