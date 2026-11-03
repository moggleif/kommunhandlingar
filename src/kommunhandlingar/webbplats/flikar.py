"""Krav: K39 i docs/02-KRAV.md, ADR-0060. Test: tests/test_navigering.py.

Ett organs sidor: sammanträdena och de sidor över tid som organet har
rader för, i samma ordning för alla organ. Kommunsidans översikt och
flikarna på organets sidor byggs ur samma lista.
"""

from kommunhandlingar.webbplats.mall import Mall, menypost
from kommunhandlingar.webbplats.sparslag import SLAGEN

MAL = "mal-och-direktiv"


# Sidans id och rubrik, och antalet mål eller saker; tomt när sidan inte
# finns för organet. Sammanträdena räknas av statussidans räkning.
def overtid(mall: Mall, kommun_id: str, organ: str) -> list[tuple[str, str, int]]:
    malen = [m for m in mall.malen.get(kommun_id, []) if m.organ == organ]
    sidor = [(MAL, "Mål och direktiv", len({m.spar for m in malen}))]
    for slag in SLAGEN:
        stegen = mall.spar.get(slag.id, {}).get(kommun_id, [])
        sakerna = {s.namn for s in stegen if s.organ == organ}
        sidor.append((slag.id, slag.rubrik, len(sakerna)))
    return sidor


# `aktuell` är flikens id: organets id för sammanträdena. Adresserna är
# relativa till organets sida, och `upp` tar dem dit från en sida över tid.
def flikar(mall: Mall, kommun_id: str, organ: str, aktuell: str) -> str:
    upp = "" if aktuell == organ else "../"
    poster = [(f"{upp}{organ}.html", organ, "Sammanträden")] + [
        (f"{upp}{organ}/{sida}.html", sida, rubrik)
        for sida, rubrik, antal in overtid(mall, kommun_id, organ)
        if antal
    ]
    lankar = "".join(
        menypost(adress, rubrik, sida == aktuell) for adress, sida, rubrik in poster
    )
    return f'<nav class="flikar" aria-label="Organets sidor"><ul>{lankar}</ul></nav>'
