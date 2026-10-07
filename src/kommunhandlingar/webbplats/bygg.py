"""Krav: K14 i docs/02-KRAV.md. Test: tests/test_webbplats.py."""

from datetime import datetime
from pathlib import Path

from kommunhandlingar import konfiguration
from kommunhandlingar.webbplats import frontmatter, sidor


def bygg(rot: Path, ut: Path, repo: str, byggd: datetime) -> None:
    kommuner = [konfiguration.las(f) for f in sorted((rot / "kommuner").glob("*.toml"))]
    mall = sidor.Mall(kommuner, repo, byggd)
    ut.mkdir(parents=True, exist_ok=True)
    skriv(ut / "index.html", sidor.startsida(mall))
    for kommun in kommuner:
        dokument = las_dokument(rot / "data" / kommun.id)
        skriv(ut / f"{kommun.id}.html", sidor.statussida(mall, kommun, dokument))


def las_dokument(katalog: Path) -> list[dict[str, str]]:
    return [
        frontmatter.las(fil.read_text(encoding="utf-8"))
        for fil in sorted(katalog.rglob("*.md"))
    ]


def skriv(fil: Path, html: str) -> None:
    fil.write_text(html, encoding="utf-8")
