---
status: proposed
date: 2026-11-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Redovisningarna följs steg för steg som handlingsplanerna, och direktiv som beställer en redovisning flyttar från målsidan

## Context and Problem Statement

Förskola & Grundskolas målsida fick 46 direktiv 2019–2026, mot 21 för
Gymnasium & Arbetsmarknad. 30 av dem beställer en redovisning av
förvaltningen ("Redovisning av situationen för nyanlända elever",
"Utredning – valfrihet skolmaten"). De har ingen status i
uppföljningarna, bara en kommentar, och de kommer tillbaka till nämnden
som egna paragrafer i protokollet. Till det kommer redovisningar som
återkommer varje år enligt lag eller nämndens årshjul, som
patientsäkerhetsberättelsen och tillsynen av fristående verksamheter.

Projektägaren frågade om redovisningarna ska ha en egen sida, och om det
går att skilja återkoppling på mål och direktiv, rena redovisningar och
informationsärenden. Hur visas det utan att målsidan blir en lista över
beställningar?

## Decision Drivers

* **Hellre märka än gissa:** vad som är en beställd redovisning ska
  avgöras av källans ord, inte av en bedömning.
* **Varje uppgift bär sin härkomst.**
* **Ingen kod för säkerhets skull:** sidorna över tid finns redan
  (ADR-0057–0059).
* **Sidan drar inga slutsatser.**

## Considered Options

* A – Ett fjärde slag av spår över tid, redovisningar, med faserna
  direktiv, redovisad och återkommande; direktiven som beställer en
  redovisning flyttar dit från målfilen
* B – Som A, men direktiven står kvar på målsidan också
* C – Ett nytt slag i målfilen, `redovisningsuppdrag`, som målsidan visar
  för sig
* D – Som A, och dessutom förvaltningens informationsärenden

## Decision Outcome

Valt: A, eftersom en beställd redovisning är ett spår över tid – beställd
i budgeten, redovisad på ett möte – och sidorna för spår redan visar det
med källor, och eftersom målsidan då bara har målen och de direktiv som
är uppdrag att göra något.

* **Slaget** `redovisningar` står i `sparslag.py` med kolumnen
  `redovisning` och faserna `direktiv`, `redovisad` och `aterkommande`.
  Ingen annan kod ändras.
* **Gränsen mot målen** är rubriken i källan: ett direktiv vars rubrik
  börjar med "Redovisning", "Utredning" eller "Information" står i
  `redovisningar/<kommun>.csv` och inte i `mal/<kommun>.csv`.
* **Uppföljningarna av målen** – årsredovisning, delårsrapport, måldag –
  står kvar på målsidan och i `uppfoljningar/<kommun>.csv`.
* **Kopplingen** mellan direktiv och paragraf är `tolkad` när paragrafen
  inte själv säger att den svarar på direktivet och rubrikerna skiljer
  sig.
* **Informationsärendena** står inte med: den stående paragrafen med
  förvaltningens information finns på nästan varje möte, och den säger
  lite om vad nämnden beställt eller följt upp.

### Consequences

* Good, eftersom FG:s målsida går från 46 till 16 direktiv, och varje
  beställd redovisning visar när den kom tillbaka.
* Good, eftersom en femte sida över tid bara är en post i
  `sparslag.py`, en CSV och dokumentationen.
* Neutral, eftersom ett direktiv som beställer något annat än en
  redovisning med andra ord ("Kunskapen om mens och tillgången till
  mensskydd ska vara god") står kvar bland målen, också när det besvaras
  med en redovisning.
* Bad, eftersom gränsen mellan återkommande redovisningar och annat i
  protokollen är AI-agentens läsning. Sidans text säger vilka som står
  med.

### Confirmation

`tests/test_redovisningar.py` prövar sidan med de tre faserna, att
Kungsbackas fil går igenom kontrollen mot poolen och att inget direktiv
i målfilen börjar med orden ovan. `tests/test_navigering.py` räknar den
nya kolumnen i översikten.

## Pros and Cons of the Options

### A – Fjärde slaget, direktiven flyttar

* Good, eftersom ingen kod kopieras och målsidan blir kortare.
* Bad, eftersom samma direktiv inte längre syns bland målen.

### B – Direktiven på båda sidorna

* Good, eftersom målsidan ser ut som förut.
* Bad, eftersom samma direktiv skrivs två gånger, i två filer.

### C – Nytt slag i målfilen

* Good, eftersom direktiven stannar i en fil.
* Bad, eftersom målsidan behöver ny kod för att visa slaget för sig, och
  en redovisning inte har status år för år.

### D – Också informationsärendena

* Good, eftersom allt nämnden får veta står med.
* Bad, eftersom det är hundratals punkter, och de flesta är dagsaktuella
  nyheter utan uppföljning.

## More Information

Projektägaren tyckte 2026-11-07 att FG hade väldigt många direktiv och
föreslog en egen sida för redovisningarna. I fas 0 föreslog AI-agenten
tre sorter, med informationen som en rad per möte. Projektägaren valde
att direktiven flyttar från målsidan, och att informationen inte står
med.
