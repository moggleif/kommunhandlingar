---
status: proposed
date: 2026-11-13
decision-makers: projektägaren
consulted: AI-agenten
---

# Projekten kopplas till detaljplanerna i en fil skriven för hand, och planens kort visar projektsidan och dokumenten

## Context and Problem Statement

Projektsidornas filer står i poolen som handlingar under organet
`bygg-projekt` (ADR-0068): planbeskrivningar, plankartor,
samrådsredogörelser och utredningar, med projektets namn först i
dokumentets namn. Detaljplanssidan (ADR-0067) följer planerna steg för
steg i protokollen men länkar inte till projektet eller dess dokument
([#261](https://github.com/moggleif/kommunhandlingar/issues/261)).

Kommunens projektsida säger vilken fastighet projektet gäller, och planens
namn på detaljplanssidan har fastighetsbeteckningen. I Kungsbacka gick 45
av de 65 planerna att koppla på fastighetsbeteckningen 2026-11-13, några
till på kvartersnamn eller namn, och ungefär tio planer har inget projekt
kvar på kommunens lista.

Hur ska en plan kopplas till sitt projekt, och vad ska sidan visa?

## Decision Drivers

* **Hellre märka än gissa** (AGENTS.md): en koppling som är en bedömning
  ska synas som det.
* **Fastighetsbeteckningen är nyckeln** för byggnationer: samma
  fastighet är en direkt koppling, inte en tolkning.
* **Ingen ny modell**: projektets dokument finns redan i poolen med
  projektet i namnet.
* **Projektägaren vill inte ha** kommunens status och tidplan för
  projektet på sidan, bara länken och dokumenten.

## Considered Options

* A – En fil skriven för hand, `projekt/<kommun>.csv`, med plan och
  projekt; planens kort får länken och dokumenten
* B – Koppla i bygget på fastighetsbeteckningen ur projektsidan
* C – Ett fält i front matter som säger vilken plan ett dokument hör till

## Decision Outcome

Valt: A, eftersom en koppling är ett påstående som en människa ska kunna
granska rad för rad, som stegen i spårfilerna.

* **Filen** har kolumnerna `organ,detaljplan,projekt,tolkad`. `organ` är
  organet projektens dokument står under, som kommunfilen ger en lista med
  projekt (ADR-0068). `detaljplan` är planens namn som det står i
  `detaljplaner/<kommun>.csv`. `projekt` är projektsidans sista del i
  adressen. `tolkad` är `ja` när kopplingen bygger på namnet och inte på
  fastighetsbeteckningen.
* **Direkt** är en koppling när en fastighet i planens namn, också ett
  kvartersnamn, står under "Fastighet" på projektsidan. Delar två projekt
  fastigheten avgör planens och projektets namn vilket det är, och det är
  fortfarande direkt. Ett planprogram som omfattar planens fastighet är
  `tolkad`.
* **Projektets dokument** är organets dokument vars namn börjar med
  projektet och ett bindestreck. Börjar namnet också med ett längre
  projekt i filen hör det dit.
* **Kortet** för en kopplad plan får en länk "Kommunens projektsida", med
  "tolkad" när kopplingen är tolkad, och en hopfälld lista med projektets
  dokument i poolen: namnet utan projektet och dagen det lades upp.
  Saknas dokumenten står det.
* **Bygget stoppas** med filen och raden när organet saknar en lista med
  projekt, planen står två gånger eller är tom, projektet inte är en del av
  en adress eller `tolkad` är något annat än tomt eller `ja`, och med filen
  när en plan inte finns på detaljplanssidan.

### Consequences

* Good, eftersom varje koppling går att granska, och "tolkad" syns på
  kortet.
* Good, eftersom inget i poolen ändras.
* Bad, eftersom filen skrivs för hand, och ett nytt projekt eller en ny
  plan kopplas först när någon lägger till raden.
* Bad, eftersom ett projekt som är början av ett annat projekts namn (som
  `asa-restaurangstrak` och `asa-restaurangstrak-del-2`) tar det andras
  dokument tills det andra står i filen.
* Neutral, eftersom ett projekt utan dokument i poolen inte stoppar
  bygget: 65 av kommunens projekt har inga filer, och nya dokument kommer
  med nattkörningen.

### Confirmation

`tests/test_projekt.py` läser en påhittad fil med två projekt där det
ena namnet är början av det andra, prövar varje fel som stoppar bygget och
kontrollerar länken och listan på planens kort. Testet för Kungsbacka läser
den riktiga filen mot kommunfilen, poolen och detaljplanerna.

## Pros and Cons of the Options

### A – En fil skriven för hand

* Good, eftersom en bedömning märks och går att rätta på en rad.
* Bad, eftersom någon måste hålla filen i takt med planerna.

### B – Koppla i bygget på fastighetsbeteckningen

* Good, eftersom inget skrivs för hand.
* Bad, eftersom poolen inte har projektsidans fakta, bara filerna, och
  sex planer delar fastighet med två projekt.

### C – Ett fält i front matter

* Bad, eftersom varje projektdokument skulle skrivas om, och kopplingen
  gäller projektet, inte dokumentet.

## More Information

Projektägaren sa 2026-11-13 ja till kopplingsfilen, länken och dokumenten
på detaljplanssidan och till att de äldre planerna (2019–2023) läggs till
på detaljplanssidan därefter, och nej till kommunens status och tidplan.

AI-agenten kopplade 50 av de 65 planerna i Kungsbacka: 43 på fastighet och
7 tolkade. Två planer med fastighet i två projekt lämnades utan koppling:
ett upphävande av en del av en äldre plan och en ändring av en plan för
samma fastighet som ett annat projekt.
