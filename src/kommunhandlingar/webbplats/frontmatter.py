"""Krav: K14 i docs/02-KRAV.md. Test: tests/test_webbplats.py.

Läser front matter så som schemat i docs/03-ARKITEKTUR.md#front-matter
skriver den: ett fält per rad, listor inom hakparenteser.
"""


def las(text: str) -> dict[str, str]:
    huvud = text.split("---\n")[1]
    return dict(rad.split(": ", 1) for rad in huvud.splitlines())


def lista(varde: str) -> list[str]:
    if varde == "null":
        return []
    return [del_ for del_ in varde.strip("[]").split(", ") if del_]
