"""Krav: K11 i docs/02-KRAV.md, ADR-0006. Test: tests/test_tidsbudget.py.

Budgetens hårda gräns (docs/03-ARKITEKTUR.md#körning-och-incheckning).
När den nås avbryts det pågående dokumentet med `Tidsgrans`, utom medan
det skrivs: då skrivs det klart, och nästa dokument startar inte, eftersom
den mjuka gränsen redan är passerad.
"""

import signal
from contextlib import contextmanager


class Tidsgrans(BaseException):
    """BaseException, så att konverteringens fångst av alla fel inte tar den."""


def avbryt(signum, ram) -> None:
    raise Tidsgrans


def hard_grans(sekunder: int) -> None:
    signal.signal(signal.SIGALRM, avbryt)
    signal.alarm(sekunder)


@contextmanager
def utan_avbrott():
    signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
    try:
        yield
    finally:
        if signal.SIGALRM in signal.sigpending():
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
        signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGALRM})
