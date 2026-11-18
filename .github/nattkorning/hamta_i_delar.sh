#!/usr/bin/env bash
# Steg 2 för en kommunfil i delar om 15 minuter. Efter varje del sparas det
# klara på körningens gren, så att ett avbrott kostar högst en del (K11,
# ADR-0088). Hämtningen avslutar med kod 4 när kandidater väntar inom
# budgeten; varje annan kod än 0 och 4 stoppar körningen.
# Användning: hamta_i_delar.sh <kommunfil> [flaggor till steg 2]
# Kräver START, GREN och DEL i miljön.
set -eo pipefail
kommunfil="$1"
shift
while :; do
  kod=0
  python -m kommunhandlingar.hamta "$kommunfil" "$RUNNER_TEMP/arbete" \
    --start "$START" --del 15 "$@" | tee -a "$RUNNER_TEMP/sammanfattning.txt" || kod=$?
  [ "$kod" -eq 0 ] || [ "$kod" -eq 4 ] || exit "$kod"
  "$(dirname "$0")/spara.sh" "$GREN" "Nattkörning $(date -u +%F), $DEL"
  [ "$kod" -eq 4 ] || exit 0
done
