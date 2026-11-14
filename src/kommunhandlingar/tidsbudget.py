"""Krav: K11 och K52 i docs/02-KRAV.md, ADR-0006 och ADR-0075.
Test: tests/test_tidsbudget.py.

Budgetens hårda gräns (docs/03-ARKITEKTUR.md#körning-och-incheckning).
När den nås avbryts det pågående dokumentet med `Tidsgrans`, utom medan
det skrivs: då skrivs det klart, och nästa dokument startar inte, eftersom
den mjuka gränsen redan är passerad. Dokumentets egen gräns (`hogst`)
avbryter med `Dokumentgrans`, utom när den hårda gränsen kommer först.
"""

import signal
import time
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta

MJUK = timedelta(hours=5)
HARD = timedelta(hours=5, minutes=30)
DOKUMENT = 30 * 60
FEL = "tidsgrans"
START = "jobbets start i sekunder sedan epoken; tidsbudgeten räknas därifrån"


class Tidsgrans(BaseException):
    """BaseException, så att konverteringens fångst av alla fel inte tar den."""


class Dokumentgrans(BaseException):
    """BaseException av samma skäl som `Tidsgrans`."""


def avbryt(signum, ram) -> None:
    raise Tidsgrans


def avbryt_dokumentet(signum, ram) -> None:
    raise Dokumentgrans


def tidpunkt(sekunder: str) -> datetime:
    return datetime.fromtimestamp(int(sekunder), UTC)


def mjuk_grans(start: datetime | None) -> datetime:
    return datetime.max.replace(tzinfo=UTC) if start is None else start + MJUK


def starta_hard_grans(start: datetime, nu: datetime) -> None:
    signal.signal(signal.SIGALRM, avbryt)
    signal.alarm(max(1, int((start + HARD - nu).total_seconds())))


def stoppa() -> None:
    signal.alarm(0)


@contextmanager
def utan_avbrott():
    signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
    try:
        yield
    finally:
        if signal.SIGALRM in signal.sigpending():
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
        signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGALRM})


@contextmanager
def hogst(sekunder: int):
    """Larmet för den hårda gränsen står kvar när det kommer först, och
    ställs annars tillbaka efteråt, räknat på bråkdelar av sekunder."""
    kvar = signal.getitimer(signal.ITIMER_REAL)[0]
    if kvar and kvar <= sekunder:
        yield
        return
    slut = time.monotonic() + kvar
    tidigare = signal.signal(signal.SIGALRM, avbryt_dokumentet)
    signal.setitimer(signal.ITIMER_REAL, sekunder)
    try:
        yield
    finally:
        with utan_avbrott():
            signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, tidigare)
        if kvar:
            signal.setitimer(signal.ITIMER_REAL, max(0.001, slut - time.monotonic()))
