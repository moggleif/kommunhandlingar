"""Krav: K16 i docs/02-KRAV.md, ADR-0018. Test: tests/test_wayback.py.

Internet Archives CDX-tjänst, adressen till en kopia och kontrollen av
kapade kopior. `id_` i adressen ger filen som den sparades, utan arkivets
ram och med originalets länkar.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode

from kommunhandlingar.fel import Hamtfel

CDX = "https://web.archive.org/cdx/search/cdx"
# Var läsare av PDF letar efter filens slut (PDF 1.7, 7.5.5).
SLUTET = 1024


@dataclass(frozen=True)
class Kopia:
    tidsstampel: str
    original: str
    langd: int


def fraga(klient, adress: str, mimetyp: str, prefix: bool = False) -> list[Kopia]:
    parametrar = [
        ("url", adress),
        ("output", "json"),
        ("fl", "timestamp,original,length"),
        ("filter", "statuscode:200"),
        ("filter", f"mimetype:{mimetyp}"),
    ]
    if prefix:
        parametrar.append(("matchType", "prefix"))
    var = f"arkivets lista för {adress}"
    try:
        rader = json.loads(
            klient.text(f"{CDX}?{urlencode(parametrar)}").strip() or "[]"
        )
    except Hamtfel as fel:
        raise Hamtfel(fel.orsak, var) from fel
    except ValueError as fel:
        # Arkivet svarar ibland med en HTML-sida, "Temporarily Offline".
        raise Hamtfel("inte-json", var) from fel
    return [Kopia(tid, original, int(langd)) for tid, original, langd in rader[1:]]


def adress(kopia: Kopia) -> str:
    return f"https://web.archive.org/web/{kopia.tidsstampel}id_/{kopia.original}"


def sista_per_ar(kopior: list[Kopia]) -> list[Kopia]:
    sista = {k.tidsstampel[:4]: k for k in sorted(kopior, key=lambda k: k.tidsstampel)}
    return sorted(sista.values(), key=lambda k: k.tidsstampel, reverse=True)


def kapad(pdf: Path) -> bool:
    with pdf.open("rb") as fil:
        fil.seek(max(0, pdf.stat().st_size - SLUTET))
        return b"%%EOF" not in fil.read()
