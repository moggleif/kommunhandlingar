"""Krav: K33 i docs/02-KRAV.md, ADR-0054. Test: tests/test_avvikelser.py."""

from html import escape

from markdown_it import MarkdownIt

from kommunhandlingar.webbplats.avvikelser import ADRESS, OKANT, ORDNING, Avvikelse
from kommunhandlingar.webbplats.mall import Mall, lank, sida

# Som dokumenten (ADR-0023), men utan bilder: en bild i ett issue skulle bli
# en extern resurs på sidan.
LASARE = MarkdownIt("commonmark", {"html": False}).disable("image")
ETIKETTEN = "/issues?q=label%3Aavvikelse"
BIDRA = "/blob/main/docs/01-BIDRA.md#avvikelser-i-k%C3%A4llan"


def avvikelsesida(mall: Mall, avvikelser: list[Avvikelse]) -> str:
    innehall = inledning(mall.repo) + "".join(
        lageavsnitt(lage, [a for a in avvikelser if a.lage == lage]) for lage in ORDNING
    )
    return sida(mall, ADRESS, "Avvikelser i källan", innehall)


def inledning(repo: str) -> str:
    return (
        "<p>Fel i hur kommunen publicerat sina handlingar, som fel datum eller "
        "en fil under fel möte. Varje avvikelse är ett "
        f'<a href="{escape(repo + ETIKETTEN)}">issue med etiketten avvikelse</a>'
        ", och hur de undersöks och meddelas står i "
        f'<a href="{escape(repo + BIDRA)}">Bidra</a>. Sidan visar de öppna; '
        "personuppgifter i handlingarna står aldrig här.</p>"
    )


def lageavsnitt(lage: str, avvikelser: list[Avvikelse]) -> str:
    if lage == OKANT and not avvikelser:
        return ""
    poster = "".join(post(a) for a in avvikelser) or "<p>Inga.</p>"
    return f"<h2>{escape(lage)} ({len(avvikelser)})</h2>{poster}"


def post(avvikelse: Avvikelse) -> str:
    rubrik = lank(avvikelse.adress, f"#{avvikelse.nummer}")
    return (
        f"<section><h3>{rubrik} {escape(avvikelse.rubrik)}</h3>"
        f"<p>{escape(avvikelse.kommun)}: {escape(avvikelse.mote)}</p>"
        f"{LASARE.render(avvikelse.beskrivning)}</section>"
    )
