"""Krav: K1 i docs/02-KRAV.md. Test: tests/test_konfiguration.py."""

import re
from datetime import date, datetime

from kommunhandlingar.fel import Konfigurationsfel

KATALOGNAMN = re.compile(r"[a-z0-9-]+")


def kontrollera_falt(post: dict, tillatna: set[str], var: str) -> None:
    okanda = sorted(set(post) - tillatna)
    if okanda:
        raise Konfigurationsfel(f"{var}: okänt fält {', '.join(okanda)}")


def varde(post: dict, falt: str, slag: type, var: str):
    if falt not in post:
        raise Konfigurationsfel(f"{var}: fältet {falt} saknas")
    return valfritt(post, falt, slag, var)


def valfritt(post: dict, falt: str, slag: type, var: str):
    if falt in post and not ar_av_slag(post[falt], slag):
        raise Konfigurationsfel(f"{var}: {falt} ska vara {slag.__name__}")
    return post.get(falt)


def ar_av_slag(varde, slag: type) -> bool:
    # En tidpunkt är en date för isinstance, men inget datum i kommunfilen.
    return isinstance(varde, slag) and not (
        slag is date and isinstance(varde, datetime)
    )


def textlista(post: dict, falt: str, var: str) -> tuple[str, ...]:
    lista = valfritt(post, falt, list, var) or []
    if not all(isinstance(text, str) for text in lista):
        raise Konfigurationsfel(f"{var}: {falt} ska vara en lista med text")
    return tuple(lista)


def katalognamn(text: str, var: str) -> str:
    if not KATALOGNAMN.fullmatch(text):
        raise Konfigurationsfel(f"{var}: {text!r} är inget katalognamn")
    return text
