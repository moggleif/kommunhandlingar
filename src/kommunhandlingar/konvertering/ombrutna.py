"""Krav: K5 i docs/02-KRAV.md, ADR-0030. Test: tests/test_ombrutna.py.

En etikett som bryts över två rader bredvid två staplade tal, som
`Kostnader för⏎verksamheten` bredvid ett värde och dess andel, ser ut som
två etiketter med var sitt tal. En tabell som delats i rader efter
textraderna, utan lodräta linjer (`olinjerade.py`) eller i en ruta
(`delade.py`), prövas därför på om en etikett fortsätter på nästa rad
(docs/03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer).
"""

import re

# Ett ord som binder till nästa rad, ett avstavningsstreck efter en bokstav
# eller en parentes som inte stängts.
FORTSATTER = re.compile(
    r"(?:(?<!\w)(?:och|eller|samt|för|av|i|till|med|på|om|från|vid|som|inom"
    r"|per|mot|utan|under|över|efter)|[^\W\d_]-|\([^)]*)$",
    re.IGNORECASE,
)


def ombruten(rader: list[list[str]]) -> bool:
    """En etikett i tabellens första kolumn med text som fortsätter på
    nästa rad: den slutar som en ofullständig rad, och nästa etikett börjar
    med liten bokstav."""
    forsta = next(i for i in range(len(rader[0])) if any(r[i] for r in rader))
    etiketter = [r[forsta] for r in rader]
    return any(map(fortsatter, etiketter, etiketter[1:]))


def fortsatter(ovre: str, undre: str) -> bool:
    sista_raden = ovre.split("\n")[-1].rstrip()
    return bool(undre[:1].islower() and FORTSATTER.search(sista_raden))
