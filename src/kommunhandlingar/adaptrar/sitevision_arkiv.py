"""Krav: K16 i docs/02-KRAV.md, ADR-0018 och ADR-0011.
Test: tests/test_sitevision_arkiv.py.

En Sitevision-källa ur Internet Archive. Den sista ögonblicksbilden per år
av varje mötessida läses med Sitevision-adaptern, den nyaste först, och
varje fil får arkivets största kopia av sin nyaste version. En fråga som
arkivet inte besvarar, och en mötessida som arkivet inte har, hoppas över
och returneras som en notering.
"""

from dataclasses import replace
from urllib.parse import urlsplit

from kommunhandlingar.adaptrar import sitevision, wayback
from kommunhandlingar.adaptrar.sitevision_html import NEDLADDNING
from kommunhandlingar.fel import Hamtfel
from kommunhandlingar.kandidat import Avvisad, Kandidat


def upptack(
    kalla: sitevision.Kalla, klient
) -> tuple[list[Kandidat], list[Avvisad], list[str]]:
    try:
        filer = nyaste_kopior(klient, kalla)
    except Hamtfel as fel:
        return [], [], [str(fel)]
    sidor, noteringar = [], []
    for organ, sidadress in kalla.sidor.items():
        bilder, fel = ogonblicksbilder(klient, sidadress)
        sidor += [(organ, bild, html) for bild, html in bilder]
        noteringar += fel
    kandidater, avvisade = sitevision.las(kalla, sidor)
    med_kopior = [med_kopia(k, filer) for k in kandidater]
    return (
        [k for k in med_kopior if isinstance(k, Kandidat)],
        avvisade + [a for a in med_kopior if isinstance(a, Avvisad)],
        noteringar,
    )


def nyaste_kopior(klient, kalla: sitevision.Kalla) -> dict[str, wayback.Kopia]:
    vardar = sorted({urlsplit(adress).netloc for adress in kalla.sidor.values()})
    kopior = [
        kopia
        for vard in vardar
        for kopia in wayback.fraga(klient, f"{vard}/download/", "application/pdf", True)
        if NEDLADDNING.match(kopia.original)
    ]
    basta: dict[str, wayback.Kopia] = {}
    for kopia in sorted(kopior, key=rang):
        basta[f"sitevision:{NEDLADDNING.match(kopia.original)[1]}"] = kopia
    return basta


def rang(kopia: wayback.Kopia) -> tuple[int, int, int]:
    """Nyaste versionen, sedan största kopian, och vid lika den äldsta."""
    version = int(NEDLADDNING.match(kopia.original)[2])
    return version, kopia.langd, -int(kopia.tidsstampel)


def ogonblicksbilder(klient, sidadress: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Den sista ögonblicksbilden per år, den nyaste först, med sin HTML."""
    try:
        kopior = wayback.fraga(klient, sidadress, "text/html")
    except Hamtfel as fel:
        return [], [str(fel)]
    if not kopior:
        return [], [f"{sidadress}: ingen kopia av mötessidan i arkivet"]
    bilder, fel = [], []
    for adress in map(wayback.adress, wayback.sista_per_ar(kopior)):
        try:
            bilder.append((adress, klient.text(adress)))
        except Hamtfel as hamtfel:
            fel.append(f"{adress}: {hamtfel.orsak}")
    return bilder, fel


def med_kopia(kandidat: Kandidat, filer: dict[str, wayback.Kopia]):
    kopia = filer.get(kandidat.kallnyckel)
    if kopia is None:
        return Avvisad(kandidat.kalla, kandidat.filnamn, "ingen kopia i arkivet")
    return replace(kandidat, url=wayback.adress(kopia))
