---
status: "accepted"
date: 2026-11-21
decision-makers: projektägaren
consulted: AI-agenten
---

# Inskannade bilder märks som bild, bildytor maskas, och vridna sidor vänds

## Context and Problem Statement

Ungefär 2 400 sidor i Kungsbackas pool och 2 000 i Region Hallands är
`ej-konverterad`. Regeln för figurer (K15) prövar inte inskannade sidor,
så en inskannad karta och en oläslig textsida märks lika. Den som vill
läsa det som inte blev text för hand kan inte skilja dem åt. Hur märks
det som inte är text, så att det som återstår är det som verkligen
behöver läsas?

## Decision Drivers

* Det som märks `ej-konverterad` ska vara text som inte gick att läsa.
* Hellre märka än gissa: en tveksam sida ska förbli `ej-konverterad`.
* Inga nya beroenden; Pillow och Tesseract finns redan.
* Kostnaden får bara läggas på sidor som annars inte blir text.

## Considered Options

* Ett rutnät över den renderade sidan, med Tesseracts ord, som hittar
  den största bildytan; maskning, riktning och `bild` på det
* Bara Tesseracts egen layoutanalys (bildblock i TSV:n)
* En bildklassificerare (en tränad modell)
* Ingen ändring: allt som inte blir text granskas för hand

## Decision Outcome

Valt alternativ: rutnätet, eftersom det gick att pröva mot ett facit av
riktiga sidor och skiljer foton och kartor från brus utan nya beroenden.

Sidan renderas i 100 dpi i färg och delas i 48 × 48 rutor. En ruta är
bild när minst 30 % av den är mörk eller minst 30 % färgad, och högst
30 % av den täcks av ord som Tesseract läst med säkerhet minst 50. Den
största sammanhängande ytan av sådana rutor är sidans bildyta. Den
räknas som bild bara när intilliggande rutor liknar varandra (ett foto,
en karta) och inte när de skiljer sig som i brus.

### Consequences

* Bra, eftersom foton, kartor och färgade baksidor slutar räknas som
  oläst text, och dokument med bara sådana sidor blir `full`.
* Bra, eftersom halva bildsidor och vridna sidor ofta blir läsbar text.
* Bra, eftersom omkonverteringen hoppar över dokument som redan är
  `full` och därför inte kan bli bättre.
* Dåligt, eftersom tunna linjeritningar och ljusa kartor ofta inte når
  gränsen för bildyta och förblir `ej-konverterad`.
* Dåligt, eftersom en sida som inte når tröskeln läses upp till tre gånger
  (med bild, utan bild, vänd), vilket tar tid i nattkörningen.

### Confirmation

`tests/test_bildyta.py` prövar rutnätet med små ritade sidor, och
`tests/test_skannad.py` hela vägen med Tesseract: ett foto, en halv
bildsida, en vriden sida, en färgad baksida och brus.

## Pros and Cons of the Options

### Rutnätet

* Bra, eftersom det bara behöver Pillow och Tesseracts TSV.
* Bra, eftersom gränserna kan prövas mot sidor som sorterats för hand.
* Dåligt, eftersom gränserna är handsatta och kan behöva justeras.

### Tesseracts layoutanalys

* Bra, eftersom den redan körs.
* Dåligt, eftersom TSV:n inte säger vilka block som är bilder, bara
  vilka som saknar ord; en dålig textskanning och ett foto ser lika ut.

### En bildklassificerare

* Bra, eftersom den kan känna igen fler sorters bilder.
* Dåligt, eftersom den kräver ett stort nytt beroende och en modell som
  inte går att granska rad för rad.

### Ingen ändring

* Bra, eftersom inget kan märkas fel.
* Dåligt, eftersom den som läser för hand får sex gånger fler sidor än
  de som behöver läsas.

## More Information

Ägaren ville nå så nära helt korrekt inläsning som möjligt och frågade
om det går att se att en sida är en bild eller en karta och inte data,
och märka den så, så att det som återstår är det som ska läsas för hand.
Ägaren påpekade att bildsidor ofta bara är halva, och ville se prov
innan något byggdes.

Provet: 72 sidor ur båda poolerna (olästa och OCR-lästa, med och utan
figur) hämtades och mättes i GitHub Actions, och de 44 olästa sorterades
för hand: 59 % foto, karta, ritning eller grafik, 9 % nästan tomma, 9 %
innehållsförteckningar med prickrader, 7 % vridna, 11 % handskrift,
namnteckningar eller streckkoder och 5 % mycket dåliga skanningar.
Regeln för bildyta hittade 18 av 26 bilder och tog en bild av en
handskriven lapp för ett foto. När bildytan på en halv bildsida målades
vit steg OCR-säkerheten från 70 till 85. De OCR-lästa sidorna var alla
läsbar text.

Testsidornas brus (`tests/fixtures/pdf/sidor.pdf`) täcker hela sidan
precis som ett foto. Det som skiljer är att intilliggande rutor i ett
foto liknar varandra: medelavvikelsen mellan grannrutor delad med
rutornas standardavvikelse var 1,03 för bruset och högst 0,76 för
bilderna i provet. Gränsen är 0,8.

Innehållsförteckningarna togs inte med. Prickraderna får Tesseract att
läsa hela rader som brus eller hoppa över dem. Att måla prickarna vita
utifrån Tesseracts ord höjde säkerheten men tappade halva raderna, och
en sida som tappar rader under tystnad strider mot "tomt är inte noll".
Det, handskriften och de dåliga skanningarna är de sista procenten och
utreds för sig.

Agenten rekommenderade att låta omkonverteringen i Kungsbacka vara på,
så att de gamla dokumenten med en svagare sida läses om efter hand, och
att hoppa över de dokument som redan är `full`, eftersom de bara skulle
ge samma resultat; ägaren instämde.
