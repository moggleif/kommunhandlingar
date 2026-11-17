"""Åren som bygget ger exempelbyn med de här raderna och inga andra (K60)."""

from kommunhandlingar.webbplats.arspann import arspann


def aren(rader) -> dict[str, range]:
    return {"exempelby": arspann([r.ar for r in rader])}
