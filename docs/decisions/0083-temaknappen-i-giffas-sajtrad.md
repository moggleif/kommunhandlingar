---
status: accepted
date: 2026-11-16
decision-makers: projektägaren
consulted: AI-agenten
---

# Temaknappen står i Giffås sajtrad, och valet gäller på projektets alla sajter

## Context and Problem Statement

Webbplatsen har ljust och mörkt tema
([ADR-0074](0074-webbplatsen-har-ljust-och-morkt-tema.md)) med en egen
textknapp, "Mörkt tema", och ett eget skript (`webbplats/tema.js`). Sedan
Giffås sajtrad blev en rad på mobilen
([ADR-0082](0082-en-kommuns-grupper-ar-menyns-poster.md)) stod knappen
sist i menyn, bakom knappen *Meny* på mobilen, och tog plats i menyraden
på datorn. Giffå och Kungsbacka i siffror hade inget mörkt tema. Ägaren bad
2026-11-16 om mörkt tema på alla projektets sidor, med en ikon i stället
för text, mitt på i mobilvyn och på en lämplig plats på datorn. Var ska
knappen och skriptet bo?

## Decision Drivers

* En knapp som ser likadan ut och står på samma plats på alla sajterna.
* Valet ska följa med mellan sajterna, som har samma värd.
* Sidan får inte först ritas i fel tema.

## Considered Options

* Knappen och skriptet i Giffås gemensamma meny
* Behålla den egna knappen och byta texten mot en ikon
* Den egna knappen i sajtraden, flyttad dit av poolens eget skript

## Decision Outcome

Valt alternativ: "Knappen och skriptet i Giffås gemensamma meny"
(Giffås beslut 0015), eftersom knappen då står på samma plats på alla
sajterna och valet gäller på alla.

* Varje sida laddar Giffås `/giffa/tema.js` utan `defer` i `<head>`,
  tillsammans med `sajter.css` och `sajter.js` (ADR-0081). Skriptet sätter
  det sparade temat (nyckeln `sajter-tema`) innan sidan ritas.
* `sajter.js` lägger en ikonknapp i sajtraden, och `sajter.css` sätter
  `color-scheme` efter det valda temat.
* Poolens egen knapp, `webbplats/tema.js` och dess regler för
  `data-tema` tas bort. Färgerna står kvar i sidmallen med `light-dark()`
  (ADR-0074).

### Consequences

* Good, eftersom knappen syns direkt på mobilen och valet följer med till
  Giffå, Kungsbacka i siffror och Region Halland.
* Good, eftersom poolen har ett skript mindre.
* Bad, eftersom en sida som visas utan Giffås filer, som en
  förhandsvisning av `_site`, inte har någon knapp; den följer då
  läsarens inställning.
* Bad, eftersom ett val sparat under den gamla nyckeln
  `kommunhandlingar-tema` inte längre gäller; läsaren väljer en gång till.

### Confirmation

`tests/test_tema.py` kontrollerar att sidan laddar Giffås `tema.js` och
inte har någon egen knapp; Giffås `tests/test_sajter.js` prövar knappen.

## Pros and Cons of the Options

### Knappen och skriptet i Giffås gemensamma meny

* Good, eftersom det är en knapp och ett skript för fyra sajter.
* Bad, eftersom knappen saknas när Giffås filer inte nås.

### Behålla den egna knappen och byta texten mot en ikon

* Good, eftersom poolen inte beror på Giffå för temat.
* Bad, eftersom knappen fortfarande står bakom *Meny* på mobilen, och de
  andra sajterna behöver var sin egen.

### Den egna knappen i sajtraden, flyttad dit av poolens eget skript

* Good, eftersom knappen hamnar rätt utan Giffå.
* Bad, eftersom poolens skript då beror på sajtradens inre form, och
  valet inte följer med till de andra sajterna.
