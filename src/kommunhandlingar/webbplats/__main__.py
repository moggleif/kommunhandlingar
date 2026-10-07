"""Krav: K14 i docs/02-KRAV.md. Bygger webbplatsen: <utkatalog> <repoadress>."""

import sys
from datetime import UTC, datetime
from pathlib import Path

from kommunhandlingar.webbplats.bygg import bygg

utkatalog, repo = sys.argv[1:]
bygg(Path.cwd(), Path(utkatalog), repo, datetime.now(UTC))
