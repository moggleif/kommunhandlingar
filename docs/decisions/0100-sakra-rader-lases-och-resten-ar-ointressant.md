---
status: "accepted"
date: 2026-11-21
decision-makers: projektägaren
consulted: AI-agenten
---

# Säkra rader läses, och en sida utan text att lagra märks `ointressant`

## Context and Problem Statement

Målet är 100 % känd inläsning: varje sida är läst, tom, en bild eller
uttryckligen märkt med varför den inte är läst
([#344](https://github.com/moggleif/kungsbackakommun/issues/344)). Efter
K72 (ADR-0099) står ändå ungefär 2 400 sidor i Kungsbacka och 2 100 i
Region Halland som `ej-konverterad`.

Ett prov på 157 sådana sidor, lästa med K72 i GitHub Actions, lämnade 72
oförändrade. Av dem var 46 kartor, plankartor, ritningar, sektioner och
foton med ljusa linjer, 14 vanliga textsidor där en underskrift, en logga,
en karta, prickrader eller skuggning drog ner medelvärdet, 8 handskrift,
2 omslag och 2 med för liten text. Tesseract läste den tryckta texten
säkert också på de sidorna; det var resten av sidan som drog ner
medelvärdet under 70.

Projektägaren vill inte lagra kartor och ritningar, ser handskrift,
omslag och mikroskopisk text som ointressant, men vill att text i en
plankarta blir sökbar. Hur märks det som inte ska läsas, och hur räddas
texten som går att läsa?

## Decision Drivers

* Varje sida ska ha känd inläsning, och märkningen ska säga varför.
* Det som går att läsa säkert ska vara sökbart.
* Hellre märka än gissa: osäker text skrivs inte.
* Inga nya beroenden, och kostnaden bara på sidor som annars inte blir text.

## Considered Options

* Säkra rader ur Tesseracts egen läsning, också vriden 90° åt båda hållen;
  färre än 30 ord ger den nya sidkvaliteten `ointressant`
* Bara `ointressant`, utan att läsa raderna
* Ingen ny kvalitet: allt som inte blir text blir `bild`
* Läsa allt som inte blir text för hand

## Decision Outcome

Valt alternativ: säkra rader och `ointressant`, eftersom det gör varje
sida i provet känd och räddar texten på textsidorna, kartornas rubriker
och plankartornas bestämmelser. En rad behålls när medelvärdet av dess
ords säkerhet är minst 80 och den har ett ord med minst tre bokstäver;
punktutfyllnad räknas inte in. Gränsen på 30 ord skiljer i provet de
flesta textsidor från kartor och handskrift; plankartor med mycket text
och blanketter med mycket tryckt text kommer över den och får sin
tryckta text, och några innehållsförteckningar hamnar under den.

Säkra rader prövas före `bild` och `tom` från K72, så att en textsida på
grått papper eller med en stor bild får sin text. En sida med för få säkra
rader prövas sedan som förut: en jämn bildyta blir `bild`, en nästan tom
sida `tom`, och allt annat `ointressant`. Det gäller också en skanning som
är för dålig för att läsas säkert: den går inte att skilja från en
ritning eller handskrift utan att en människa läser den, och i provet
fanns ingen sådan sida. Fallerar Tesseract i en vriden läsning blir sidan
`ej-konverterad`, eftersom den då inte är läst.

`ointressant` sätts också för hand i granskningen (K34) när regeln missat.
`bild` står kvar för foton och kartor som K72 känner igen, så att
figurtolkningen hittar dem.

Att bara märka `ointressant` skulle kasta brev med underskrift. Att göra
allt till `bild` skulle kalla handskrift och omslag för bild. Att läsa för
hand kostar mest och gäller sidor som projektägaren inte vill lagra.

### Consequences

* Bra, eftersom en sida bara blir `ej-konverterad` när Tesseract
  fallerar eller sidan är för tung, och resten är kända.
* Bra, eftersom text på sidor med underskrift, logga eller karta, och på
  högkant i plankartor, blir sökbar.
* Bra, eftersom andelen kända sidor går att följa per kommun.
* Dåligt, eftersom en sida som inte når tröskeln läses två gånger till,
  vriden.
* Dåligt, eftersom handskrift aldrig läses, inte heller belopp i en
  handskriven blankett; den som behöver dem läser originalet.
* Dåligt, eftersom en innehållsförteckning med få säkra rader blir
  `ointressant`.
* Dåligt, eftersom en skanning av text som är för dålig för OCR också
  blir `ointressant`, och dokumentet då kan bli `full` och inte
  konverteras om (K72). Den hittas bara genom granskning.
* Dåligt, eftersom en sida som ligger upp och ner och inte når tröskeln
  efter vändningen bara läses rak och vriden 90° åt båda hållen.

### Confirmation

`tests/test_sakra_rader.py`, `tests/test_skannad.py` och
`tests/test_kand_inlasning.py`.
