"""Tillfälligt prov för #344: läser de olästa sidorna i urvalet med K72 och
skriver mått, OCR-text och en liten bild per sida. Tas bort före PR."""
import gzip, subprocess, base64, csv, io, json, re, sys, tempfile
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

def tsv_for(gra, psm):
    with tempfile.TemporaryDirectory() as k:
        f = Path(k) / "s.png"; gra.save(f)
        return subprocess.run(["tesseract", f, "-", "-l", "swe", "--dpi", "300", "--psm", psm, "tsv"], capture_output=True, text=True).stdout

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
                gra = ocr.rendera(dok[nr - 1])
                for psm in ("3", "11"):
                    tsv = tsv_for(gra, psm)
                    print("TSV " + json.dumps([r["nr"], psm, base64.b64encode(gzip.compress(tsv.encode())).decode()]), flush=True)

if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
