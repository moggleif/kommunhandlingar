"""Krav: K20 i docs/02-KRAV.md, ADR-0025. Test: tests/test_facit.py.

`python -m kommunhandlingar.facit [--spara]` konverterar urvalet och skriver
måtten per dokument, med en not per avvikelse, och totalt; med `--spara`
också raden för poolens version i matt.csv.
"""

import argparse
from collections import Counter
from importlib.metadata import version

from kommunhandlingar.facit.jamfor import MATT
from kommunhandlingar.facit.matt import URVALET, spara, totalt, urvalets_utfall


def rad(namn: str, matt: Counter) -> str:
    return f"{namn:<30}" + " ".join(f"{m}={matt[m]}" for m in MATT)


def main():
    tolkare = argparse.ArgumentParser(prog="python -m kommunhandlingar.facit")
    tolkare.add_argument("--spara", action="store_true", help="skriv raden i matt.csv")
    argument = tolkare.parse_args()
    utfall = urvalets_utfall(URVALET)
    for namn, u in utfall.items():
        print(rad(namn, u.matt))
        for not_ in u.noter:
            print(f"  {not_}")
    print(rad("totalt", totalt(utfall)))
    if argument.spara:
        spara(URVALET / "matt.csv", version("kommunhandlingar"), totalt(utfall))


if __name__ == "__main__":
    main()
