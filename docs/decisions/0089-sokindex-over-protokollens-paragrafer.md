---
status: accepted
date: 2026-11-19
decision-makers: projektägaren
consulted: AI-agenten
---

# Sökindex över protokollens paragrafer, i Giffås format

## Context and Problem Statement

Projektägaren vill kunna söka på alla projektets sajter från knappen
*Sök* i den gemensamma sajtraden, som Giffå ritar
([Giffås beslut 0018](https://github.com/moggleif/giffa/blob/main/beslut/0018-sok-i-sajtraden.md)).
Sajten är statisk och poolen är stor: Kungsbackas text är omkring 700 MB
i drygt 5 000 dokument. Vad ska webbläsaren söka i?

## Decision Drivers

* Ingen server och inget externt; sökningen sker i webbläsaren.
* En träff ska leda till rätt ställe i ett protokoll.
* Det som hämtas ska gå att hämta på en mobil.

## Considered Options

* Protokollens paragrafer: rubrik, diarienummer, organ och datum
* Paragraferna med beslutstexten
* Hela texten i alla dokument

## Decision Outcome

Valt alternativ: "Protokollens paragrafer", eftersom de redan finns i
`paragrafer.jsonl`, säger vad som beslutats och var, och ger för
Kungsbacka omkring 23 000 poster, 7 MB eller knappt 600 kB komprimerat.
Beslutstexten fördubblar storleken, och hela texten går inte att hämta
till en webbläsare.

### Consequences

* Bra, eftersom ett ärende hittas på sin rubrik eller sitt diarienummer
  i alla organ och år, med länk till protokollets sida.
* Bra, eftersom regionhalland får samma index med nästa kodversion.
* Dåligt, eftersom det som bara står i handlingarna eller i
  beslutstexten inte hittas, och kallelsens punkter syns först när
  protokollet finns.

### Confirmation

`tests/test_sokindex.py` bygger en liten pool och läser `sok.json`.
