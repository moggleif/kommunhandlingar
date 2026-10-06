---
name: fas-7-8-leverera
description: Fas 7–8 i kommunhandlingar. Använd när fas 5 och granskningen är klara, för att presentera arbetet, öppna pull request och driva den till grönt.
---

# Fas 7–8 – Leverera

## Fas 7 – Kontrollpunkt och pull request

1. Kontrollera att utdata från fas 5 och granskningens fynd finns, och att
   inget blockerande fynd är kvar. Sammanfatta båda i PR-texten.
2. Presentera det färdiga arbetet och **vänta på bekräftelse**.
3. Uppdatera grenen mot senaste `main`, kör all verifiering igen.
4. Öppna en PR: kort rubrik i imperativ (under 70 tecken), punktlista med
   vad som ändrats, testplan som checklista, och `Closes #<nr>` när arbetet
   kommer från ett issue.

## Fas 8 – CI och avslut

- Vänta tills alla kontroller är gröna. Faller något: hitta orsaken och
  rätta på grenen.
- Merge görs av en människa om inget annat sagts.
- Efter merge: byt till `main`, hämta och ta bort den lokala grenen.
