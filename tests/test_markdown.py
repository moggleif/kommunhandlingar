"""Krav: K4, ADR-0021. Kod: src/kommunhandlingar/konvertering/markdown.py."""

import unittest

from markdown_it import MarkdownIt

from kommunhandlingar.konvertering import markdown
from kommunhandlingar.konvertering.tabeller import som_markdown
from kommunhandlingar.konvertering.text import stycken

GFM = MarkdownIt("commonmark").enable(["table", "strikethrough"])

RADER = [
    "1. i polisarrest, eller",
    "2026. En viktig del av arbetet",
    "36.",
    "3) tredje",
    "- Information från Valmyndigheten",
    "+ plus",
    "* stjärna",
    "-",
    "- - -",
    "=====",
    "___________________________________",
    "*** fet ***",
    "# Rubrik",
    "#",
    "> Rättigheter redovisas inom detaljplaneområdet.",
    "Brev: Val ValAdm <valadm@val.se>",
    "enligt <förvaltningens> förslag",
    "<!-- inte en kommentar -->",
    "Riskbedo&#776;mning och &amp;",
    "5\\1674701\\74\\701\\:N",
    "slutar med \\",
    "Dagab AB`s verksamhet och ``kod``",
    "ca ~5 och ~~inte struket~~",
    "11 $), för störande buller (11 $",
    "/_ldo_2019/_bilder-til och __fet__ och _kursiv_",
    "DSO årsrapport Kungsbacka_20250205",
    "[länk](https://example.se) och ![bild](a.png)",
    "[1]: https://example.se",
    "---|---",
    "| a | b |",
    ":--|--:",
    "|",
    "a  *  b",
]


def synlig_text(md: str) -> tuple[set[str], str]:
    tokens = GFM.parse(md)
    inline = [c for t in tokens if t.children for c in t.children]
    text = "".join("\n" if c.type == "softbreak" else c.content for c in inline)
    return {t.type for t in tokens + inline} - {"softbreak"}, text


STYCKE = {"paragraph_open", "inline", "paragraph_close", "text"}


class TestRad(unittest.TestCase):
    def test_varje_rad_visas_som_den_star(self):
        for rad in RADER:
            with self.subTest(rad=rad):
                typer, text = synlig_text(markdown.rad(rad))
                self.assertEqual(typer, STYCKE)
                self.assertEqual(text, rad)

    def test_raderna_i_ett_stycke_visas_som_de_star(self):
        stycke = "\n".join(markdown.rad(r) for r in ["Datum", *RADER])
        typer, text = synlig_text(stycke)
        self.assertEqual(typer, STYCKE)
        self.assertEqual(text.split("\n"), ["Datum", *RADER])

    def test_vanlig_text_ror_inte(self):
        rad = "Årets  arbete med 4 078  4 054 kr, fil_2024.pdf (bilaga 3)."
        self.assertEqual(markdown.rad(rad), rad)

    def test_indrag_tas_bort(self):
        self.assertEqual(markdown.rad("    kod?"), "kod?")


class TestTabell(unittest.TestCase):
    def test_cellerna_visas_som_de_star(self):
        celler = ["a|b", "*x*", "<y>", "rad 1\nrad 2", "1.", "\\|", "_z_"]
        tokens = GFM.parse(som_markdown([["Rubrik"] * len(celler), celler]))
        rad = [t for t in tokens if t.type == "inline"][len(celler) :]
        texter = [
            "".join(c.content for c in t.children if c.type == "text") for t in rad
        ]
        typer = {c.type for t in rad for c in t.children} - {"text"}
        self.assertEqual(
            texter, ["a|b", "*x*", "<y>", "rad 1rad 2", "1.", "\\|", "_z_"]
        )
        self.assertEqual(typer, {"html_inline"})


class TestSidansText(unittest.TestCase):
    def test_raderna_escapas_men_inte_den_osakra_tabellen(self):
        sida = "1. Ärende\n  - punkt\n10  20\n30  40\n50  60\n# slut"
        text, osaker = stycken(sida)
        self.assertTrue(osaker)
        self.assertEqual(
            text,
            "1\\. Ärende\n\\- punkt\n\n```osaker-tabell\n10  20\n30  40\n50  60\n```"
            "\n\n\\# slut",
        )


class TestKodstaket(unittest.TestCase):
    def test_staketet_ar_langre_an_blockets_backticks(self):
        self.assertEqual(markdown.kodstaket("1  2\n3  4"), "```")
        self.assertEqual(markdown.kodstaket("1 ``` 2"), "````")
