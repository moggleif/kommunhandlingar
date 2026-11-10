---
status: proposed
date: 2026-11-10
decision-makers: projektägaren
consulted: AI-agenten
---

# Revisionens granskningar följs steg för steg per granskat organ, med stegen i alla organs dokument

## Context and Problem Statement

Projektägaren frågade om kommunrevisionens handlingar ger något att
visa. Revisionen publicerar bara sina protokoll, och där står oftast
bara att en granskning godkänts eller avrapporterats. Rapporten med
revisorernas bedömning och rekommendationer finns i poolen när den
ligger bland nämndens, kommunstyrelsens eller fullmäktiges handlingar,
oftast som underlag till nämndens svar. En granskning går alltså genom
flera organ: revisionen beslutar projektplanen och godkänner rapporten,
nämnden svarar, revisionen informerar fullmäktige och följer senare upp
granskningen.

Hur visas granskningarna så att de går att följa för den nämnd som
granskats?

## Decision Drivers

* **Varje uppgift bär sin härkomst.**
* **Ingen kod för säkerhets skull:** sidorna för spår över tid finns
  redan (ADR-0057–0059, ADR-0065, ADR-0067).
* **Sidan drar inga slutsatser:** bedömningen är revisorernas, med
  deras ord.
* **Tomt är inte noll:** saknas rapporten står ingen bedömning.

## Considered Options

* A – Ett slag av spår över tid, granskningar, under det granskade
  organet, med ett steg per beslut eller bedömning i vilket organs
  dokument som helst
* B – En sida för revisionen med alla granskningar
* C – Som A, men med antalet rekommendationer som eget steg

## Decision Outcome

Valt: A, eftersom läsaren av en nämnds sidor vill se hur nämnden
granskats och svarat, och sidorna för spår redan visar det med källor.

* **Slaget** `granskningar` med kolumnen `granskning` och faserna
  `projektplan`, `rapport`, `bedomning`, `svar`, `fullmaktige` och
  `uppfoljning`.
* **Bedömningen** är ett av revisorernas ord, som bygget prövar mot en
  lista och mot källans sida.
* **Organet** är det granskade. En granskning av hela kommunen står
  under kommunstyrelsen, och dessutom under varje nämnd som svarar
  själv. Den grundläggande granskningen står under en nämnd när nämnden
  har ett eget steg; information som nämnden bara noterar räknas inte.
* **Inte med:** ansvarsfrihet, revisionens interna ärenden, granskningar
  av bolag, stiftelser och gemensamma nämnder, och revisorernas namn.
* **Filen** `sparslag.py` når den hårda gränsen på 250 rader. Formerna
  flyttar till `sparformer.py` och det nya slaget står i
  `granskningsslag.py`.

### Consequences

* Good, eftersom en sjunde sida över tid bara är ett slag, en CSV och
  dokumentationen.
* Good, eftersom en nämnds svar och revisorernas bedömning står bredvid
  varandra med källor.
* Neutral, eftersom de flesta granskningar saknar bedömning när
  rapporten inte finns i poolen.
* Bad, eftersom slagen nu står i två filer.

### Confirmation

`tests/test_granskningar.py` prövar sidan med en granskning från
revisionens protokoll till nämndens svar, att en bedömning som inte är
revisorernas ord stoppar bygget, och att Kungsbackas fil går igenom
kontrollen mot poolen. `tests/test_navigering.py` räknar den nya
kolumnen i översikten.

## Pros and Cons of the Options

### A – Spår under det granskade organet

* Good, eftersom granskningen står där läsaren letar.
* Bad, eftersom en granskning av flera nämnder står på flera sidor.

### B – En sida för revisionen

* Good, eftersom alla granskningar står samlade.
* Bad, eftersom revisionen inte är ett organ med egna mål eller svar,
  och en nämnds läsare måste leta.

### C – Antalet rekommendationer som steg

* Good, eftersom omfattningen syns.
* Bad, eftersom ett tal prövas dåligt mot källan och handarbetet växer
  utan att läsaren får veta vad rekommendationerna gäller.

## More Information

Projektägaren frågade 2026-11-10 om revisionens och valnämndens
handlingar ger något intressant. I fas 0 föreslog AI-agenten
omfattningen ovan, och projektägaren sa ja till att granskningar av
hela kommunen står under kommunstyrelsen, att den grundläggande
granskningen står per nämnd och att alla nämnder kommer i en PR.
Antalet rekommendationer, som fanns med i fas 0, föll bort när
designen skrevs (alternativ C).
