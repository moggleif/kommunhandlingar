---
status: proposed
date: 2026-10-22
decision-makers: projektägaren
consulted: AI-agenten
---

# Handlingsplanerna följs steg för steg som initiativärendena, med en länk till själva planen

## Context and Problem Statement

Nämnden ger uppdrag om handlingsplaner, antar dem, får dem
återrapporterade och följer upp dem. Kommunens planer kommer till
nämnden på remiss eller som motioner. Stegen står i protokoll,
verksamhetsplaner, delårsrapporter och årsredovisningar, ibland år efter
varandra, och inget dokument samlar dem.

Webbplatsen ska visa varje handlingsplan över tid med en källa för varje
steg, en länk till själva planen när den finns i poolen, och partiet när
planen kommer ur en motion. Initiativärendena har redan en sådan sida
(ADR-0058). Vad räknas som en handlingsplan, och hur byggs sidan utan ny
kod för det som redan finns?

## Decision Drivers

* **Varje uppgift bär sin härkomst.**
* **Sidan drar inga slutsatser** om planerna.
* **Ingen ny kod för det som redan finns** i den gemensamma modellen för
  spår över tid.
* **Inga personnamn i repots texter.**
* **Inget hårdkodat om en kommun.**

## Considered Options

* A – Ett tredje slag i den gemensamma modellen, med en fas för själva
  planen och avsändaren som frivilligt värde i fasen `uppdrag`
* B – Som A, men länken till planen i en egen kolumn
* C – Som A, men med alla planer som nämns i poolen, också den interna
  kontrollplanen
* D – Planerna som mål i målfilen

## Decision Outcome

Valt: A, eftersom läsningen, kontrollen mot poolen, ikonerna,
tidslinjen och korten redan finns, och eftersom länken till planen då är
ett steg med en text som prövas mot källan som alla andra.

* **Vilka planer:** en plan står med när den har ett eget steg i
  organets protokoll eller handlingar. Organets egna planer står med,
  och kommunens planer där organet yttrar sig eller får ett uppdrag.
  Planer som bara nämns, den interna kontrollplanen och planer för
  enskilda elever står inte med.
* **Filen** är `handlingsplaner/<kommun>.csv` med initiativfilens
  kolumner, men `plan` i stället för `arende`. Faserna är `uppdrag`,
  `yttrande`, `plan`, `antagen`, `uppfoljning`, `revidering` och
  `avslutad`.
* **Själva planen** är steget `plan`, med en text ur planen. Kortet
  länkar till den.
* **Avsändaren** är värdet i `uppdrag` när planen kommer ur en motion
  eller ett initiativ, och står tomt annars. Den gemensamma koden räknar
  bara avsändare som finns.
* **Historiken** på korten står under "Läs mer" på alla sidor om spår
  över tid, med källorna.

### Consequences

* Good, eftersom en fjärde sida av samma slag bara är en ny post i
  `sparslag.py`, en CSV och en text i dokumentationen.
* Good, eftersom läsaren kommer till själva planen med ett klick.
* Neutral, eftersom sammanfattningen av historiken byter text också på
  lokalbehovens och initiativärendenas sidor.
* Bad, eftersom "antagen eller framtagen" är en fas för både ett beslut
  i nämnden och en rad i en årsredovisning om att förvaltningen tagit
  fram en plan. Värdet och texten visar vilket.
* Bad, eftersom ett förslag från tre ledamöter i olika partier inte får
  någon avsändare, när källan bara skriver deras namn och partier var för
  sig.

### Confirmation

`tests/test_handlingsplaner.py` prövar en plan utan avsändare, länken
till själva planen, att historiken står under "Läs mer" och att
Kungsbackas fil går igenom kontrollen mot poolen. `tests/test_initiativ.py`
och `tests/test_lokalbehov.py` visar att de andra sidorna fungerar som
förut.

## Pros and Cons of the Options

### A – Tredje slaget, planen som fas

* Good, eftersom ingen kod kopieras och länken prövas mot källan.
* Bad, eftersom planen syns som en ikon i tidslinjen, inte bara på kortet.

### B – Länken i en egen kolumn

* Good, eftersom kolumnen säger vad den är.
* Bad, eftersom kolumnen står tom på nästan alla rader och behöver en
  egen prövning.

### C – Alla planer som nämns

* Good, eftersom inget väljs bort.
* Bad, eftersom ordet står i hundratals sammanhang, de flesta i
  förbifarten, och sidan skulle bli en lista över omnämnanden.

### D – Planerna i målfilen

* Good, eftersom målsidan redan har urval och kort.
* Bad, eftersom en plan inte är ett mål med status år för år.

## More Information

Projektägaren bad om sidan 2026-10-22, "precis som för
initiativärenden", så långt tillbaka som möjligt. I fas 0 föreslog
AI-agenten att också ta med den interna kontrollplanen, en rad per år.
Projektägaren sa nej till internkontrollen, ja till faserna, och bad
dessutom om en länk till själva handlingsplanen och om att källorna
står dolda under "Läs mer". Fasen `yttrande` tillkom när raderna
skrevs, för kommunens planer där nämnden bara yttrar sig.

Poolen saknar GA:s protokoll för 2015–2017 och 2019, det mesta av
2020, andra halvåret 2022 och april–december 2023. Där finns inga steg,
vilket inte betyder att inget hände.

Ett förslag om aktivitetsplanen för rörelse 2017 kom från tre ledamöter
i L, M och C; källan namnger dem var för sig och säger inte Alliansen,
så planen har ingen avsändare.
