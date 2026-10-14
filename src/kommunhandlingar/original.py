"""Krav: K4, K16 och K31 i docs/02-KRAV.md, ADR-0018 och ADR-0049.
Test: tests/test_hamta.py och tests/test_sammanslagning.py.

Ett dokuments original hämtas till en PDF. Ett dokument i flera delar
hämtas del för del och slås ihop i delarnas ordning; sha256 och storlek
står då per del, eftersom den hopslagna filen inte blir byte för byte
densamma två gånger. En kapad kopia ur arkivet är ett hämtfel för hela
dokumentet. En del som inte går att öppna ger dokumentet orsaken i `fel`.
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path

import pypdfium2 as pdfium

from kommunhandlingar.adaptrar import wayback
from kommunhandlingar.fel import Hamtfel
from kommunhandlingar.konvertering.dokument import oppningsfel


@dataclass(frozen=True)
class Original:
    sha256: str | list[str]
    bytes: int | list[int]
    pdf: Path
    fel: str | None = None


def hamta(klient, adresser: list[str], pdf: Path, arkiv: bool) -> Original:
    if len(adresser) == 1:
        sha256, storlek = hamta_del(klient, adresser[0], pdf, arkiv)
        return Original(sha256, storlek, pdf)
    delar = [pdf.with_name(f"del-{nr}.pdf") for nr in range(len(adresser))]
    par = zip(adresser, delar, strict=True)
    hamtade = [hamta_del(klient, adress, del_, arkiv) for adress, del_ in par]
    sha256 = [sha for sha, _ in hamtade]
    storlekar = [storlek for _, storlek in hamtade]
    return Original(sha256, storlekar, pdf, sla_ihop(delar, pdf))


def hamta_del(klient, adress: str, mal: Path, arkiv: bool) -> tuple[str, int]:
    klient.fil(adress, mal)
    if arkiv and wayback.kapad(mal):
        raise Hamtfel("kapad", adress)
    with mal.open("rb") as fil:
        return hashlib.file_digest(fil, "sha256").hexdigest(), mal.stat().st_size


def sla_ihop(delar: list[Path], mal: Path) -> str | None:
    """Delarna i ordning till en PDF, eller orsaken till att en del inte
    gick att öppna."""
    hel = pdfium.PdfDocument.new()
    for del_ in delar:
        try:
            with pdfium.PdfDocument(del_) as dokument:
                hel.import_pages(dokument)
        except pdfium.PdfiumError as fel:
            return oppningsfel(fel)
    hel.save(mal)
    return None
