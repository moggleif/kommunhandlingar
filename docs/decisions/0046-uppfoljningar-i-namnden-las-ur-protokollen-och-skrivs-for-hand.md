---
status: proposed
date: 2026-10-13
decision-makers: projektägaren
consulted: AI-agenten
---

# Nämndens uppföljningar och dragningar om målen läses ur protokollen av AI-agenten, skrivs i en CSV per kommun och räknas per år på målsidan

## Context and Problem Statement

Målsidan (K26, K27) räknar mål och direktiv per år. Den räknar också de
uppföljningar som målen är lästa ur. Projektägaren vill också veta hur
ofta nämnden följt upp målen
([#149](https://github.com/moggleif/kommunhandlingar/issues/149)). Det
står i protokollen. Där godkänner nämnden årsredovisningen, delårsrapporten
och uppföljningen per april, och "noterar informationen till protokollet"
efter dragningar om måluppföljning, måldagar och budgetarbete. Hur kommer
de talen in på sidan?

## Decision Drivers

* **Varje uppgift bär sin härkomst.** Varje räknad paragraf ska gå att
  hitta i protokollet.
* **Bara det som rör målen.** Protokollen noterar också många dragningar
  om verksamheten. De ska inte räknas (projektägarens val).
* **Tomt är inte noll.** Protokollen saknas för flera år.
* **Ingen kod för säkerhets skull.**

## Considered Options

* A – AI-agenten skriver en CSV per kommun, `uppfoljningar/<kommun>.csv`,
  med en rad per paragraf och protokollets sida som källa
* B – Paragraferna blir rader i målfilen
* C – Kod räknar paragraferna med "noterar informationen" eller "godkänner
  årsredovisning" i protokollen

## Decision Outcome

Valt: A, eftersom det är bara en läsare som kan avgöra om en paragraf rör
målen, och en egen fil håller målfilens regler oförändrade.

* **Filen** har kolumnerna `organ`, `datum`, `paragraf`, `slag`, `rubrik`
  och `kalla`. `slag` är `uppföljning`, för en uppföljning nämnden
  godkänner eller tar emot, eller `dragning`, för information om målen som
  nämnden noterar.
* **Kontrollen** prövar att källan är en sida i mötets protokoll i poolen,
  och att paragrafens rubrik står där.
* **Räkningen** går på mötets år, för tabellens år. Ett år utan protokoll
  med text från organet står som tomt i båda kolumnerna.
* **Sidan** får ingen egen lista över paragraferna, bara två kolumner i
  tabellen över antal per år (projektägarens val).

### Consequences

* Good, eftersom varje tal går att följa till en sida i ett protokoll
  genom filen.
* Good, eftersom målfilen behåller en rad per mål.
* Bad, eftersom filen skrivs för hand när nya protokoll kommer.
* Bad, eftersom urvalet av vad som "rör målen" är agentens bedömning.
* Bad, eftersom ett år med några protokoll räknas, fast andra protokoll
  från året saknas. Talen är alltså ett minsta antal.

### Confirmation

`tests/test_uppfoljningar.py` prövar läsningen, kontrollerna och räkningen
med en påhittad kommun, och att Kungsbackas fil går ihop med poolen.

## Pros and Cons of the Options

### A – En egen CSV per kommun

* Good, eftersom raden har protokollets sida som källa.
* Good, eftersom formatet är detsamma som för kalendern och målen.
* Bad, eftersom det blir en fil till per kommun.

### B – Rader i målfilen

* Good, eftersom allt om målen står i en fil.
* Bad, eftersom en dragning ofta gäller alla mål eller inget namngivet.
  Rubriken, formuleringen och spåret i målfilen passar inte.

### C – Kod räknar i protokollen

* Good, eftersom nya protokoll räknas av sig själva.
* Bad, eftersom "noterar informationen" står i 223 paragrafer i GA:s
  protokoll, och de flesta gäller inte målen.
* Bad, eftersom ordvalet skiftar mellan åren ("lägger … till
  handlingarna", "godkänner uppföljning per april").

## More Information

Agenten gick igenom GA:s protokoll i poolen och fann 17 godkända
uppföljningar och 16 noterade dragningar om målen från 2017 och framåt,
de år tabellen visar. Tre av uppföljningarna justerades direkt i ett
separat protokoll från mötet, som också finns i poolen. Projektägaren svarade
på tre frågor:

* Ingen egen lista på sidan.
* Två kolumner i tabellen per år, med tomt för år utan protokoll.
* Bara det som rör målen, inte uppföljningar av verksamheten som
  kvartalsuppföljningen av arbetsmarknaden.

Rubriken är paragrafens rubrik i protokollet, också när den är ärendets
namn snarare än innehållet. Årsredovisningen 2024 står till exempel under
rubriken "Budget 2024" i protokollet 2025-02-20.
