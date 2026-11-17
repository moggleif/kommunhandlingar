---
status: accepted
date: 2026-11-17
decision-makers: projektägaren
consulted: AI-agenten
---

# Kanten där två fyllda cellrutor möts är en cellgräns

## Context and Problem Statement

Word ritar en tabells celler som fyllda rutor, en per cell, och strecken
för sig. Har en kolumngräns inget streck möts bara två rutor kant i kant.
En säker tabell räknar bara streck och rutor högst 2 punkter breda som
linjer ([ADR-0005](0005-konvertering-verktyg-ocr-och-kvalitet.md)), så
kolumnerna slås ihop. Texten i dem flätas ihop rad för rad, och sidan
märks ändå `ok`. Saknas strecken helt hittas tabellen inte och blir
löptext med kolumnerna ihopflätade. Så blev målstyrningen i Region
Hallands årsredovisningar för Närsjukvården 2023 och 2024 oläslig, och
riskerna i Kungsbackas internkontrollplaner
([#318](https://github.com/moggleif/kungsbackakommun/issues/318)). Hur
hålls kolumnerna isär utan att färgade rader blir cellgränser igen?

## Decision Drivers

* Data ska vara rätt eller märkt. En tabell med ihopslagna kolumner som
  märks `ok` är det fel som ser riktigt ut.
* Skälet i ADR-0005 står kvar: en färgad rad eller kolumn får inte bli
  en cellgräns.
* Facit ([ADR-0025](0025-facit-for-konverteringen.md)) får inte bli
  sämre.

## Considered Options

* A – Den gemensamma kanten där två fyllda rutor möts är en linje
* B – Alla kanter på fyllda rutor är linjer, som pdfplumbers standard
* C – En lodrät glipa i texten genom hela cellen är en kolumngräns
* D – Som i dag

## Decision Outcome

Valt: A, eftersom den ger tillbaka just den gräns Word ritat, och en
ensam färgad yta inte möter någon annan yta och därför inte ger någon
kant. Två bredare fyllda ytor som möts kant i kant, högst 1 punkt isär
och längs minst 2 punkter, ger en linje längs den gemensamma kanten,
lodrät eller vågrät. Reglerna för en säker tabell gäller sedan som
förut: varje ord ska ha sin mittpunkt i en cell, och ingen cell får
rymma mer än ett tal.

Poolens version höjs till 0.12.0. Poolen rättas när den konverteras om
([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

### Consequences

* Bra, eftersom målstyrningen i Närsjukvårdens årsredovisningar 2023 och
  2024 blir Mål | Uppdrag | Kommentar, och riskerna i
  internkontrollplanerna får sina kolumner.
* Bra, eftersom många tabeller som i dag är löptext blir tabeller, till
  exempel indikatorerna (Indikator | Utfall | Målvärde).
* Dåligt, eftersom en tabell där en kolumn saknar både streck och en
  granne att möta kan gå sönder i stället för att bli fel: rutnätet går
  inte ihop och sidan blir löptext. Det hände i en riskmatris i
  stickprovet, där dagens tabell hade 5 kolumner i stället för 11. Att
  märka en sådan sida står i
  [#319](https://github.com/moggleif/kungsbackakommun/issues/319).
* Dåligt, eftersom en rubrikcell som ritats som två rutor ovanpå
  varandra, som `Tid / Tillskottsbelastning`, blir två rader. Talen står
  rätt.
* Neutralt, eftersom CSV:erna på en sida numreras om när poolen
  konverteras om, som i ADR-0031.

### Confirmation

`tests/test_rutkanter.py` prövar kanterna mellan rutor, och sidorna i
`tests/fixtures/pdf/rutor.pdf` prövar en tabell med cellrutor, en
färgad rad och två rutor som inte möts. Facit ska inte bli sämre.

## Pros and Cons of the Options

### A – Den gemensamma kanten är en linje

* Bra, eftersom en färgad rad, kolumn eller markering som inte möter en
  annan yta inte ger någon kant.
* Bra, eftersom tabellen fortfarande prövas med samma regler som förut.
* Dåligt, eftersom två färgade ytor som ligger kant i kant av andra skäl,
  som två rutor i en figur, ger en kant. Reglerna för en hel tabell
  fångar det när orden inte passar i cellerna.

### B – Alla kanter på fyllda rutor

* Bra, eftersom den hittar flest tabeller.
* Dåligt, eftersom det är precis det ADR-0005 valde bort: tjänsteskrivelsernas
  rosa radbakgrunder gav nio kolumner i stället för tre.

### C – En glipa i texten

* Bra, eftersom den inte behöver något ritat alls.
* Dåligt, eftersom en kort cell, ett indrag eller en ombruten rad ger
  glipor som inte är kolumner, och det är svårt att pröva.

### D – Som i dag

* Bra, eftersom inget ändras.
* Dåligt, eftersom kolumnerna slås ihop och märks `ok`.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Frågan** kom från Region Halland: Närsjukvårdens mål gick bara att
   läsa ut för 2025. Projektägaren bad om en analys av vad som går fel.
2. **Analysen (AI-agenten)** jämförde original-PDF:erna med poolen. 2023
   och 2024 hade tabellen ovan, 2020 en tabell med bara vågräta streck.
   2021, 2022 och 2025 har en rubrik per mål och går att läsa, och
   2017–2018 har ingen bedömning per mål i källan.
3. **Stickprovet.** Regel A prövades på Närsjukvårdens årsredovisningar
   och på 40 slumpvis valda Kungsbackahandlingar 2022–2026. I
   Kungsbacka påverkades 8 dokument: 13 sidor där dagens tabell har
   ihopslagna kolumner rättades, och 31 sidor fick tabeller som i dag är
   löptext. Stickproven stämde mot PDF:en. Facit var oförändrat.
4. **Bara lodräta kanter** prövades också. Det undvek att rubrikcellen
   delades, men förlorade tabeller på 9 sidor i fem handlingar, bland
   dem budget- och volymtabeller, där raderna bara skiljs av rutor. Därför räknas båda riktningarna.
5. **Beslutet.** Projektägaren har som stående regel att arbetet körs
   enligt rekommendationen, och analysen rekommenderade A.

Ompröva beslutet om en tabell där två ytor möts kant i kant ger fel tal.
