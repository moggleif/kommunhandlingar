"""Krav: K5, ADR-0028 och ADR-0029. Skapar `delade.pdf` för tests/test_delade.py.

Körs för hand med reportlab, som inte är projektets beroende:
`python tests/fixtures/pdf/skapa_delade.py`. Varje sida är en tabell med
linjer där en cell rymmer mer än ett tal.

1. Rubrikraden saknar lodräta linjer; åren står i samma ruta.
2. Tre rader i varje ruta, utan vågräta linjer emellan.
3. Rubrik och värde i samma ruta, etiketten på värdets höjd.
4. Två tal i rutan men etiketten står mitt emellan: förblir osäker.
5. Rubrikraden saknar lodräta linjer, och rubrikens etikett går över
   linjen under: står i den första kolumnen (ADR-0029).
6. Rubrikraden saknar lodräta linjer, och en rad har ett enda tal i en
   cell över två kolumner: delas inte.
7. Som sida 2, men ett tal står med sista siffran över linjen, som
   etiketterna i ett diagram vars rutnät läses som en tabell: delas inte.
8. Bara vågräta linjer och en smal första ruta i rubrikraden, talen i
   linje utan lodrät linje emellan, och etiketter som bryts runt sina
   tal, som i en personaltabell (ADR-0029).
9. En rubrik över två kolumner i en rad utan lodräta linjer (ADR-0029).
10. En etikett som bryts över två rader bredvid ett värde och dess andel,
    `Kostnader för⏎verksamheten`: delas inte (ADR-0030).
"""

from pathlib import Path

from reportlab.pdfgen.canvas import Canvas

HAR = Path(__file__).parent
B, H = 595, 842
X = [60, 210, 290, 370]


def vagrata(c: Canvas, y: list[float]) -> None:
    for yi in y:
        c.line(X[0], yi, X[-1], yi)


def lodrata(c: Canvas, topp: float, botten: float) -> None:
    for xi in X:
        c.line(xi, topp, xi, botten)


def rad(c: Canvas, y: float, celler: tuple) -> None:
    c.drawString(X[0] + 5, y, celler[0])
    for xi, cell in zip(X[2:], celler[1:], strict=True):
        c.drawRightString(xi - 5, y, cell)


def rubrik_utan_linjer(
    c: Canvas, rubrik: tuple = ("Belopp, tkr", "2026", "2027")
) -> None:
    vagrata(c, [780, 760, 740, 720])
    c.line(X[0], 780, X[0], 720)
    c.line(X[-1], 780, X[-1], 720)
    lodrata(c, 760, 720)
    rad(c, 766, rubrik)
    rad(c, 746, ("Intäkter", "4 078", "4 054"))
    rad(c, 726, ("Kostnader", "-1 845", "-2 001"))


def tre_rader_i_rutan(c: Canvas) -> None:
    vagrata(c, [780, 760, 700])
    lodrata(c, 780, 700)
    rad(c, 766, ("Post", "2026", "2027"))
    for i, celler in enumerate(
        [
            ("Intäkter", "4 078", "4 054"),
            ("Kostnader", "-1 845", "-2 001"),
            ("Netto", "2 233", "2 053"),
        ]
    ):
        rad(c, 746 - 16 * i, celler)


def rubrik_och_varde(c: Canvas) -> None:
    vagrata(c, [780, 740, 720])
    lodrata(c, 780, 720)
    rad(c, 766, ("", "Bokslut", "Budget"))
    rad(c, 756, ("", "2025", "2026"))
    rad(c, 745, ("Nämnden", "-1,3", "-1,7"))
    rad(c, 726, ("Kostnader", "-48,6", "-53,8"))


def etikett_mitt_emellan(c: Canvas) -> None:
    vagrata(c, [780, 760, 720])
    lodrata(c, 780, 720)
    rad(c, 766, ("Post", "2026", "2027"))
    rad(c, 746, ("", "4 078", "4 054"))
    rad(c, 738, ("Intäkter", "", ""))
    rad(c, 730, ("", "-1 845", "-2 001"))


def rubrik_over_linjen(c: Canvas) -> None:
    rubrik_utan_linjer(c, ("Belopp i tusentals kronor, netto", "2026", "2027"))


def tal_over_tva_kolumner(c: Canvas) -> None:
    vagrata(c, [780, 760, 740, 720])
    c.line(X[0], 780, X[0], 720)
    c.line(X[-1], 780, X[-1], 720)
    lodrata(c, 760, 740)
    c.line(X[1], 740, X[1], 720)
    rad(c, 766, ("Belopp, tkr", "2026", "2027"))
    rad(c, 746, ("Intäkter", "4 078", "4 054"))
    rad(c, 726, ("Summa ram", "", "8 132"))


def tal_over_linjen(c: Canvas) -> None:
    vagrata(c, [780, 760, 720])
    lodrata(c, 780, 720)
    rad(c, 766, ("Post", "2026", "2027"))
    rad(c, 746, ("Intäkter", "4 078", "4 054"))
    rad(c, 730, ("Kostnader", "", "-2 001"))
    c.drawRightString(X[2] + 4, 730, "-1 845")


def talen_utan_lodrat_linje(c: Canvas) -> None:
    vagrata(c, [780, 760, 730, 700])
    c.line(X[0], 780, X[0], 700)
    c.line(X[-1], 780, X[-1], 700)
    c.line(X[0] + 4, 780, X[0] + 4, 760)
    rad(c, 766, ("Namn", "Bokslut 2024", "Bokslut 2025"))
    for y, (ovre, undre), tal in (
        (742, ("Andel kvinnor", "som har heltid"), ("94,3 %", "96,9 %")),
        (712, ("Andel män som", "har heltid"), ("98,6 %", "99,2 %")),
    ):
        c.drawString(X[0] + 5, y + 6, ovre)
        c.drawString(X[0] + 5, y - 6, undre)
        rad(c, y, ("", *tal))


def rubrik_over_tva_kolumner(c: Canvas) -> None:
    vagrata(c, [780, 735, 715])
    lodrata(c, 735, 715)
    for xi in X[:2] + X[-1:]:
        c.line(xi, 780, xi, 735)
    c.drawString(X[1] + 5, 768, "Andel av volymen")
    rad(c, 756, ("", "Bokslut 2024", "Bokslut 2025"))
    rad(c, 741, ("Förskola", "22,6", "23,7"))
    rad(c, 721, ("Grundskola", "51,0", "50,2"))


def ombruten_etikett(c: Canvas) -> None:
    vagrata(c, [780, 760, 720])
    lodrata(c, 780, 720)
    rad(c, 766, ("Post", "2026", "2027"))
    rad(c, 746, ("Kostnader för", "-1 845", "-2 001"))
    rad(c, 730, ("verksamheten", "12 %", "13 %"))


def skapa() -> None:
    c = Canvas(str(HAR / "delade.pdf"), pagesize=(B, H))
    for sida in (
        rubrik_utan_linjer,
        tre_rader_i_rutan,
        rubrik_och_varde,
        etikett_mitt_emellan,
        rubrik_over_linjen,
        tal_over_tva_kolumner,
        tal_over_linjen,
        talen_utan_lodrat_linje,
        rubrik_over_tva_kolumner,
        ombruten_etikett,
    ):
        sida(c)
        c.showPage()
    c.save()


if __name__ == "__main__":
    skapa()
