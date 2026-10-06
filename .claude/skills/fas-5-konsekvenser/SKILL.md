---
name: fas-5-konsekvenser
description: Fas 5 i kommunhandlingar. Använd när implementationen är klar, för att hitta allt ändringen påverkar, rätta det och köra all verifiering innan granskningen.
---

# Fas 5 – Konsekvensgenomgång och verifiering

1. **Konsekvensradie.** För varje fil som skapats eller ändrats: sök efter
   alla filer som refererar till, länkar till, beskriver eller beror på den.
   Läs dem. Ta alltid med `docs/02-KRAV.md`, `docs/03-ARKITEKTUR.md`,
   `docs/decisions/README.md`, README och berörd `docs/kallor/<kommun>.md`.
2. Uppdatera varje fil vars beskrivning nu är fel, ofullständig eller saknas.
3. Kontrollera att varje krav har en namngiven verifiering och att
   hänvisningarna stämmer.
4. Kontrollera att ändringen följer besluten i `docs/decisions/` och
   reglerna i `AGENTS.md`.
5. Kör **all** verifiering som finns (se `docs/01-BIDRA.md`) – gissa inte
   vilken som berörs. Rätta grundorsaken till varje fel.

## Utdata – krävs innan fas 6

1. Varje fil som lästes under genomgången.
2. Vilka filer som uppdaterades och varför.
3. Vilka som lästes men inte behövde ändras – och varför inte.
4. Vilka kommandon som kördes och deras resultat.

Kan listan inte skrivas är genomgången inte klar.

Sedan: starta granskningsagenten (`.claude/agents/granskare.md`) med
grenens namn och issuet. Hittar den något: rätta och gör om fas 5 i sin
helhet.
