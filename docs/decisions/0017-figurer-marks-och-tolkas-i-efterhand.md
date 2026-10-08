---
status: proposed
date: 2026-10-08
decision-makers: projektägaren
consulted: AI-agenten
---

# Sidor med figurer märks vid konverteringen och tolkas i efterhand av en Claude-session

## Context and Problem Statement

Diagram, kartor, scheman och bilder blir ingen text i dag. Det som står
utskrivet i ett diagram, axlar, teckenförklaringar och tal, hamnar i
sidans text eller i ett kodblock märkt `osaker-tabell`, men utan att
något säger vilket tal som hör till vilken stapel. Ett organisationsschema
eller en karta syns inte alls
([#17](https://github.com/moggleif/kommunhandlingar/issues/17)).

Hur kan poolen säga var figurerna finns, och få ut det de visar, utan
att ett tal som inte står i dokumentet kommer in i den?

## Decision Drivers

* **Ett fel tal som ser riktigt ut är värre än ett som saknas**
  (ADR-0005). Det gäller också tal som en modell läser av en bild.
* **Hellre märka än gissa.** En sida med figur ska gå att hitta, också
  innan den är tolkad.
* **Bara text lagras** (ADR-0001), och nattkörningen ska inte bli
  beroende av en tjänst som kostar per anrop. Claude genom
  abonnemanget går att använda; ett betalt API gör det inte.
* **Enkelt först.** Sessionerna körs för hand till en början; en rutin
  kan komma när arbetssättet har prövats.

## Considered Options

* A – Märk sidorna vid konverteringen, och låt en Claude-session tolka
  dem i efterhand, för hand
* B – Tolka varje figur i nattkörningen med en bildmodell genom ett API
* C – Tolka diagrammen med en öppen modell för diagram, lokalt i
  nattkörningen
* D – Som i dag: figurerna märks inte och tolkas inte

## Decision Outcome

Valt: A, eftersom det är det enda alternativet som varken kostar per
anrop eller lägger in tal som ingen kan stämma av. Märkningen är en
mekanisk regel i konverteringen. Tolkningen görs av en Claude-session
som ser sidan som bild, och datakontrollen prövar att varje tal i en
tolkad tabell står i sidans text.

Reglerna står i [ARKITEKTUR](../03-ARKITEKTUR.md#figurer) och
[Tolkade figurer](../03-ARKITEKTUR.md#tolkade-figurer). I korthet:

* En sida står i `figurer` när en bild täcker 2–90 % av sidan, eller när
  minst 8 ritade objekt ligger utspridda över minst 2 % av sidan: kurvor,
  och rutor som syns och inte har text i sig.
* Arbetslistan är sidorna i `figurer` som inte står i `tolkade`. Ett
  hjälpkommando hämtar originalet, prövar sha256 och renderar sidorna.
* Ett diagram med utskrivna tal blir en tolkad CSV,
  `<sida>-<nr>.tolkad.csv`. Bara tal som står utskrivna tas med, och
  varje sådant tal måste stå i sidans text. Ett schema blir Mermaid, och
  en karta eller ett foto en kort beskrivning. Tolkningen står sist på
  sidan, märkt med modell och datum.
* De 921 dokument som redan finns får `figurer: null` och
  `tolkade: null`: de är inte undersökta. De får värden när de
  konverteras om ([#44](https://github.com/moggleif/kommunhandlingar/issues/44)).

Poolens version höjs till 0.3.0, eftersom front matter får två fält.

### Consequences

* Bra, eftersom en sida med figur går att hitta i front matter, också
  innan den är tolkad.
* Bra, eftersom ett tal i en tolkad CSV står i sidans text före
  tolkningen; det modellen bidrar med är vilken rad och kolumn talet hör
  till. Att den texten är orörd prövas inte mekaniskt, men syns i PR:ens
  diff.
* Bra, eftersom inget nytt beroende behövs och nattkörningen inte ändras
  mer än att den skriver två fält till.
* Dåligt, eftersom regeln tar med många sidor som inte har en figur:
  302 av 1 876 sidor i proven blev märkta, och i ett stickprov på 48 av
  dem hade 14 ingen figur. Det var logotyper som täcker mer än 2 % av
  sidan, namnteckningar och tabeller med färgade eller tomma rutor.
  Varje sådan sida kostar en titt i sessionen.
* Dåligt, eftersom regeln missar ett diagram vars tal står inuti
  staplarna, en liten bild under 2 % av sidan, och varje figur i en
  skanning.
* Dåligt, eftersom tolkningen är ett manuellt steg. Med ungefär var
  sjätte sida märkt blir arbetslistan lång när hela poolen är
  konverterad om.
* Dåligt, eftersom en ny konvertering av ett dokument tar bort dess
  tolkningar. Det händer när originalet har ändrats, och då kan
  figurerna också ha ändrats, men också när bara källnyckeln har bytts
  (K9).
* Dåligt, eftersom ett original som byts ut under samma adress inte
  hämtas igen (ADR-0004); dess sidor står kvar i arbetslistan men går
  inte att rendera förrän dokumentet konverteras om.
* Dåligt, eftersom tal som står med ett enda mellanslag emellan, som en
  axel `0 100 200` eller värden som `90 130`, läses ihop som tusental,
  och då inte går att ta med för sig. Två siffergrupper som kan vara
  ett tal delat över en radbrytning, som `5⏎053`, går inte heller att ta
  med; det gäller 837 av poolens 417 250 tal. Står båda delarna ensamma
  på var sin rad räknas de som två tal, också om de var ett.
* Neutralt, eftersom talen i en tolkad CSV på en sida som lästs med OCR
  stäms av mot OCR-texten, och därför är lika obekräftade som den.
* Neutralt, eftersom ett Mermaid-diagram och en beskrivning inte prövas
  mekaniskt. De är märkta som tolkade.

### Confirmation

* Påhittade sidor prövar regeln: en stor bild, en liten logotyp, en
  skanning, åtta och sju staplar, ett vapen av kurvor på liten yta, vita
  och tunna rutor, rutor med text i och rutor i en säker tabell
  (`tests/test_figurer.py`).
* Ett stapeldiagram i `tests/fixtures/pdf/sidor.pdf` blir `figurer: [17]`.
* Arbetslistan och renderingen prövas mot fixturen, också med ett
  original som har ändrats.
* Datakontrollen prövas med en tolkad CSV vars tal står i sidans text,
  ett tal som bara står i tolkningen, siffror som inte är ett helt tal,
  en etikett som står ordagrant, en sida som inte står i `tolkade`, en
  tolkad sida utan tolkning, med två eller utan modell och datum, en
  sida som står två gånger, `tolkade` utanför `figurer`, en sida i
  `figurer` som inte finns, `figurer` och `tolkade` som inte är `null`
  samtidigt, och en lucka i numren
  (`tests/test_datakontroll_tolkning.py`). Talen i sidans text prövas
  med tal delade över en radbrytning och ett smalt mellanslag, och med
  ett stapeldiagram ur poolen med flera tal per rad. En ny konvertering
  tar bort de tolkade CSV:erna (`tests/test_figurer.py`).

## Pros and Cons of the Options

### A – Märk vid konverteringen, tolka i efterhand för hand

* Bra, eftersom märkningen är mekanisk och prövas med tester.
* Bra, eftersom Claude genom abonnemanget kan se sidan som bild och
  tolka både diagram, scheman och kartor.
* Bra, eftersom datakontrollen hindrar ett tal som inte står i
  dokumentet.
* Dåligt, eftersom det kräver att någon tar en omgång då och då.

### B – Bildmodell genom ett API i nattkörningen

* Bra, eftersom varje figur tolkas utan att någon behöver göra något.
* Dåligt, eftersom det kostar per anrop, vilket projektet inte ska.
* Dåligt, eftersom ingen ser tolkningen innan den når poolen.

### C – Öppen diagrammodell lokalt

* Bra, eftersom den är gratis och körs i nattkörningen.
* Dåligt, eftersom modellerna för diagram läser av staplarnas höjd och
  ger tal som inte står i dokumentet.
* Dåligt, eftersom de bara klarar diagram, inte scheman eller kartor,
  och kräver stora beroenden.

### D – Som i dag

* Bra, eftersom ingenting kan bli fel.
* Dåligt, eftersom det diagrammen visar inte går att använda, och det
  inte går att se vilka sidor som har figurer.

## More Information

1. **Uppdraget.** Projektägaren valde i fas 0 2026-10-08 att #15 och #17
   görs i var sin PR, att ett diagram blir en tolkad tabell som CSV med
   bara de tal som står utskrivna, att sessionerna körs för hand till en
   början, och att omkonverteringen av poolen blir ett eget issue (#44).
   Projektägaren frågade varför en tolkad tabell inte skulle bli CSV;
   agentens första förslag var ett kodblock. Svaret blev att CSV går bra
   när namnet säger att den är tolkad och talen kan stämmas av.
2. **Mätningen.** Regeln kalibrerades på 29 slumpvis valda handlingar
   från nämnderna (1 876 sidor). Sidorna som regeln tog med, och de som
   låg nära gränsen, granskades som miniatyrer. Ett första förslag
   (minst 20 objekt eller bilder över 2 %) tog med kommunvapnet på
   protokollens försättsblad och logotyper, och missade diagram med få
   staplar. Att mäta ytan som objekten sprids över tog bort vapnen och
   logotyperna, och att inte räkna vita rutor tog bort tolv
   tabellsidor. Gränsen 8 objekt i stället för 10 tog med två
   riskmatriser. Resultatet blev 302 sidor i 9 dokument. I ett
   stickprov på 48 av dem var 34 figurer: diagram, kartor,
   detaljplaner, foton och en riskmatris.
3. **Varför talen ska stå i texten.** Ett diagram i en PDF har oftast
   sina tal i textlagret, och de står då redan i sidans text. Agenten
   valde att låta datakontrollen kräva det, så att det modellen tillför
   är strukturen och aldrig ett tal. En tolkning före sidans text räknas
   inte, så att ett tal som bara står i tolkningen inte räknas som
   avstämt. Granskningen (fas 6) visade att kontrollen först bara
   prövade celler som helt var ett tal, och att länkarna till
   tabellerna, klockslag och datum gav tal att stämma av mot. Nu prövas
   varje tal i varje cell, en cell med siffror som inte är ett helt tal
   faller, och varje tolkad sida ska ha precis en tolkning, så att en
   tolkning utan märkning inte räknas som sidans text. Det andra varvet
   visade att en sidkommentar till i tolkningen gjorde ett tal i den till
   sidans text, att text före märkningen räknas som sidans, och att
   etiketter som `65–79 år` aldrig gick att skriva. Nu ska sidorna stå
   en gång var, en etikett med siffror får stå med när den står
   ordagrant i sidans text, och att texten före märkningen är orörd
   lämnas åt granskningen av PR:en, som alla tolkningar går genom.
   Det tredje varvet visade att en ordagrann cell kunde vara en del av
   ett tal, som `5–3` ur `2,5–3,5`, och att `figurer` kunde ha sidor som
   inte finns. Den ordagranna cellen har nu samma gränser som talen, och
   talen tas inte ur ord som `K15` eller ur ett spann som `1 250–1 300`.
   Det fjärde varvet visade samma fel vid tusentalsmellanrummet
   (`250–300` ur `1 250–300`) och vid snedstreck (`23` ur `2022/23`), och
   att tolkningens modell och datum inte prövades. Nu prövas alla tre.
   Det femte varvet visade att ett tal som bryts över två rader i
   löptexten, som `5⏎053`, gav två tal. Ett tal intill en radbrytning
   räknas nu bara när det står ensamt på sin rad, som i ett diagram.
   Det sjätte varvet visade att det fällde över tusen tal i diagram med
   flera tal per rad. Nu gäller regeln bara två grupper som har formen
   av ett delat tusental.
4. **Omprövas** när arbetslistan har prövats några omgångar, om en
   rutin ska ta över, eller om falsklarmen från tabeller kostar för
   mycket.
