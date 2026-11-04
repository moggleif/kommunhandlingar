"""Krav: K39 i docs/02-KRAV.md, ADR-0060. Test: tests/test_navigering.py.

Ett organs sidor: sammanträdena och de sidor över tid som organet har
rader för, i samma ordning för alla organ. Kommunsidans översikt och
flikarna på organets sidor byggs ur samma lista.
"""

from kommunhandlingar.webbplats.mall import Mall, menypost
from kommunhandlingar.webbplats.sparslag import SLAGEN

MAL = "mal-och-direktiv"
SAMMANTRADEN = "sammantraden"
# Sidorna över tid, med id, rubrik och vad som räknas, i flikarnas och
# kolumnernas ordning.
SIDOR = [(MAL, "Mål och direktiv", "mål")] + [(s.id, s.rubrik, s.antal) for s in SLAGEN]


# Antalet mål eller saker på varje sida över tid för organet; noll när
# sidan inte finns för organet.
def overtid(mall: Mall, kommun_id: str, organ: str) -> dict[str, int]:
    malen = [m for m in mall.malen.get(kommun_id, []) if m.organ == organ]
    antal = {MAL: len({m.spar for m in malen})}
    for slag in SLAGEN:
        stegen = mall.spar.get(slag.id, {}).get(kommun_id, [])
        antal[slag.id] = len({s.namn for s in stegen if s.organ == organ})
    return antal


# `aktuell` är den visade flikens id. Adresserna är relativa till den
# visade sidan: organets sida eller, ett steg ner, en sida över tid.
def flikar(mall: Mall, kommun_id: str, organ: str, aktuell: str) -> str:
    upp = "" if aktuell == SAMMANTRADEN else "../"
    antal = overtid(mall, kommun_id, organ)
    poster = [(f"{upp}{organ}.html", SAMMANTRADEN, "Sammanträden")] + [
        (f"{upp}{organ}/{sida}.html", sida, rubrik)
        for sida, rubrik, _ in SIDOR
        if antal[sida]
    ]
    lankar = "".join(
        menypost(adress, rubrik, sida == aktuell) for adress, sida, rubrik in poster
    )
    return f'<nav class="flikar" aria-label="Organets sidor"><ul>{lankar}</ul></nav>'
