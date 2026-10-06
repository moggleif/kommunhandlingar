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
- Följ "Ren kod – strikt" i `AGENTS.md`: gränserna för storlek och
  komplexitet, och ingen kod "för säkerhets skull". Funktioner gör en sak,
  på en abstraktionsnivå.
- Läs din egen diff innan fasen är klar och stryk allt som inte krävs av
  ett krav eller ett test.
- Namn som säger vad saken är i domänen (`sammantrade`, inte `data`).
- Kommentarer förklarar avsikt och begränsningar, inte otydlig kod – gör
  koden tydligare i stället.
- Committa när implementationen är grön.
