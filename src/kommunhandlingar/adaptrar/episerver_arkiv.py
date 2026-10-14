"""Krav: K23 och K31 i docs/02-KRAV.md, ADR-0018, ADR-0039 och ADR-0049.
Test: tests/test_episerver_arkiv.py och tests/test_sammanslagning.py.

Organens mappar i Episerver-generationerna ur Internet Archive. Varje PDF
under en mapp är en fil, också när arkivet har den under http och https,
med och utan www; filen får arkivets största kopia och vid lika den äldsta.
En mapp som arkivet inte svarar för hoppas över och returneras som en
notering. Ett mötes filer av samma typ i samma mapp, till exempel en per
ärende, blir en kandidat i delar, i sökvägarnas ordning med talen som tal.
Mappen hör till gruppen, så att två nämnder som lagts under samma organ
inte slås ihop när de möttes samma dag.
"""

import re
from dataclasses import replace
from urllib.parse import quote, unquote, urlsplit

from kommunhandlingar.adaptrar import episerver, wayback
from kommunhandlingar.fel import Hamtfel, IngenKandidat
from kommunhandlingar.kandidat import Avvisad, Kandidat


def upptack(
    kalla: episerver.Kalla, klient
) -> tuple[list[Kandidat], list[Avvisad], list[str]]:
    kandidater, avvisade, noteringar = [], [], []
    for organ, mappar in kalla.mappar.items():
        for mapp in mappar:
            try:
                kopior = wayback.fraga(klient, mapp, "application/pdf", True)
            except Hamtfel as fel:
                noteringar.append(str(fel))
                continue
            nya, bort = las_mapp(kalla, organ, mapp, kopior)
            kandidater, avvisade = kandidater + nya, avvisade + bort
    return moten(kandidater), avvisade, noteringar


def moten(kandidater: list[Kandidat]) -> list[Kandidat]:
    grupper: dict[tuple, list[Kandidat]] = {}
    for k in kandidater:
        grupper.setdefault((k.organ, k.kalla, k.datum, k.typ), []).append(k)
    return [
        filer[0] if len(filer) == 1 else i_delar(filer) for filer in grupper.values()
    ]


def i_delar(filer: list[Kandidat]) -> Kandidat:
    """Nyckeln är mappens, mötets och typens, så att den inte beror på
    vilken del som kom först. Ett blanksteg i en adress kodas, så att listan
    går att läsa."""
    filer = sorted(filer, key=lambda k: naturlig(unquote(k.kallnyckel)))
    forsta = filer[0]
    mapp = quote(unquote(forsta.kalla), safe="/")
    nyckel = f"episerver:{mapp}{forsta.datum.isoformat()}/{forsta.typ}"
    delar = tuple(k.url.replace(" ", "%20") for k in filer)
    return replace(forsta, kallnyckel=nyckel, delar=delar)


def naturlig(text: str) -> list:
    return [int(d) if d.isdigit() else d for d in re.split(r"(\d+)", text)]


def las_mapp(
    kalla: episerver.Kalla, organ: str, mapp: str, kopior: list[wayback.Kopia]
) -> tuple[list[Kandidat], list[Avvisad]]:
    kandidater, avvisade = [], []
    for kopia in basta(kopior).values():
        try:
            kandidater.append(kandidat(kalla, organ, mapp, kopia))
        except IngenKandidat as fel:
            avvisade.append(Avvisad(mapp, filnamn(kopia), str(fel)))
    return kandidater, avvisade


def nyckel_av(original: str) -> str:
    """Värden utan www och port, och sökvägen kodad på ett enda sätt."""
    delar = urlsplit(original)
    vard = delar.hostname.removeprefix("www.")
    return f"episerver:{vard}{quote(unquote(delar.path), safe='/')}"


def basta(kopior: list[wayback.Kopia]) -> dict[str, wayback.Kopia]:
    basta: dict[str, wayback.Kopia] = {}
    for kopia in sorted(kopior, key=lambda k: (k.langd, -int(k.tidsstampel))):
        basta[nyckel_av(kopia.original)] = kopia
    return basta


def kandidat(
    kalla: episerver.Kalla, organ: str, mapp: str, kopia: wayback.Kopia
) -> Kandidat:
    nyckel = nyckel_av(kopia.original)
    typ, datum = episerver.typ_och_datum(kalla, under(mapp, kopia), nyckel)
    return Kandidat(
        organ=organ,
        datum=datum,
        typ=typ,
        url=wayback.adress(kopia),
        kalla=mapp,
        kallnyckel=nyckel,
        filnamn=filnamn(kopia),
    )


def under(mapp: str, kopia: wayback.Kopia) -> str:
    """Sökvägen under mappen, avkodad."""
    mappens = unquote(mapp.split("/", 1)[1])
    return unquote(urlsplit(kopia.original).path).lstrip("/")[len(mappens) :]


def filnamn(kopia: wayback.Kopia) -> str:
    return unquote(urlsplit(kopia.original).path).rsplit("/", 1)[-1]
