#!/usr/bin/env bash
# Sparar det klara på körningens gren: datakontrollerna, bara textfiler
# under data/ och versioner/, en commit och en push (K11, ADR-0088). Varje
# fel stoppar körningen; det som redan pushats står kvar på grenen. Också
# en commit som en tidigare push inte fick iväg pushas, så att ingen del
# försvinner tyst. Inget pushas när ingenting har ändrats sedan utcheckningen.
# Användning: spara.sh <gren> <commit-meddelande>
# Kräver BAS, utcheckningens commit, i miljön.
set -euo pipefail
gren="$1"
python -m kommunhandlingar.datakontroll data
git add -A
if git -c core.quotePath=false diff --cached --name-only | grep -Ev '^(data|versioner)/'; then exit 1; fi
if git diff --cached --numstat | grep '^-'; then exit 1; fi
git diff --cached --quiet || git -c user.name="github-actions[bot]" \
  -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
  commit -q -m "$2"
[ "$(git rev-parse HEAD)" = "$BAS" ] || git push -q origin "HEAD:refs/heads/$gren"
