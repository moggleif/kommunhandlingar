"""Tillfällig sond (#159): sökvägarna under några mappar. Tas bort före PR."""

from pathlib import Path

from kommunhandlingar import konfiguration
from kommunhandlingar.adaptrar import episerver_arkiv, wayback
from kommunhandlingar.hamtning import installningar
from kommunhandlingar.hamtning.klient import Klient

A = "kungsbacka.se/globalassets/kommun-och-politik/dokument/moten-handlingar-och-protokoll/"
MAPPAR = {
    "ks": A + "kommunstyrelsen/",
    "fg": A + "forskola-och-grundskola/",
    "revision": A + "kommunrevisionen/",
}
kommun = konfiguration.las(Path("kommuner/kungsbacka.toml"))
klient = Klient(installningar.las(Path("hamtning.toml")))
kalla = kommun.arkivkallor[0]
for organ, mapp in MAPPAR.items():
    kopior = wayback.fraga(klient, mapp, "application/pdf", True)
    kand, bort = episerver_arkiv.las_mapp(kalla, organ, mapp, kopior)
    for k in kand:
        if k.datum.year > 2023 or organ == "ks" and k.datum.year == 2020:
            print("KAND", organ, k.datum, k.typ, k.kallnyckel)
    for kopia in episerver_arkiv.basta(kopior).values():
        under = episerver_arkiv.under(mapp, kopia)
        if any(b.filnamn == episerver_arkiv.filnamn(kopia) for b in bort):
            print("BORT", organ, under)
