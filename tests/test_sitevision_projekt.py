"""Krav: K45, ADR-0068. Kod: src/kommunhandlingar/adaptrar/sitevision_projekt.py."""

import unittest
from datetime import date

from kommunhandlingar.adaptrar.sitevision_projekt import upptack
from kommunhandlingar.fel import Hamtfel

LISTA = "https://exempelby.se/bygga/projekt"
# 23.30 i UTC är nästa dag i svensk sommartid.
SENT = "1779406200000"
MORGON = "1740992400000"


def fil(nod: str, tid: str, namn: str) -> str:
    return f'<a href="/download/18.{nod}/{tid}/{namn}">{namn}</a>'


def json_fil(nod: str, tid: str, namn: str) -> str:
    return (
        "<script>AppRegistry.registerInitialState('12.1',{\"files\":[{"
        f'"uri":"/download/18.{nod}/{tid}/{namn}","lastModifiedBy":"255.0"'
        "}]});</script>"
    )


SIDOR = {
    LISTA: '<a href="/bygga/projekt/bostader-i-by">Bostäder</a>'
    '<a href="/bygga/projekt?sida=1">1</a>'
    '<a href="/bygga/projekt?sida=2">2</a><a href="/bygga">Bygga</a>'
    '<a href="/bygga/projekt?sv.target=1&amp;kategori=VA">Filter</a>',
    f"{LISTA}?sida=2": '<a href="/bygga/projekt/va-i-by">VA</a>'
    '<a href="/bygga/projekt?sida=2">2</a>'
    '<a href="/bygga/projekt/bostader-i-by">Bostäder igen</a>'
    '<a href="/bygga/projekt/borta">Borta</a>',
    f"{LISTA}/bostader-i-by": fil("a1", SENT, "Planbeskrivning.pdf")
    + json_fil("a2", MORGON, "Geoteknisk%20utredning%202025.pdf"),
    f"{LISTA}/va-i-by": fil("b1", MORGON, "VA-taxa.pdf")
    + fil("a1", SENT, "Planbeskrivning.pdf"),
}


HAMTADE: list[str] = []


def hamta(adress: str) -> str:
    HAMTADE.append(adress)
    if adress not in SIDOR:
        raise Hamtfel("http-404", adress)
    return SIDOR[adress]


class TestProjektsidorna(unittest.TestCase):
    def setUp(self):
        HAMTADE.clear()
        self.kandidater, self.avvisade = upptack({"bun-projekt": LISTA}, hamta)

    def test_varje_fil_pa_alla_listans_sidor(self):
        self.assertEqual(
            [k.kallnyckel for k in self.kandidater],
            ["sitevision:18.a1", "sitevision:18.a2", "sitevision:18.b1"],
        )

    def test_handlingar_under_organet_med_projektets_namn(self):
        forsta = self.kandidater[0]
        self.assertEqual(
            (forsta.organ, forsta.typ, forsta.namn, forsta.kalla),
            (
                "bun-projekt",
                "handlingar",
                "bostader-i-by-planbeskrivning",
                f"{LISTA}/bostader-i-by",
            ),
        )
        self.assertEqual(
            self.kandidater[1].namn, "bostader-i-by-geoteknisk-utredning-2025"
        )

    def test_datumet_ar_dagen_filen_lades_upp_i_svensk_tid(self):
        self.assertEqual(self.kandidater[0].datum, date(2026, 5, 22))
        self.assertEqual(self.kandidater[1].datum, date(2025, 3, 3))

    def test_en_fil_pa_flera_projekt_blir_det_forstas(self):
        self.assertEqual(self.kandidater[0].kalla, f"{LISTA}/bostader-i-by")

    def test_en_projektsida_som_inte_svarar_star_i_sammanfattningen(self):
        self.assertEqual(len(self.avvisade), 1)
        self.assertEqual(self.avvisade[0].kalla, f"{LISTA}/borta")
        self.assertIn("http-404", self.avvisade[0].orsak)

    def test_en_listsida_som_inte_svarar_star_i_sammanfattningen(self):
        kandidater, avvisade = upptack({"o": "https://exempelby.se/saknas"}, hamta)
        self.assertEqual(kandidater, [])
        self.assertIn(
            "listan: https://exempelby.se/saknas: http-404", avvisade[0].orsak
        )

    def test_en_projektsida_som_inte_gar_att_lasa_hoppas_over(self):
        trasig = "<script>AppRegistry.registerInitialState('12.1',{\"files\":[{"

        def med_trasig(adress: str) -> str:
            return trasig if adress.endswith("/va-i-by") else hamta(adress)

        kandidater, avvisade = upptack({"o": LISTA}, med_trasig)
        self.assertEqual(len(kandidater), 2)
        self.assertEqual(
            [a.kalla for a in avvisade], [f"{LISTA}/va-i-by", f"{LISTA}/borta"]
        )

    def test_listans_forsta_sida_hamtas_en_gang(self):
        self.assertEqual(HAMTADE.count(LISTA), 1)
        self.assertNotIn(f"{LISTA}?sida=1", HAMTADE)

    def test_utan_projekt_hamtas_inget(self):
        self.assertEqual(upptack({}, hamta), ([], []))


PROJEKTET = f"{LISTA}/arena"
UNDER = {
    LISTA: '<a href="/bygga/projekt/arena">Arena</a>',
    PROJEKTET: fil("c1", MORGON, "Program.pdf")
    + '<a href="/bygga/projekt/arena/detaljplan">Detaljplan</a>'
    '<a href="/bygga/projekt/arena/detaljplan#karta">Detaljplan</a>'
    '<a href="/bygga/projekt/arena/borta">Borta</a>'
    '<a href="/bygga/projekt/bostader-i-by">Grannen</a>',
    f"{PROJEKTET}/detaljplan": fil("c2", SENT, "Plankarta.pdf")
    + fil("c1", MORGON, "Program.pdf")
    + '<a href="/bygga/projekt/arena/detaljplan/djupare">Djupare</a>',
}


class TestSidorUnderEttProjekt(unittest.TestCase):
    def setUp(self):
        self.hamtade: list[str] = []

        def under(adress: str) -> str:
            self.hamtade.append(adress)
            return UNDER[adress] if adress in UNDER else hamta(adress)

        self.kandidater, self.avvisade = upptack({"o": LISTA}, under)

    def test_sidan_under_ar_ett_eget_projekt(self):
        self.assertEqual(
            [(k.namn, k.kalla) for k in self.kandidater],
            [
                ("arena-program", PROJEKTET),
                ("detaljplan-plankarta", f"{PROJEKTET}/detaljplan"),
            ],
        )

    def test_en_niva_och_varje_sida_en_gang(self):
        borta = f"{PROJEKTET}/borta"
        self.assertEqual(
            self.hamtade, [LISTA, PROJEKTET, f"{PROJEKTET}/detaljplan", borta]
        )
        self.assertEqual(
            [(a.kalla, a.orsak) for a in self.avvisade],
            [(borta, f"sidan under projektet: {borta}: http-404")],
        )
