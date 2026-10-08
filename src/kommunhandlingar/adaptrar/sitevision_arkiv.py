"""Krav: K16 i docs/02-KRAV.md, ADR-0018 och ADR-0011.
Test: tests/test_sitevision_arkiv.py.

En Sitevision-källa ur Internet Archive. Den sista ögonblicksbilden per år
av varje mötessida läses med Sitevision-adaptern, den nyaste först, och
varje fil får arkivets största kopia av sin nyaste version. En fråga som
arkivet inte besvarar hoppas över och returneras som obesvarad.
"""

import re
from dataclasses import replace
from urllib.parse import urlsplit

from kommunhandlingar.adaptrar import sitevision, wayback
from kommunhandlingar.fel import Hamtfel
from kommunhandlingar.kandidat import Avvisad, Kandidat

# Nod-id:t och versionens tidsstämpel i en nedladdningsadress.
NEDLADDNING = re.compile(r"/download/(18\.[0-9a-f]+)/(\d+)/")


def upptack(
    kalla: sitevision.Kalla, klient
) -> tuple[list[Kandidat], list[Avvisad], list[str]]:
    obesvarade: list[str] = []
    try:
        filer = nyaste_kopior(klient, kalla)
    except Hamtfel as fel:
        return [], [], [str(fel)]
    sidor = [
        (organ, bild, html)
        for organ, sidadress in kalla.sidor.items()
        for bild, html in ogonblicksbilder(klient, sidadress, obesvarade)
    ]
    kandidater, avvisade = sitevision.las(kalla, sidor)
    med_kopior = [med_kopia(k, filer) for k in kandidater]
    return (
        [k for k in med_kopior if isinstance(k, Kandidat)],
        avvisade + [a for a in med_kopior if isinstance(a, Avvisad)],
        obesvarade,
    )


def nyaste_kopior(klient, kalla: sitevision.Kalla) -> dict[str, wayback.Kopia]:
    vardar = sorted({urlsplit(adress).netloc for adress in kalla.sidor.values()})
    kopior = [
        kopia
        for vard in vardar
        for kopia in fraga(klient, f"{vard}/download/", "application/pdf", True)
        if NEDLADDNING.search(kopia.original)
    ]
    basta: dict[str, wayback.Kopia] = {}
    for kopia in sorted(kopior, key=rang):
        basta[f"sitevision:{NEDLADDNING.search(kopia.original)[1]}"] = kopia
    return basta


def rang(kopia: wayback.Kopia) -> tuple[int, int, int]:
    """Nyaste versionen, sedan största kopian, och vid lika den äldsta."""
    version = int(NEDLADDNING.search(kopia.original)[2])
    return version, kopia.langd, -int(kopia.tidsstampel)


def fraga(klient, adress: str, mimetyp: str, prefix: bool = False):
    try:
        return wayback.fraga(klient, adress, mimetyp, prefix)
    except Hamtfel as fel:
        raise Hamtfel(fel.orsak, f"arkivets lista för {adress}") from fel


def ogonblicksbilder(klient, sidadress: str, obesvarade: list[str]):
    """Den sista ögonblicksbilden per år, den nyaste först, med sin HTML."""
    try:
        kopior = fraga(klient, sidadress, "text/html")
    except Hamtfel as fel:
        obesvarade.append(str(fel))
        return
    for kopia in wayback.sista_per_ar(kopior):
        bild = wayback.adress(kopia)
        try:
            html = klient.text(bild)
        except Hamtfel as fel:
            obesvarade.append(f"{bild}: {fel.orsak}")
            continue
        yield bild, html


def med_kopia(kandidat: Kandidat, filer: dict[str, wayback.Kopia]):
    kopia = filer.get(kandidat.kallnyckel)
    if kopia is None:
        return Avvisad(kandidat.kalla, kandidat.filnamn, "ingen kopia i arkivet")
    return replace(kandidat, url=wayback.adress(kopia))
