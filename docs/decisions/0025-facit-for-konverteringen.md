---
status: accepted
date: 2026-10-12
decision-makers: projektägaren
consulted: AI-agenten
---

# Konverteringen mäts mot ett facit för utdrag ur riktiga handlingar, och måtten för varje version låses i en fil som testet prövar

## Context and Problem Statement

Poolen ska konverteras om en gång, när konverteringen är bra nog
(ADR-0019, `omkonvertera = false` i kommunfilen). Det finns inget mått på
när den är det. Tal och tabeller ska vara helt rätt eller märkta, men
ingen vet i dag hur ofta de är det i riktiga handlingar, och en ändring
som rättar en sorts tabell kan förstöra en annan utan att något test
märker det
([#61](https://github.com/moggleif/kommunhandlingar/issues/61)).

Vad ska facit vara, var kommer PDF:erna ifrån, vem kontrollerar facit,
och vad mäts?

## Decision Drivers

* **Tal och tabeller ska vara 100 % rätt eller märkta.** Texten väger
  lättare (ADR-0005, punkt 11).
* **Bara text lagras** (ADR-0001). Små testfixturer under 1 MB är
  undantaget.
* **Facit ska stå still.** Kommunen visar bara ett par år bakåt, och en
  fil som tas bort ska inte ta facit med sig.
* **Testerna körs utan nät** (fas 3 i arbetsflödet).
* **Facit ska vara sant, inte bara likt.** Ett facit som skrivs av ur
  konverteringen mäter ingenting.
* **Inga personnamn i repot** (`AGENTS.md`). Utdragen ligger under
  `tests/`, inte under `data/`.
* **Senare issues ska kunna mätas:** tal i celler
  ([#60](https://github.com/moggleif/kommunhandlingar/issues/60)) och
  rättningen av poolens tabeller
  ([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

## Considered Options

* A – Utdrag ur riktiga PDF:er med facit per sida: tabellerna som CSV och
  sidans tal; måtten per version i en fil som testet låser
* B – Som A, men källan hämtas på nytt vid varje körning i stället för
  att utdragen checkas in
* C – Ögonblicksbilder: konverteringens utdata för urvalet sparas, och
  testet visar varje skillnad
* D – Som A, men med facit för hela texten, ord för ord

## Decision Outcome

Valt: A, eftersom det är det enda alternativet där facit både står still,
körs utan nät och är sant oberoende av konverteringen, och det mäter just
tal och tabeller.

* **Urvalet** är åtta dokument och sexton sidor ur tre handlingar från
  kommunstyrelsen och dess arbetsutskott och en från nämnden för teknik:
  årsredovisning, kommunbudget, uppföljningar, en skuggbudget, ett
  kommunalförbunds budget ur Excel, en protokollsparagraf, en
  delårsrapport och en regional remiss. De täcker tabeller med och utan
  linjer, en tabell över två sidor, rubriker och etiketter på flera rader,
  tabeller bredvid löptext i två spalter, minustecken som står för sig och
  en sida som bara är en bild. Utdragen är tillsammans 2,2 MB, var och ett
  under 1 MB.
* **Facit** är per sida: tabellerna som CSV så som de står på sidan, och
  sidans tal i läsordning. En skannad sida har bara sin märkning.
* **Kontrollen.** AI-agenten tar fram talen ur textlagret med två verktyg
  (pdftotext och pdfplumber) och skriver tabellerna ur pdftotext, inte ur
  konverteringen. Varje tabell kontrolleras mot sidbilden, och mot summor
  där tabellen har sådana. Där verktygen är oeniga avgör sidbilden.
  Projektägaren gör stickprov på en tabell per dokument.
* **Måtten** är rätta, ofullständiga, osäkra och saknade tabeller, fel
  rader, påhittade tabeller, avvikande tal och omärkta bildsidor. Hur de
  räknas står i
  [ARKITEKTUR](../03-ARKITEKTUR.md#facit-för-konverteringen).
* **Testet låser måtten.** `matt.csv` har en rad per version av poolen.
  Testet prövar att raden för den installerade versionen stämmer, så att
  varje ändring som flyttar ett mått måste skriva om raden i samma
  ändring, där granskningen ser om det blev bättre eller sämre.
* **Omkonverteringen.** Målet är noll fel rader, noll saknade tabeller,
  noll avvikande tal och noll omärkta bildsidor. När omkonverteringen slås
  på bestämmer projektägaren med måtten som underlag, också hur många
  osäkra och ofullständiga tabeller som är godtagbart. Varje tabell i
  facit går att läsa, så `osakra` är just de tabeller som märkts osäkra i
  onödan. Det räknas per tabell: en sida märkt `tabell-osaker` vars
  CSV:er stämmer räknas inte.

### Consequences

* Bra, eftersom det för första gången finns en siffra för hur ofta tal
  och tabeller blir rätt, och den kan jämföras mellan versioner.
* Bra, eftersom facit redan första gången hittade fel som inga tester
  sett: en tabell med linjer som lästs som en del av sig själv, med tal
  utan etiketter och en sida märkt `ok`; tal i texten som delats av ett
  mellanrum (`4 76,7` för `476,7`); en tabell som saknas utan märkning, och
  rubriker med årtal som hamnat i texten i stället för i CSV:en.
* Dåligt, eftersom 2,2 MB PDF ligger i repot. Det ryms i ADR-0001:s
  undantag men växer med varje dokument som läggs till.
* Dåligt, eftersom facit kan vara fel. Ett fel i facit rättas med en
  ändring som säger varför, och testet att tabellernas tal står bland
  sidans tal fångar skrivfel.
* Dåligt, eftersom ett mått som låses också låser fel. Testet säger bara
  att måtten är kända, inte att de är bra; målet ovan står därför i
  ADR:en och inte i testet.
* Neutralt: urvalet täcker inte allt. Gamla skanningar med tal,
  blanketter och protokoll med omröstningslistor saknas, de senare för att
  de bär personnamn.

### Confirmation

`tests/test_facit.py` prövar reglerna på påhittade sidor, att facit hänger
ihop, att utdragens textlager inte har något som maskas, och att måtten för den
installerade versionen står i `matt.csv`. Den skannade sidan har inget
textlager; AI-agenten har läst den mot sidbilden. Projektägaren gjorde
stickprovet 2026-10-12.

## Pros and Cons of the Options

### A – Utdrag med facit per sida, måtten låsta per version

* Bra, eftersom facit står still och körs utan nät.
* Bra, eftersom facit tas fram oberoende av konverteringen och därför
  mäter om den är rätt, inte om den är oförändrad.
* Bra, eftersom måtten är tal som går att jämföra mellan versioner.
* Dåligt, eftersom PDF:er checkas in, och eftersom facit kostar arbete för
  hand.

### B – Källan hämtas på nytt

* Bra, eftersom inga binärer checkas in.
* Dåligt, eftersom testet kräver nät och att kommunen behåller filen;
  kommunen visar bara ett par år bakåt.
* Dåligt, eftersom en körning tar minuter: handlingarna är upp till
  200 MB, och de valda sidorna är 16 av nära 1 900.

### C – Ögonblicksbilder av utdata

* Bra, eftersom det är billigt: ingen kontroll för hand.
* Dåligt, eftersom det mäter förändring, inte riktighet. Ett fel som
  finns i dag står i ögonblicksbilden som rätt, och en rättning ser ut som
  en avvikelse.

### D – Facit för hela texten

* Bra, eftersom också texten mäts.
* Dåligt, eftersom varje ord måste kontrolleras för hand, och texten inte
  är det som ska vara 100 % rätt.
* Dåligt, eftersom textens radbrytningar och mellanrum ändras med varje
  ändring av uppställningen utan att något blivit fel.

## More Information

Diskussionen i tråden för #61, 2026-10-11:

1. **Fas 0.** AI-agenten föreslog utdrag under 1 MB, kontroll av både
   AI-agenten och projektägaren, noll fel som krav och en gräns för osäkra
   tabeller som projektägaren sätter när siffrorna finns, och en enda pull
   request. Projektägaren svarade "kör", alltså rekommendationerna.
2. **Noll fel gick inte att kräva i CI.** I fas 0 skrev agenten att CI
   skulle hålla fel tal och saknade tabeller på noll hela tiden. När facit
   var klart visade det att dagens konvertering har fel av båda slagen.
   Att kräva noll skulle göra CI rött tills de är rättade, och att sänka
   kravet till dagens nivå vore att kalla fel för rätt. Agenten valde i
   stället att låsa måtten per version och skriva målet i ADR:en. Felen
   blir issues.
3. **Urvalet.** Kungsbackas egen årsredovisning ligger i
   arbetsutskottets handlingar, där många sidor är bilder; sidan med
   balansräkningen som bild är med som den skannade sidan, och
   kommunbudgeten ger resultat-, kassaflödes- och balansräkningen med
   textlager. Riktiga skanningar med tal i poolen är protokoll och
   blanketter med namn, och kallelser och omröstningslistor har namn på
   varje sida, så de är inte med. Ett utdrag som delar typsnitt med resten
   av handlingen blir stort: tre sidor ur apriluppföljningen är 925 kB, och
   en fjärde sida fick inte plats.
4. **Hur en rad jämförs.** Agenten övervägde att jämföra cell för cell,
   men en tabell som brutits i två CSV:er, eller vars rubrik står på två
   rader, skulle då bli fel i sin helhet. Raden blev enheten, med talen på
   exakt plats och etiketten fri att vara avkortad i början eller slutet,
   eftersom en etikett på två rader ofta bara får med den ena. En rad med
   tal men utan etikett räknas som fel: talen går inte att använda. Ett
   minustecken som står för sig i cellen (`- 41,4`) räknas som samma tal.
5. **Hur talen i texten jämförs.** Siffergrupper i stället för hela tal,
   så att jämförelsen inte beror på hur ett tal avgränsas i texten, men så
   att ett tal som delats av ett mellanrum eller slagits ihop med ett annat
   syns. Ett tecken framför ett tal i texten jämförs inte; tecknen i
   tabellerna jämförs med raderna.
6. **Beslutet.** Projektägaren gjorde stickprovet och godkände ADR:en
   2026-10-12.
