---
status: accepted
date: 2026-10-11
decision-makers: projektägaren
consulted: AI-agenten
---

# En tabell med linjer och flera tal i en cell delas efter linjerna i andra rader och efter textraderna

## Context and Problem Statement

Sedan [ADR-0016](0016-tabeller-utan-lodrata-linjer.md) är en tabell med
linjer där en cell rymmer mer än ett tal inte säker. Den blir ingen CSV,
och sidan märks `tabell-osaker`. Det hindrar att två tal sparas som ett,
men tabellerna går förlorade som data
([#60](https://github.com/moggleif/kommunhandlingar/issues/60)).

Räknat med dagens regel har 976 CSV:er i 223 av poolens dokument, skrivna
innan regeln fanns, en sådan cell. Ett stickprov visade tre mönster:

* **En vågrät linje saknas** och flera rader står i samma ruta, som
  `30 %⏎18 %⏎10 %⏎5 %`. Ungefär 60 % av CSV:erna.
* **Lodräta linjer saknas** i en rad, oftast rubrikraden, så att
  `Årets resultat 2020 2021 2022 2023` står i en enda ruta, eller flera
  tal står på samma rad i en ruta. Ungefär 35 %.
* **En rubrik och ett värde i samma ruta**, som `Bokslut 2024⏎-1,3` eller
  `2023⏎117`, vanligt i nämndernas ekonomitabeller.

Resten är spann som `0,20 - 1,90` och textrutor med datum och belopp,
som delegeringslistor.

Hur kan de här tabellerna bli CSV utan att ett enda tal hamnar i fel
cell?

## Decision Drivers

* **Ett fel tal som ser riktigt ut är värre än ett som saknas**
  ([ADR-0005](0005-konvertering-verktyg-ocr-och-kvalitet.md)). Det gäller
  också raden och kolumnen talet står i.
* **Hellre märka än gissa.** Det som inte går ihop förblir osäkert.
* **Ur textlagret och linjerna**, som resten av tabellreglerna, så att
  varje villkor går att pröva mekaniskt.
* **Inga nya beroenden.**

## Considered Options

* A – Dela efter linjerna i andra rader och efter textraderna
* B – Läsa hela tabellen som en tabell utan lodräta linjer
* C – Låta pdfplumber gissa linjerna ur texten
* D – Som i dag: tabellen fälls

## Decision Outcome

Valt: A, eftersom det bygger på det som redan står i PDF:en, linjerna i
tabellens andra rader och textradernas höjd, och fäller tabellen så
fort något inte går ihop. Reglerna står i
[ARKITEKTUR](../03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
I korthet:

* **Kolumnerna** är varje cells kanter i hela tabellen. En rad utan
  lodräta linjer delas efter dem, fält för fält, och ett fält som går
  över en gräns fäller tabellen.
* **Raderna** delas nerifrån: den nedersta textraden blir en egen rad när
  den står på samma höjd i varje ruta som inte är tom. En rubrik ovanför
  ett värde blir då en rubrikrad.
* **En rad med högst ett tal per cell** delas inte, så en rubrik i två
  rader, `Prognos⏎2024`, står kvar i en cell.

Poolens version höjs till 0.7.0. Poolen rättas när den konverteras om
([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

### Consequences

* Bra, eftersom de vanliga ekonomitabellerna blir CSV: i stickprovets
  nio dokument blev 23 av 35 fällda tabeller CSV. Varje ord i tabellen
  står i CSV:n exakt en gång, och summaraderna stämmer där tabellen har
  sådana.
* Bra, eftersom en rubrik och ett värde i samma ruta skiljs åt, i
  stället för att stå i en cell som `Bokslut 2024⏎-1,3`.
* Bra, eftersom inget nytt beroende behövs och regeln är kort.
* Dåligt, eftersom en tabell som helt saknar lodräta linjer mellan två
  tal, som `94,3 % 96,9 %` i en ruta över hela bredden, förblir osäker.
  Där finns ingen linje att låna.
* Dåligt, eftersom en etikett som bryts över två rader runt talen, med
  talen mitt emellan, gör att tabellen inte delas.
* Dåligt, eftersom en etikett som är längre än sin kolumn, eller en
  rubrik som står mitt över två kolumner, i en rad utan lodräta linjer
  fäller tabellen, fast en människa kan läsa den. I stickprovet gällde
  det tre av 35 tabeller.
* Neutralt, eftersom en kolumn kan bli tom i varje rad när två linjer
  bara finns i en del av tabellen.

### Confirmation

Tester mot en PDF i `tests/fixtures/pdf/delade.pdf` med en rubrikrad
utan lodräta linjer, tre rader i en ruta, rubrik och värde i samma
ruta, en etikett mitt emellan två tal och en etikett över en linje, och
enhetstester av raddelningen. Facit (K20) mäts före och efter, och
mätningen på stickprovet står nedan.

## Pros and Cons of the Options

### A – Dela efter linjerna i andra rader och efter textraderna

* Bra, eftersom varje cellgräns är en linje som står i PDF:en eller en
  textrad som står på samma höjd i varje cell.
* Bra, eftersom det täcker alla tre mönstren.
* Dåligt, eftersom det inte hjälper där ingen linje finns att låna.

### B – Läsa hela tabellen som en tabell utan lodräta linjer

* Bra, eftersom reglerna redan finns (ADR-0016).
* Dåligt, eftersom de kräver att varje rad är en etikett följd av tal i
  linje. Rubrikrader och celler med rubrik och värde klarar dem inte,
  och linjerna, som säger mest, används inte.

### C – Låta pdfplumber gissa linjerna ur texten

pdfplumbers strategi `text` drar linjer där texten står i linje.

* Bra, eftersom ingen egen kod behövs.
* Dåligt, eftersom gissade linjer inte går att stämma av, och en
  tusentalsavgränsare kan bli en kolumngräns.

### D – Som i dag

* Bra, eftersom ingenting kan bli fel.
* Dåligt, eftersom några av poolens viktigaste tabeller, nämndernas
  bokslut och budgetar, förblir text.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet (projektägaren)** bad om ett stickprov för att se mönstren,
   en kontroll av att resultatet är rätt, och en fråga om ordningen mot
   facit ([#61](https://github.com/moggleif/kommunhandlingar/issues/61)).
2. **Stickprovet (agenten)** tog tolv dokument ur poolen och hämtade nio
   av dem från källan. En prototyp med kolumnerna ur hela tabellen och
   raderna efter textraderna, där alla celler måste ha samma höjder,
   gjorde 20 av 35 fällda tabeller rätt. Rubrik och värde i samma ruta
   klarade den inte, eftersom rubriken hade fler textrader än etiketten.
3. **Förslaget (agenten)** var att ta med rubrik och värde nu, låta
   tabeller helt utan lodräta linjer vänta till ett eget issue och mäta
   mot facit från #61. Projektägaren valde förslaget.
4. **Delningen nerifrån** ersatte kravet på samma höjder i alla celler:
   bara den nedersta raden behöver stå på samma höjd i varje cell, och
   det som står ovanför prövas igen. Det gav rubrik och värde, och 23 av
   35.
5. **Fälten i en cell som går över flera kolumner** avgränsas som i
   ADR-0016. En löptext har vanliga mellanslag och blir ett fält, som
   går över en gräns och fäller tabellen, i stället för att delas ord för
   ord i kolumnerna. En cell inom en kolumn skrivs i den hel, också när
   texten sticker ut över linjen.

### Mätningen

Stickprovet: tolv slumpvis valda dokument bland de 223, där sidorna med
en sådan CSV prövades; tre av PDF:erna gick inte att hämta hela. Av 35
fällda tabeller blev 23 CSV. Varje ny CSV lästes för hand mot ordens
lägen, och där tabellen har en summarad stämdes den av. De tolv som
förblev osäkra är nio textrutor, som delegeringslistor, ärendelistor
och handlingsplaner, som ska förbli osäkra, och tre där en rubrik står
över en kolumngräns, till exempel ett år mitt över två kolumner.

Facit ([ADR-0025](0025-facit-for-konverteringen.md)): en tabell till
blev rätt, skuggbudgetens, och de osäkra gick från två till en. Inga
andra mått ändrades (`tests/fixtures/facit/matt.csv`, 0.6.0 mot 0.7.0).

Ompröva beslutet när facit (#61) visar fel i delade tabeller, eller när
tabellerna utan lodräta linjer mellan talen får en egen regel.
