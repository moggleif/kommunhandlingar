---
name: fas-1-3-krav-och-design
description: Fas 1–3 i kommunhandlingar. Använd efter bekräftad fas 0 för att skriva krav som Given/When/Then, fatta designbeslut (ADR enligt MADR) och bestämma hur ändringen ska verifieras.
---

# Fas 1–3 – Krav, design och valideringsstrategi

Skapa en gren innan något skrivs. Committa efter varje fas.

## Fas 1 – Krav

- Skriv kraven i `docs/02-KRAV.md` som Given/When/Then: önskat tillstånd,
  inte en beskrivning av kodändringen.
- Konkreta, testbara och begripliga för någon som inte kan koden.
- Varje krav hör till ett GitHub-issue.

## Fas 2 – Design och dokumentation

- Beskriv hur kraven uppfylls i `docs/03-ARKITEKTUR.md`.
- **Ett beslut som är svårt att ändra får en ADR** i `docs/decisions/`,
  enligt reglerna i `docs/decisions/README.md`.
- Hitta varje fil som beskriver eller indexerar den del som ändras – krav,
  arkitektur, ADR-index, `docs/kallor/<kommun>.md`, README – och uppdatera
  dem nu, inte i efterhand.

## Fas 3 – Valideringsstrategi

- Bestäm hur varje krav ska verifieras. Automatiskt i första hand.
- Adaptrar verifieras mot sparade sidor och små riktiga PDF:er i
  `tests/fixtures/`, utan nät.
- Konvertering verifieras mot dokument där facit går att kontrollera för
  hand, inklusive ett inskannat och ett med tabeller.
- Går det inte att automatisera: skriv ner det manuella steget.
