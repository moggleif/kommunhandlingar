---
status: "accepted"
date: 2026-11-21
decision-makers: projektägaren
consulted: AI-agenten
---

# Statussidan visar andelen känd inläsning

## Context and Problem Statement

Andelen sidor med känd inläsning (K73,
[ADR-0100](0100-sakra-rader-lases-och-resten-ar-ointressant.md)) fanns
bara som kommando. Statussidan räknar men visar inga andelar
([ADR-0012](0012-webbplatsen-byggs-i-actions-och-publiceras-pa-pages.md)),
eftersom det då inte fanns något att räkna en andel av. För sidorna finns
det nu: alla sidor i poolen.

## Considered Options

* En rad överst och en tabell per organ med sidor per sidkvalitet
* Bara en rad överst
* Inte på webbplatsen

## Decision Outcome

Valt alternativ: "En rad överst och en tabell per organ", eftersom
projektägaren vill se på webbplatsen var de olästa sidorna finns.
Andelen känd inläsning är ett undantag från ADR-0012: den är den enda
andel statussidan visar. Räkningen är densamma som kommandots
(`kand_inlasning.kanda` och `andel`).

### Consequences

* Bra, eftersom andelen byggs om varje gång webbplatsen byggs.
* Dåligt, eftersom statussidan får en tabell till.

### Confirmation

`tests/test_kand_inlasning_sida.py` prövar raden och tabellen.
