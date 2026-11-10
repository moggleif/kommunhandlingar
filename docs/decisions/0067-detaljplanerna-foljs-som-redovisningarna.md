---
status: proposed
date: 2026-11-10
decision-makers: projektägaren
consulted: AI-agenten
---

# Detaljplanerna följs steg för steg som redovisningarna, med besluten i alla organs protokoll

## Context and Problem Statement

Det mesta på byggnadsnämndens dagordning är detaljplaner och
myndighetsärenden. Projektägaren ville ha en egen sida för
detaljplanerna, eftersom de är viktiga att tycka till om. Tillsynen
(förelägganden, viten och sanktionsavgifter) ska inte med.

En plan går genom flera organ. Kommunstyrelsen ger planbesked eller
beställer planen, nämnden eller arbetsutskottet ger planuppdraget och
nämnden beslutar om samråd och granskning. Nämnden antar planen, eller
godkänner den så att fullmäktige kan anta den. Ett överklagande kan
sedan följa.

Poolen har ungefär 110 planärenden i nämndens protokoll 2024–2026 och
ungefär 130 i arbetsutskottets 2023–2026, och de flesta av utskottets
är förslag till nämnden. Före 2024 har nämndens protokoll ingen
innehållsförteckning, och nämnden saknas helt 2018 och från mars 2022
till 2023. Hur visas planerna utan att sidan blir en lista över
dagordningen?

## Decision Drivers

* **Varje uppgift bär sin härkomst.**
* **Ingen kod för säkerhets skull:** sidorna för spår över tid finns
  redan (ADR-0057–0059, ADR-0065).
* **Sidan drar inga slutsatser.**
* **Inga personuppgifter i onödan:** tillsynen gäller enskilda.

## Considered Options

* A – Ett femte slag av spår över tid, detaljplaner, med ett steg per
  beslut i vilket organs protokoll som helst
* B – Som A, men också arbetsutskottets förslag, informationen och
  avstämningarna
* C – En planförteckning per år, utan steg

## Decision Outcome

Valt: A, eftersom en plan är ett spår över tid med beslut i flera
organ, och sidorna för spår redan visar det med källor.

* **Slaget** `detaljplaner` står i `sparslag.py` med kolumnen
  `detaljplan` och faserna `planbesked`, `uppdrag`, `samrad`,
  `granskning`, `godkannande`, `antagande`, `overklagande` och
  `avslutad`. Två ikoner som slagen delar blir konstanter; ingen annan
  kod ändras.
* **Planen** har ett namn med vad den gäller och fastighetsbeteckningen,
  så att den går att känna igen på lokalbehovssidorna.
* **Ett steg är ett beslut:** nämndens, arbetsutskottets egna
  (planuppdragen), kommunstyrelsens (planbesked och projektbeställningar)
  och fullmäktiges. Utskottets förslag till nämnden står inte med, också
  när nämndens protokoll saknas i poolen.
* **Planbeskeden** står med bara när de blev en plan på sidan. De flesta
  gäller en enskild fastighet som aldrig blir en plan.
* **Första omgången** har planerna med ett steg 2024–2026 och deras
  äldre steg där poolen har dem.

### Consequences

* Good, eftersom en sjätte sida över tid bara är en post i
  `sparslag.py`, en CSV och dokumentationen.
* Good, eftersom en plan som fullmäktige antar visar hela vägen från
  nämnden.
* Neutral, eftersom planer som bara finns före 2024 inte står med än.
* Bad, eftersom ett steg som bara står i arbetsutskottets förslag 2023
  saknas, när nämndens protokoll inte finns i poolen.

### Confirmation

`tests/test_detaljplaner.py` prövar sidan med ett steg i ett annat
organs protokoll, och att Kungsbackas fil går igenom kontrollen mot
poolen. `tests/test_navigering.py` räknar den nya kolumnen i
översikten.

## Pros and Cons of the Options

### A – Spår med besluten

* Good, eftersom ingen kod kopieras och varje steg är ett beslut med
  källa.
* Bad, eftersom äldre planer kräver handarbete plan för plan.

### B – Också förslag och information

* Good, eftersom de saknade nämndprotokollen 2023 täcks.
* Bad, eftersom samma steg står två gånger, och förslag inte är beslut.

### C – Planförteckning

* Good, eftersom den är enkel att läsa.
* Bad, eftersom den kräver en ny sida och inte visar hur planen gick.

## More Information

Projektägaren bad 2026-11-10 om en egen sida för detaljplanerna och
sa att tillsynen inte ska med. I fas 0 föreslog AI-agenten omfattningen
ovan, och projektägaren sa ja till alla fyra frågorna.
