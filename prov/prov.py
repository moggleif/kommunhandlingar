"""Tillfälligt prov för #344: läser de olästa sidorna i urvalet med K72 och
skriver mått, OCR-text och en liten bild per sida. Tas bort före PR."""
import base64, csv, io, json, re, sys, tempfile
from pathlib import Path
import pdfplumber, pypdfium2 as pdfium
from kommunhandlingar import frontmatter, original
from kommunhandlingar.hamtning import installningar
from kommunhandlingar.hamtning.klient import Klient
from kommunhandlingar.konvertering import bildyta, ocr, riktning
from kommunhandlingar.konvertering.las_sida import las_sida

PRICK = re.compile(r"^[.·…,:_\-–—]{2,}$|^\.{3,}")

def matt(rendering):
    gra = ocr.rendera(rendering)
    forsta = ocr.las_bild(gra)
    rader = ocr.ordrader(forsta[0]) if forsta else []
    conf = [float(r["conf"]) for r in rader]
    ej_prick = [float(r["conf"]) for r in rader if not PRICK.match(r["text"].strip())]
    farg = rendering.render(scale=100 / 72).to_pil()
    yta = bildyta.storsta(farg, [])
    return dict(
        ord=len(conf),
        medel=round(sum(conf) / len(conf), 1) if conf else None,
        prickord=len(conf) - len(ej_prick),
        medel_utan_prickar=round(sum(ej_prick) / len(ej_prick), 1) if ej_prick else None,
        mork=round(bildyta.mork_andel(farg), 4),
        bildyta=round(yta.andel, 3), jamn=yta.jamn,
        grader=riktning.grader(gra),
        text=(forsta[1] if forsta else "")[:600],
    ), gra

def miniatyr(gra):
    b = gra.copy(); b.thumbnail((1000, 1400))
    ut = io.BytesIO(); b.save(ut, "JPEG", quality=40)
    return base64.b64encode(ut.getvalue()).decode()

def main(urval, delnr):
    klient = Klient(installningar.las(Path("hamtning.toml")))
    per_dok = {}
    for r in csv.DictReader(open(urval)):
        if int(r["del"]) == delnr:
            per_dok.setdefault((r["repo"], r["md"]), []).append(r)
    for (repo, md), rader in per_dok.items():
        bas = Path("rh") if repo == "regionhalland" else Path(".")
        falt = frontmatter.las((bas / md).read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as t:
            pdf = Path(t) / "o.pdf"
            try:
                original.hamta(klient, frontmatter.adresser(falt["kalla_url"]), pdf, arkiv=False)
            except Exception as fel:
                print("PROVFEL", repo, md, fel, flush=True); continue
            plumb, dok = pdfplumber.open(pdf), pdfium.PdfDocument(pdf)
            for r in rader:
                nr = int(r["sida"])
                try:
                    k73 = las_sida(plumb.pages[nr - 1], dok[nr - 1])
                    m = {}
                except Exception as fel:
                    print("PROVFEL", repo, md, nr, fel, flush=True); continue
                rad = dict(r, k73=k73.kvalitet, figur=k73.figur, text=k73.text)
                print("PROV " + json.dumps(rad, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
