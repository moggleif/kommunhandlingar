"""Krav: K5 i docs/02-KRAV.md, ADR-0035. Test: tests/test_mellanrader.py.

En rad med bara en etikett mellan raderna i en tabell utan lodräta linjer
är en avsnittsrubrik, som `Skulder`, eller början eller fortsättningen på
en etikett: en etikett som börjar med liten bokstav fogas till raden
ovanför när den ena av dem bara är en etikett, som `Avskrivningar på⏎byggnader`
eller `Antal⏎medarbetare per chef`
(docs/03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer).
"""


def foga(kropp: list[list[str]]) -> list[list[str]]:
    """Fortsättningarna fogade till etiketten ovanför, med cellerna från
    den av de två raderna som har tal."""
    ut: list[list[str]] = []
    for rad in kropp:
        if ut and fogas(ut[-1], rad):
            celler = [a or b for a, b in zip(ut[-1][1:], rad[1:], strict=True)]
            ut[-1] = [f"{ut[-1][0]} {rad[0]}", *celler]
        else:
            ut.append(rad)
    return ut


def fogas(ovre: list[str], rad: list[str]) -> bool:
    """Etiketten börjar med liten bokstav, högst en av raderna har tal, och
    etiketten ovanför är ingen rubrik med kolon, som `Varav:`."""
    liten = rad[0][:1].islower() and not ovre[0].endswith(":")
    return liten and not (any(ovre[1:]) and any(rad[1:]))
