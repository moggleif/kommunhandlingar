---
name: fas-4-implementera
description: Fas 4 i kommunhandlingar. Använd när krav, design och valideringsstrategi är klara och koden ska skrivas.
---

# Fas 4 – Implementera

- **Testa först**: skriv det fallerande testet ur kravets Given/When/Then,
  sedan koden. Försvaga eller ta aldrig bort ett befintligt test för att få
  grönt.
- Den minsta sammanhängande lösningen som uppfyller kraven. Ingen
  orelaterad städning.
- Varje ny källfil börjar med en kommentar som länkar till kravet och
  testerna den hör till.
- Kod för en publiceringsplattform läser allt kommunspecifikt ur
  konfigurationen. Ett kommunnamn i koden är en bugg.
- Funktioner: en sak, på en abstraktionsnivå. Helst under 20 rader, över 50
  kräver skäl. Högst tre parametrar och tre nivåers nästling.
- Namn som säger vad saken är i domänen (`sammantrade`, inte `data`).
- Kommentarer förklarar avsikt och begränsningar, inte otydlig kod – gör
  koden tydligare i stället.
- Committa när implementationen är grön.
