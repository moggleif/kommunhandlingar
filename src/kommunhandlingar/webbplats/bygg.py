"""Krav: K14 i docs/02-KRAV.md. Test: tests/test_webbplats.py."""

from datetime import datetime
from pathlib import Path

from kommunhandlingar import frontmatter, konfiguration
from kommunhandlingar.fel import Datafel
from kommunhandlingar.konfiguration import Kommun
from kommunhandlingar.webbplats import sidor
from kommunhandlingar.webbplats.rakning import okanda


def bygg(rot: Path, ut: Path, repo: str, byggd: datetime) -> None:
    kommuner = [konfiguration.las(f) for f in sorted((rot / "kommuner").glob("*.toml"))]
    mall = sidor.Mall(kommuner, repo, byggd)
    ut.mkdir(parents=True, exist_ok=True)
    (ut / "index.html").write_text(sidor.startsida(mall), encoding="utf-8")
    for kommun in kommuner:
        dokument = las_dokument(rot / "data" / kommun.id, kommun)
        html = sidor.statussida(mall, kommun, dokument)
        (ut / f"{kommun.id}.html").write_text(html, encoding="utf-8")


def las_dokument(katalog: Path, kommun: Kommun) -> list[dict[str, str]]:
    dokument = []
    for fil in sorted(katalog.rglob("*.md")):
        falt = frontmatter.las(fil.read_text(encoding="utf-8"))
        if fel := okanda(falt, kommun):
            raise Datafel(f"{fil}: okänt {', '.join(fel)}")
        dokument.append(falt)
    return dokument
