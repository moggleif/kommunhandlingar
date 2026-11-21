"""Krav: K72 i docs/02-KRAV.md, ADR-0099. Test: tests/test_skannad.py.

Hur många grader en inskannad sida ska vridas medurs för att stå rätt,
enligt Tesseracts orienteringsdetektering (`--psm 0`, modellen `osd`).
En osäker riktning, en sida med för lite text, eller en detektering som
fallerar, ger 0
(docs/03-ARKITEKTUR.md#inskannade-sidor-som-inte-blir-text).
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

from kommunhandlingar.konvertering import ocr

MINSTA_SAKERHET = 2.0
VRID = re.compile(r"^Rotate: (\d+)$", re.MULTILINE)
SAKERHET = re.compile(r"^Orientation confidence: ([\d.]+)$", re.MULTILINE)
# Tesseracts svar när sidan har för lite text för att ha en riktning.
FOR_LITE_TEXT = "Too few characters"


def grader(bild: Image.Image) -> int:
    svar = detektera(bild)
    vrid, sakerhet = VRID.search(svar), SAKERHET.search(svar)
    if not vrid or not sakerhet or float(sakerhet[1]) < MINSTA_SAKERHET:
        return 0
    return int(vrid[1])


def detektera(bild: Image.Image) -> str:
    with tempfile.TemporaryDirectory() as katalog:
        fil = Path(katalog) / "sida.png"
        bild.save(fil)
        try:
            svar = subprocess.run(
                ["tesseract", fil, "-", "--psm", "0", "--dpi", str(ocr.DPI)],
                capture_output=True,
                text=True,
                timeout=ocr.TIDSGRANS,
            )
        except subprocess.TimeoutExpired as fel:
            print(f"Tesseract, riktning: {fel}", file=sys.stderr)
            return ""
    if svar.returncode != 0 and FOR_LITE_TEXT not in svar.stderr:
        print(f"Tesseract, riktning: {svar.stderr.strip()}", file=sys.stderr)
    return svar.stdout
