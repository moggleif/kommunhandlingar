"""Krav: K72 i docs/02-KRAV.md, ADR-0099. Test: tests/test_bildyta.py.

Den största bildytan på en renderad sida, i ett rutnät av 48 × 48 rutor:
rutor som är mörka eller färgade och inte täcks av lästa ord, och som
hänger ihop sida vid sida. Ytan är jämn när grannrutorna liknar varandra,
som i ett foto eller en karta och inte i brus
(docs/03-ARKITEKTUR.md#inskannade-sidor-som-inte-blir-text).
"""

from collections import deque
from dataclasses import dataclass

from PIL import Image, ImageChops, ImageDraw

RUTOR = 48
MORK = 200
FARGAD = 40
NASTAN_VIT = 245
I_RUTAN = 0.3
JAMN = 0.8


@dataclass(frozen=True)
class Yta:
    andel: float
    ruta: tuple[int, int, int, int] | None
    jamn: bool


def storsta(bild: Image.Image, ord_: list[tuple]) -> Yta:
    """Bildytan på sidan; `ord_` är rutor kring lästa ord i bildens pixlar."""
    celler = storsta_grupp(bildrutor(bild, ord_))
    if not celler:
        return Yta(0.0, None, False)
    x0, y0, x1, y1 = omslutande(celler)
    rb, rh = bild.width / RUTOR, bild.height / RUTOR
    ruta = (int(x0 * rb), int(y0 * rh), int(x1 * rb), int(y1 * rh))
    andel = (x1 - x0) * (y1 - y0) / RUTOR**2
    return Yta(andel, ruta, jamn(bild, celler))


def mork_andel(bild: Image.Image) -> float:
    andelar = per_ruta(mork(bild))
    return sum(andelar) / len(andelar)


def bildrutor(bild: Image.Image, ord_: list[tuple]) -> list[bool]:
    morka, fargade = per_ruta(mork(bild)), per_ruta(fargad(bild))
    lasta = per_ruta(ordmask(bild.size, ord_))
    return [
        lasta[i] <= I_RUTAN and (morka[i] >= I_RUTAN or fargade[i] >= I_RUTAN)
        for i in range(RUTOR * RUTOR)
    ]


def per_ruta(mask: Image.Image) -> list[float]:
    """Andelen av varje ruta som masken täcker, rad för rad."""
    return [v / 255 for v in mask.resize((RUTOR, RUTOR), Image.BOX).tobytes()]


def mork(bild: Image.Image) -> Image.Image:
    return bild.convert("L").point(lambda v: 255 if v < MORK else 0)


def fargad(bild: Image.Image) -> Image.Image:
    r, g, b = bild.convert("RGB").split()
    storsta_ = ImageChops.lighter(ImageChops.lighter(r, g), b)
    minsta = ImageChops.darker(ImageChops.darker(r, g), b)
    skillnad = ImageChops.subtract(storsta_, minsta)
    mattad = skillnad.point(lambda v: 255 if v > FARGAD else 0)
    inte_vit = bild.convert("L").point(lambda v: 255 if v < NASTAN_VIT else 0)
    return ImageChops.multiply(mattad, inte_vit)


def ordmask(storlek: tuple[int, int], ord_: list[tuple]) -> Image.Image:
    mask = Image.new("L", storlek, 0)
    rita = ImageDraw.Draw(mask)
    for ruta in ord_:
        rita.rectangle(ruta, fill=255)
    return mask


def storsta_grupp(rutor: list[bool]) -> list[int]:
    """Den grupp av sammanhängande rutor vars omslutande rektangel är störst."""
    sedda: set[int] = set()
    basta: list[int] = []
    for start in (i for i, bild in enumerate(rutor) if bild):
        if start in sedda:
            continue
        grupp = grupp_fran(start, rutor, sedda)
        if storlek(grupp) > storlek(basta):
            basta = grupp
    return basta


def grupp_fran(start: int, rutor: list[bool], sedda: set[int]) -> list[int]:
    ko, grupp = deque([start]), []
    sedda.add(start)
    while ko:
        cell = ko.popleft()
        grupp.append(cell)
        for granne in grannar(cell):
            if rutor[granne] and granne not in sedda:
                sedda.add(granne)
                ko.append(granne)
    return grupp


def grannar(cell: int) -> list[int]:
    y, x = divmod(cell, RUTOR)
    return [
        ny * RUTOR + nx
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
        if 0 <= ny < RUTOR and 0 <= nx < RUTOR
    ]


def omslutande(celler: list[int]) -> tuple[int, int, int, int]:
    ys, xs = [c // RUTOR for c in celler], [c % RUTOR for c in celler]
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def storlek(celler: list[int]) -> int:
    if not celler:
        return 0
    x0, y0, x1, y1 = omslutande(celler)
    return (x1 - x0) * (y1 - y0)


def jamn(bild: Image.Image, celler: list[int]) -> bool:
    """Medelavvikelsen mellan grannrutorna i ytan, delad med rutornas
    standardavvikelse, är under gränsen; i brus är den över 1."""
    gra = bild.convert("L").resize((RUTOR, RUTOR), Image.BOX).tobytes()
    i_ytan = set(celler)
    varden = [gra[c] for c in celler]
    medel = sum(varden) / len(varden)
    spridning = (sum((v - medel) ** 2 for v in varden) / len(varden)) ** 0.5
    skillnader = [
        abs(gra[c] - gra[g]) for c in celler for g in grannar(c) if g in i_ytan
    ]
    if spridning == 0:
        return True
    return sum(skillnader) / len(skillnader) / spridning < JAMN
