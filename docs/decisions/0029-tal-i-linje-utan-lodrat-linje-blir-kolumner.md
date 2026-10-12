---
status: proposed
date: 2026-10-12
decision-makers: projektägaren
consulted: AI-agenten
---

# Tal i linje utan lodrät linje emellan blir kolumner i en tabell med linjer

## Context and Problem Statement

[ADR-0028](0028-tabeller-med-linjer-delas-efter-linjer-och-textrader.md)
delar en tabell med linjer där en cell rymmer flera tal, efter de lodräta
linjer som finns i tabellens andra rader. Där ingen rad har en linje att
låna förblir tabellen osäker, som personaltabellerna där
`94,3 % 96,9 % 96,9 % 97,1 % 97 %` står i en rad med bara vågräta linjer
och etiketten bryts runt talen. En rubrik som står mitt över två kolumner,
som `Andel av verksamhetsvolym %` över två år, fäller också tabellen.
Hur delas de utan att gissa
([#95](https://github.com/moggleif/kommunhandlingar/issues/95))?

## Decision Drivers

* Data ska vara rätt eller märkt: hellre en osäker tabell än tal i fel
  kolumn.
* Samma krav på tal i linje som för tabellerna utan lodräta linjer
  ([ADR-0016](0016-tabeller-utan-lodrata-linjer.md)), så att reglerna
  liknar varandra.
* Ingen ny väg genom konverteringen: delningen i ADR-0028 får fler
  kolumngränser, och resten av dess regler gäller som förut.

## Considered Options

* A – Kolumngränser efter talen inne i en kolumn mellan två linjer, när
  en textrad har två tal
* B – Läsa raderna som en tabell utan lodräta linjer (ADR-0016)
* C – Som i dag

## Decision Outcome

Valt: A, eftersom talen själva visar var kolumnerna går när de står i
linje rad efter rad, och den vågräta linjen mellan raderna avgör vilken
rad ett tal hör till, så att en etikett som bryts runt sina tal inte
blir tvetydig. Reglerna står i
[ARKITEKTUR](../03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell):

* **Gränser efter talen:** i en kolumn mellan två linjer där en textrad
  har två tal grupperas fälten med siffror efter hur de överlappar på
  bredden. Varje grupp ska ha minst två tal, eller inget (en rubrik över
  en tom kolumn), och högst ett tal per textrad. En gräns läggs mitt i
  varje mellanrum, och före den första gruppen när text står till
  vänster. Talen behöver inte stå med högerkanten i linje, som i
  ADR-0016, eftersom talen i personaltabellerna är centrerade.
* **Etiketterna ska finnas:** tabellens första kolumn med text ska ha en
  etikett utan siffror. En tabell med linjer runt bara talen, där
  etiketterna står utanför, får inga gränser, eftersom raderna då skulle
  bli tal utan etikett.
* **Text över en gräns:** ett fält utan siffror som går över en
  kolumngräns skrivs i den första kolumn det täcker. Ett fält med siffror
  som gör det fäller tabellen som förut.
* **Textraderna i en sammanslagen cell** prövas var för sig: bara tal,
  bara text, eller en rubrik med siffror men utan fält som bara är ett
  tal. En rad som blandar en etikett och ett tal fäller tabellen.
* **En etikett som bryts runt sina tal:** en cell som har textrader både
  ovanför och under talens höjd räknas som att den står på den höjden.

Poolens version höjs till 0.8.0. Poolen rättas när den konverteras om
([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

### Consequences

* Bra, eftersom personaltabellerna och tabellerna med en rubrik över två
  kolumner blir CSV: i stickprovet blev 10 av 33 fällda tabeller CSV,
  mot 2 före. Varje ord i tabellen står i CSV:n exakt en gång.
* Bra, eftersom en etikett som bryts runt sitt tal står i en cell, som
  `Andel kvinnor⏎som har heltid`.
* Dåligt, eftersom en rubrik över två kolumner hamnar i den första av
  dem, som `Andel av volymen⏎Bokslut 2024 | Bokslut 2025`. Ingen linje
  säger att den gäller båda.
* Dåligt, eftersom en etikett med siffror som bryts runt sina tal, som
  `Medarbetare⏎30 - 39 år`, står på en annan höjd än talen och fäller
  tabellen som förut.
* Dåligt, eftersom tal som står tätt, med ett tvetydigt mellanrum, som
  `175 173 183 671`, inte går att skilja från tusental och fäller
  tabellen som förut.
* Neutralt, eftersom en bildtext eller tabellrubrik över hela bredden,
  som `Gjorda konsekvensbedömningar …`, hamnar i den första kolumnen
  tillsammans med den kolumnens rubrik.

### Confirmation

`tests/test_talkolumner.py` prövar gränserna, och `tests/test_delade.py`
och `tests/test_delade_kolumner.py` prövar sidorna 8 och 9 i
`tests/fixtures/pdf/delade.pdf`, texten över en gräns, textraderna i en
sammanslagen cell och etiketten runt sitt tal. Facit
([ADR-0025](0025-facit-for-konverteringen.md)) ska inte bli sämre.

## Pros and Cons of the Options

### A – Kolumngränser efter talen inne i en kolumn

* Bra, eftersom den vågräta linjen avgör raden och talen avgör kolumnen.
* Dåligt, eftersom gränsen läggs mitt i mellanrummet, där ingen linje
  finns.

### B – Läsa raderna som en tabell utan lodräta linjer

* Bra, eftersom regeln redan finns.
* Dåligt, eftersom den kräver att etiketten står på talens rad, och i
  personaltabellerna bryts etiketten runt talen. Rader med en vågrät
  linje emellan blir dessutom egna tabeller med en rad var.

### C – Som i dag

* Bra, eftersom inget ändras.
* Dåligt, eftersom tabellerna förblir osäkra och talen står kvar som text.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet** kom ur granskningen av #60 och bad om samma krav som i
   ADR-0016: högerkanten i linje och minst två tal per kolumn.
   Projektägaren bad att följd-issues görs och mergas.
2. **Stickprovet (AI-agenten)** tog tolv dokument ur poolen med en CSV
   som har flera tal på en rad i en cell, och prövade de 33 fällda
   tabellerna på de sidorna. Personaltabellerna har centrerade tal, så
   kravet på högerkanten byttes mot att talen överlappar på bredden.
3. **Facit** visade att en tabell i årsredovisningen, med linjer bara
   runt talen och etiketterna utanför, blev en CSV med tal utan
   etiketter. Därför krävs en etikett i tabellens första kolumn.
4. **Rubriken över två kolumner** (öppen fråga i issuet) skrivs i den
   första kolumnen, eftersom det är det enklaste som inte gissar vilka
   kolumner den gäller.

### Mätningen

Stickprovet: tolv slumpvis valda dokument bland de 129 vars CSV har flera
tal på en rad i en cell. Av 33 fällda tabeller blev 10 CSV, mot 2 före;
varje ny CSV lästes mot ordens lägen och mot sidbilden. De som förblir
osäkra är främst textrutor, tabeller med etiketter med siffror runt talen
och tal med tvetydiga mellanrum. Stickprovet för #60 gav en tabell till,
22 av 35. Facit oförändrat.

Ompröva beslutet när facit visar tal i fel kolumn i en delad tabell.
