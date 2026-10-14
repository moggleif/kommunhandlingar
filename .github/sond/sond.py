"""Tillfällig sond (#159): Episerver-mapparna ur arkivet. Tas bort före PR."""

import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import pypdfium2 as pdfium

from kommunhandlingar import konfiguration
from kommunhandlingar.adaptrar import episerver_arkiv
from kommunhandlingar.hamtning import installningar
from kommunhandlingar.hamtning.klient import Klient

kommun = konfiguration.las(Path("kommuner/kungsbacka.toml"))
klient = Klient(installningar.las(Path("hamtning.toml")))
alla, bort, noter = [], [], []
for kalla in kommun.arkivkallor:
    k, b, n = episerver_arkiv.upptack(kalla, klient)
    alla, bort, noter = alla + k, bort + b, noter + n
print(f"KANDIDATER {len(alla)}  AVVISADE {len(bort)}")
for n in noter:
    print("NOTERING", n)
per_mapp = Counter(k.kalla for k in alla)
for kalla in kommun.arkivkallor:
    for organ, mappar in kalla.mappar.items():
        for mapp in mappar:
            ar = sorted({k.datum.year for k in alla if k.kalla == mapp})
            span = f"{ar[0]}-{ar[-1]}" if ar else "-"
            print(f"MAPP {organ:10} {per_mapp[mapp]:5} {span:9} {mapp}")
delar = defaultdict(list)
for k in alla:
    delar[k.organ].append(len(k.delar) or 1)
for organ, n in sorted(delar.items()):
    typer = Counter(k.typ for k in alla if k.organ == organ)
    print(f"ORGAN {organ:10} kand {len(n):5} filer {sum(n):6} maxdelar {max(n):4} {dict(typer)}")
orsaker = Counter((b.orsak, b.kalla) for b in bort)
for (orsak, mapp), n in orsaker.most_common():
    exempel = [b.filnamn for b in bort if b.orsak == orsak and b.kalla == mapp][:6]
    print(f"AVVISAD {n:5} {orsak} | {mapp} | {exempel}")
fs = [k for k in alla if "Funktionsst" in (k.adresser()[0].replace("%C3%B6", "ö"))]
print("FUNKTIONSSTOD", len(fs))
for k in fs[:2]:
    with tempfile.TemporaryDirectory() as d:
        pdf = Path(d) / "f.pdf"
        klient.fil(k.adresser()[0], pdf)
        sida = pdfium.PdfDocument(pdf)[0].get_textpage().get_text_range()
        print("FS", k.datum, k.typ, k.adresser()[0])
        print(sida[:1200])
