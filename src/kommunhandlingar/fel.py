"""Krav: K1 och K2. Test: tests/test_konfiguration.py, tests/test_monster.py."""


class Konfigurationsfel(Exception):
    """Kommunfilen följer inte schemat; körningen stoppas innan något hämtas (K1)."""


class IngenKandidat(Exception):
    """En fil blir ingen kandidat; orsaken nämns i sammanfattningen (K2)."""

    def __init__(self, orsak: str):
        super().__init__(orsak)
        self.orsak = orsak
