"""Krav: K14 och K33 i docs/02-KRAV.md. Bygger webbplatsen:
<utkatalog> <repoadress> <avvikelsefil>, där avvikelsefilen har de öppna
avvikelserna i källan, ett issue per rad (ADR-0054).
"""

import sys
from datetime import UTC, datetime
from pathlib import Path

from kommunhandlingar.webbplats import avvikelser
from kommunhandlingar.webbplats.avvikelsesida import avvikelsesida
from kommunhandlingar.webbplats.bygg import bygg

utkatalog, repo, avvikelsefil = sys.argv[1:]
mall = bygg(Path.cwd(), Path(utkatalog), repo, datetime.now(UTC))
html = avvikelsesida(mall, avvikelser.las(Path(avvikelsefil)))
(Path(utkatalog) / avvikelser.ADRESS).write_text(html, encoding="utf-8")
