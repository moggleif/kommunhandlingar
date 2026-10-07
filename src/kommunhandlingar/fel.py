"""Krav: K1, K2, K10 och K14. Test: tests/test_konfiguration.py,
tests/test_monster.py, tests/test_webbplats.py, tests/test_klient.py."""


class Konfigurationsfel(Exception):
    """Kommunfilen följer inte schemat; körningen stoppas innan något hämtas (K1)."""


class IngenKandidat(Exception):
    """En fil blir ingen kandidat; orsaken nämns i sammanfattningen (K2)."""


class Datafel(Exception):
    """Ett dokument i poolen följer inte schemat; webbplatsbygget stoppas (K14)."""


class Hamtfel(Exception):
    """En adress gick inte att hämta; `orsak` är koden, som `http-404` (K10)."""

    def __init__(self, orsak: str, adress: str = ""):
        super().__init__(f"{adress}: {orsak}" if adress else orsak)
        self.orsak = orsak
