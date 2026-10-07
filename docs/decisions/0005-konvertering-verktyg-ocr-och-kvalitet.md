---
status: accepted
date: 2026-10-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Konvertering: pdfplumber och Tesseract, tal bara från textlagret, och kvalitet som den sämsta sidan avgör

## Context and Problem Statement

Varje hämtad PDF blir en `.md` med tabeller som CSV, och PDF:en raderas
(ADR-0001). Konverteringen kan inte göras om utan att filen letas upp igen,
så den måste vara så bra som möjligt första gången – och säga ärligt hur bra
den blev ([#4](https://github.com/moggleif/kommunhandlingar/issues/4)).

Handlingarna är blandat material: protokoll och tjänsteskrivelser i löptext,
budget- och uppföljningstabeller, inskannade blanketter och underskrivna
sidor, och stora sammanslagna handlingar-PDF:er
([källor](../kallor/kungsbacka.md)).

Vilket verktyg läser text och tabeller, vad läser sidor utan textlager, vad
betyder kvalitetsnivåerna och hur avgörs de, och vad står i `pipeline`?

## Decision Drivers

* **Öppen källkod.** Varje beroende ska vara fri programvara med en
  licens som OSI godkänt, och kosta ingenting. Copyleft som GPL och AGPL
  går bra: poolen och koden är publika och gratis.
* **Tabellerna och talen.** Siffrorna i budgetar och uppföljningar är det
  analyserna behöver mest. Ett fel tal som ser riktigt ut är värre än ett
  som saknas. Talen ska kunna användas som data till 100 %; texten är
  inte lika viktig i dag (ägaren 2026-10-07).
* **Rätt före snabbt.** Tid och storlek väger lätt mot att det blir rätt
  (ägaren 2026-10-06), men körningen ska fortfarande gå utan GPU.
* **Hellre märka än gissa.** Kvaliteten ska gå att avgöra mekaniskt och
  stämma med hur användbar texten faktiskt är (K5, K6).
* **Svenska.** Å, ä och ö i textlager och OCR.
* **Enkelhet och drift.** Hellre få och små beroenden; körningen ska
  fungera i CI eller en molnmiljö utan GPU (#5).

## Considered Options

* A – pdfplumber för text och tabeller, Tesseract för OCR
* B – Docling för text, tabeller och OCR
* C – PyMuPDF (pymupdf4llm) med Tesseract
* D – Poppler (`pdftotext -layout`) med OCRmyPDF
* E – Camelot eller Tabula för tabellerna (prövade efter valet)
* F – PaddleOCR för OCR (prövat efter valet)
* G – MinerU och Marker (övervägda, inte prövade)
* H – OCR med RapidOCR och Tesseract, där PaddleOCR avgör när de läser
  talen olika (prövat efter valet, sparat till när tal ur skanningar
  behövs)

## Decision Outcome

Valt alternativ: **A – pdfplumber för text och tabeller, Tesseract för
OCR**, rekommenderat av agenten efter jämförelsen nedan och valt av ägaren
2026-10-06. **Skannade sidor ger bara text, aldrig data:** OCR läser dem
för sammanhangets skull, och talen på dem räknas aldrig som bekräftade.
Det valde ägaren 2026-10-07, på agentens rekommendation, i stället för H.
Tabeller utan lodräta linjer får ett eget, kontrollerat steg i
[#15](https://github.com/moggleif/kommunhandlingar/issues/15).

För OCR avgjorde att ingen motor läste alla tal rätt: Tesseract läste 14
av 117 tal fel på skannade protokoll, på sidor där säkerheten ändå var
hög. H visade att felen går att hitta och märka, men det kostar tre
motorer, och datat som analyserna behöver finns i de digitala
handlingarna. Det som är skannat är mest bilagor – inlämnade motioner,
gamla protokoll, underskriftssidor – och de behövs som sammanhang. H
står kvar som vägen när tal ur skanningar behövs.

Det som avgjorde var att A:s tabeller kan kallas säkra eller osäkra
mekaniskt, så att en CSV bara skrivs när talen sitter i ritade celler.
B:s modell gav ett fel tal som inte gick att skilja från de rätta. C
läste budgettabellerna nästan lika bra som B och utan fel i de första
proven, men lika omärkt: ingenting skiljer en rätt tabell från en fel.
Det bredare provet bekräftade det: i 1 090 tabellrader ur fyra hela
dokument gav B 26 och C 8 rader med fel tal, och A och Camelot med linjer
inga. D ger inga celler alls. A läste också hela den sammanslagna
handlingar-PDF:en på 228 sidor på under två minuter utan GPU, med
beroenden på några tiotal MB i stället för 6 GB.

Avgjort av ägaren 2026-10-07, efter det bredare provet:

* **Text och tal märks var för sig.** Sidor vars tal inte är bekräftade
  listas, så att data bara används från sidor där varje tal är
  bekräftat. Textens kvalitet märks som förut.
* **Skannade sidor ger bara text.** De läses med en motor för
  sammanhangets skull, och deras tal räknas aldrig som bekräftade. Att
  hoppa över dem helt valdes bort: PDF:en raderas efter konverteringen,
  och kommunens webbplats visar bara ett par år bakåt, så det som hoppas
  över kan vara borta när det behövs.

Avgjort av ägaren 2026-10-06, före jämförelsen:

* **AGPL utesluts.** Det ändrades efter jämförelsen (se nedan): öppen
  källkod räcker, så C och D var aldrig uteslutna av licensen.
* **Kvalitet per sida, och den sämsta sidan avgör dokumentet.**
* **`pipeline`** bär poolens version ur `pyproject.toml` och verktygen
  som läste dokumentet, med version.

Avgjort efter jämförelsen. Reglerna och trösklarna i exakt form står
bara i [ARKITEKTUR](../03-ARKITEKTUR.md#konvertering-och-kvalitet); här
står varför.

* **Ett läsbart textlager behålls, hur kort det än är,** om sidan inte är
  en skanning, så att en kort sista sida med kommunens logga inte läses
  om med OCR.
* **En skanning har färre än 50 synliga tecken.** Gränsen är uppmätt:
  skannade sidor hade 0 synliga tecken, medan den kortaste riktiga
  textsidan hade 72 (en underskriftssida) och budgetens omslag, ett
  helsidesfoto med text, 126. Gränsen släpper också igenom en stämpel
  eller ett diarienummer på en skanning.
* **En sida helt utan tecken men med grafik läses med OCR**, så att text
  som gjorts om till kurvor inte försvinner tyst. Blir OCR:n tom är sidan
  `ej-konverterad`, eftersom en karta eller ett foto inte är tomt. `tom`
  avgörs i stället på den renderade sidan: nästan bara vita pixlar.
  Gränsen 0,5 % är satt, inte uppmätt.
* **Gränsen för oläsliga tecken, 1 %,** är satt, inte uppmätt: inga
  oläsliga tecken förekom alls i proven. Ett riktigt textlager har inga.
* **En skanning med ett tidigare OCR-lager läses med vår OCR.** Den känns
  igen på att bilderna täcker sidan och texten är osynlig, som i ett
  OCR-lager; osynlig text räknas inte som synliga tecken. Ett tidigare
  OCR-lager i synlig text känns inte igen; i proven var alla osynliga.
  Gränsen 90 % täckning är satt; i proven täckte skanningarna
  hela sidan.
* **OCR-säkerheten 70** ligger i glappet mellan 67 och 75 i
  kalibreringen. Hur den beter sig på verkliga skanningar nära tröskeln är
  oprövat: den sämsta riktiga skanningen låg på 71. Den avgör bara om
  sidan har läsbar text alls, inte om talen stämmer: Tesseracts säkerhet
  var 78–95 på sidor där den läste tal fel.
* **Tesseract läser texten, inte RapidOCR,** fast RapidOCR läste talen
  bättre. Orden läste de lika bra (95,3 och 94,7 %), talen används ändå
  inte, och Tesseracts säkerhet är kalibrerad medan RapidOCR:s låg på
  96–100 hur dålig bilden än var. Tesseract är också ett litet
  systempaket.
* **Varje sida som lästs med OCR har obekräftade tal,** liksom varje
  sida som är `ej-konverterad`, eftersom tal som inte lästs inte kan vara
  bekräftade, och varje sida med textlager där något tecken är oläsligt,
  eftersom tecknet kan ha varit en siffra.
* **Ritade linjer är streck och smala rektanglar; bredare fyllda ytor är
  inga linjer.** Annars tas färgade rader och kolumner för cellgränser.
* **En osäker tabell blir ingen CSV.** Den står i Markdown märkt som osäker,
  med radernas uppställning, där talen står rätt.
* **En sida som lästs med OCR får inga CSV:er**, eftersom OCR:ns säkerhet
  inte fångar tal som saknas.

### Consequences

* Bra, eftersom kvaliteten i varje fil går att lita på: den mäts, den
  gissas inte.
* Bra, eftersom ingen CSV i proven fick ett tal i fel cell.
* Dåligt, eftersom budgettabeller utan lodräta linjer, som Kungsbackas,
  inte blir CSV alls. Talen finns rätt i texten, men den som vill
  analysera dem får läsa dem därifrån tills tabellerna kan läsas säkert
  på annat sätt (se När beslutet bör omprövas).
* Dåligt, eftersom en enda inskannad sida gör ett annars rent dokument
  till `ocr`. `kvalitet_per_sida` visar då att resten är `ok`.
* Bra, eftersom ett tal som går att använda som data kommer ur ett
  textlager, och varje sida där det inte gör det är listad.
* Bra, eftersom OCR bara kräver Tesseract, och skannade sidor läses på
  ett par sekunder.
* Dåligt, eftersom tal i skanningar, som beloppen på blanketterna för
  partistöd, inte går att använda som data. Behövs de, är H vägen; då
  måste de dokument som redan konverterats hämtas igen, och det går bara
  så länge de finns kvar hos kommunen.
* Dåligt, eftersom en sammanslagen handlingar-PDF med en enda skannad
  bilaga inte har en tom `tal_obekraftade`. Talen på de andra sidorna går
  ändå att använda, eftersom listan anger sidorna.
* Dåligt, eftersom ett tidigare OCR-lager i synlig text inte känns igen.
  Det läses som textlager, och dess tal räknas som bekräftade fast de är
  någon annans OCR. I proven var alla tidigare OCR-lager osynliga.

### Confirmation

* Testfixturer under `tests/fixtures/` med facit som går att kontrollera
  för hand: en sida med textlager, en kort sida utan bilder, en inskannad
  sida, en tom inskannad baksida, en skanning med osynligt OCR-lager, ett
  omslag med helsidesbild och kort synlig text, en kort sida med logotyp,
  en sida med text omgjord till kurvor, en inskannad karta, en inramad
  textruta, en tabell med linjer, en tabell med färgade rader, en tabell
  utan lodräta linjer, en sida med löptext, datum och
  diarienummer som inte får märkas `tabell-osaker`, en lösenordsskyddad
  och en trasig fil. Testerna kontrollerar både texten och den kvalitet
  varje sida får, och vilka sidor som står i `tal_obekraftade`.
* CI kontrollerar att `kvalitet` stämmer med `kvalitet_per_sida` enligt
  tabellen i ARKITEKTUR, och att varje sida som är `ocr` eller
  `ej-konverterad` står i `tal_obekraftade`, i varje `.md` under `data/`.

## Pros and Cons of the Options

### A – pdfplumber för text och tabeller, Tesseract för OCR

pdfplumber (MIT, på pdfminer.six) ger varje ord med koordinater och varje
ritad linje. Tabellerna läses med linjerna som cellgränser, som i
`moggleif/politik` (`scripts/pdftabell.py`). Sidor som ska läsas med OCR
renderas med pypdfium2 (Apache-2.0/BSD) och läses av Tesseract
(Apache-2.0) med svensk modell.

* Bra, eftersom alla licenser är tillåtande (MIT, Apache-2.0, BSD).
* Bra, eftersom alla 85 rader i tjänsteskrivelsernas linjerade tabeller
  blev rätt, och ingen tabell blev fel utan att märkas.
* Bra, eftersom "säker tabell" får en mekanisk definition.
* Bra, eftersom det är snabbt: 228 sidor på 113 sekunder, varav de flesta
  för de 31 skannade sidorna.
* Neutralt, eftersom Tesseract är ett systempaket, inte ett Python-paket.
* Dåligt, eftersom tabeller utan lodräta linjer inte blir CSV.
* Dåligt, eftersom Tesseract missar tal i rutor och handskrift på
  blanketter.
* Dåligt, eftersom Tesseract läste 14 av 117 tal fel på skannade protokoll
  ("80%" blev "803", "§ 83" blev "883"), på sidor med hög säkerhet. Därför
  räknas tal på skannade sidor aldrig som bekräftade.

### B – Docling för text, tabeller och OCR

Docling (MIT) analyserar sidans layout med maskininlärda modeller, ger
läsordning och tabellstruktur och kör OCR (som standard RapidOCR).

* Bra, eftersom tabeller utan linjer blir tabeller: 115 av budgetprovets
  rader blev exakt rätt.
* Bra, eftersom OCR:en hittade alla femton kontrollerade värden på den
  inskannade blanketten.
* Dåligt, eftersom en rad i budgetprovet fick tal flyttade mellan rader
  (40 676 blev 40 och 676) utan att något i utdata visar det. I det
  bredare provet gav B 26 sådana rader, oftast rader ur två
  tabeller bredvid varandra som lagts ihop. En modells tabell går inte
  att kalla säker mekaniskt.
* Dåligt, eftersom standard-OCR:en inte kan svenska: "Kronor" blev
  "Kranor" och "från föregående" blev "frán füreglende".
* Dåligt, eftersom det kräver PyTorch och modeller från Hugging Face:
  6,4 GB installerat och 0,5 GB modeller, och 5,8 GB minne under körning.
* Dåligt, eftersom det är långsamt utan GPU: 228 sidor tog 849 sekunder,
  ungefär 3,7 sekunder per sida.

### C – PyMuPDF (pymupdf4llm) med Tesseract

* Bra, eftersom det är snabbt och ger bra Markdown direkt; tabellerna
  blev nästan lika bra som i B (113 rader rätt, inga fel tal).
* Neutralt, eftersom licensen är AGPL-3.0, som är öppen källkod.
* Dåligt, eftersom tabellerna hittas med en heuristik som inte säger när
  den är osäker; samma invändning som mot B. C gjorde inga fel i de första
  proven men 8 i det bredare.
* Dåligt, eftersom OCR:en körde utan svensk modell ("Kvarstàende").

### D – Poppler (`pdftotext -layout`) med OCRmyPDF

* Bra, eftersom `pdftotext` är snabbast (en sekund för 228 sidor) och
  behåller radernas uppställning.
* Bra, eftersom OCRmyPDF:s förberedelse av bilden gav bäst Tesseract-läsning
  av blanketten (14 av 15).
* Dåligt, eftersom tabeller bara blir text i spalter, utan celler.
* Neutralt, eftersom OCRmyPDF (MPL-2.0) kräver Ghostscript (AGPL) och
  Poppler är GPL; båda är öppen källkod.

### E – Camelot eller Tabula för tabellerna

Camelot (MIT) och Tabula (MIT, Java) läser bara tabeller, antingen efter
ritade linjer (`lattice`) eller efter mellanrum (`stream`).

* Bra, eftersom Camelot med linjer läste alla 85 rader i
  tjänsteskrivelserna exakt som A. Det bekräftar A:s regel med ett annat
  verktyg.
* Bra, eftersom Camelot efter mellanrum fick 104 av budgetens 135 rader
  rätt utan något fel tal, och 959 av 1 090 i det bredare provet. Det är
  en kandidat för det kontrollerade steget i #15.
* Dåligt, eftersom Camelot efter mellanrum i det bredare provet lade en
  fotnotssiffra eller ett sidnummer till som sista tal i 8 rader. Steget i
  #15 måste alltså stämma av talen mot textlagret.
* Dåligt, eftersom samma läge efter mellanrum förstörde
  tjänsteskrivelsernas linjerade tabeller (11 av 236 rader som A), så det
  går inte att använda utan att veta vilken sorts tabell det är.
* Dåligt, eftersom Tabula med linjer delade tjänsteskrivelsernas tabeller
  i 97 bitar längs de färgade raderna – samma fel som pdfplumbers
  standardinställning – och Tabula efter mellanrum gav 12 rader med fel
  tal i budgeten ("500" och "1 000" blev "5001000").
* Neutralt, eftersom inget av dem läser löptext eller gör OCR; de skulle
  bli ett tillägg till A, inte ett alternativ.

### F – PaddleOCR för OCR

PaddleOCR (Apache-2.0) med `lang="sv"`, som ger modellen PP-OCRv6 medium,
på blanketten och de skannade protokollen i 300 dpi.

* Bra, eftersom det hittade alla femton kontrollerade värden på blanketten
  och läste alla 117 tal på protokollen rätt.
* Dåligt, eftersom å blev fel ("Kvarstaende", "frán", "Ar 2025"); ö blev
  rätt.
* Dåligt, eftersom en sida tog 107–174 sekunder utan GPU, mot 2–4 sekunder
  för Tesseract, och PaddlePaddle måste köras utan oneDNN för att alls gå.
  Som enda motor är det för långsamt; i H läser det bara om enstaka rader.

### G – MinerU och Marker

* MinerU (AGPL) är en layoutmodell som B, med samma invändning: en
  modells tabell säger inte när den har fel. Inte prövad, eftersom B
  redan visar hur sådana modeller beter sig på proven.
* Marker uppfyller inte kravet på öppen källkod: koden är GPL, men
  modellvikterna har en licens som begränsar vem som får använda dem.

### H – RapidOCR och Tesseract, där PaddleOCR avgör

RapidOCR (Apache-2.0, på onnxruntime, MIT) med modellerna PP-OCRv6 small,
som följer med paketet, läser sidan rad för rad; Tesseract läser samma
sida. Där de läser talen på en rad olika läser PaddleOCR (F) om raden, och
en läsning gäller bara när två motorer är eniga. Inte valt nu, eftersom
tal ur skanningar inte behövs i dag. Reglerna i sammandrag; den
fullständiga, granskade versionen står i ARKITEKTUR i commit `1be9f93`
och behövs för att bygga H:

* Raderna är RapidOCR:s, med den rektangel som omsluter radens
  fyrhörning; Tesseracts ord hör till den rad som innehåller ordets
  mittpunkt, och ord utanför alla rader bildar egna rader efter
  Tesseracts radnummer.
* Ett sifferfält är siffror skilda av `,` `.` `:` `/` `-`, med `-` direkt
  före och `%` direkt efter; `−` och `–` görs om till `-` och `80 %` till
  `80%` före jämförelsen. Ett mellanslag avslutar fältet.
* En rad är bekräftad när två läsningar har samma sifferfält i samma
  ordning. PaddleOCR läser om raden, utskuren med 15 bildpunkters
  marginal i 300 dpi, när RapidOCR och Tesseract är oense. En läsning
  utan sifferfält kan aldrig bekräfta en med sifferfält.
* Obekräftade rader står i ett kodblock märkt `tal-obekraftade`.

* Bra, eftersom inget fel tal blev kvar omärkt på de åtta handlästa
  sidorna: 20 av 21 oeniga rader avgjordes rätt och den sista märktes.
* Bra, eftersom RapidOCR ensam läste 116 av 117 tal rätt och klarade de
  försämrade bilderna i kalibreringen mycket bättre än Tesseract.
* Bra, eftersom det kostar ingenting och alla licenser är öppna
  (Apache-2.0 och MIT).
* Dåligt, eftersom RapidOCR tappade en hel rad på en sida utan att märka
  det; det fångas bara för att Tesseract läste raden.
* Dåligt, eftersom RapidOCR läste å som á eller à på blanketten ("frán",
  "Kvarstäende"), fast inte på protokollen.
* Dåligt, eftersom tre motorer och PaddlePaddle är större och långsammare
  än Tesseract ensam: ungefär 11 sekunder per skannad sida i stället för
  3, och ett par sekunder till för varje oenig rad.
* Dåligt, eftersom PaddleOCR:s modeller inte följer med paketet utan
  laddas ned första gången, som RapidOCR:s inte behöver. En körning utan
  nät, som i CI (#5), måste få dem i förväg, med samma version som
  `pipeline` anger.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Fas 0 (agenten).** Fyra saker att bestämma: verktyg, OCR, `pipeline`
   och kvalitetsnivåerna. `status` var redan löst av ADR-0004: `kvalitet`
   och `fel` tillsammans.
2. **Fem frågor till ägaren, med agentens rekommendation:** utesluta AGPL
   på förhand, låta den sämsta sidan avgöra, ta versionen i `pipeline` ur
   `pyproject.toml`, hålla jämförelseskriptet utanför repot och bara
   redovisa resultatet här, och låta ägaren ladda upp provfiler. **Ägaren
   sa ja** till de fyra första 2026-10-06, och ville att provfilerna
   hämtades från källan i stället.
3. **Provfilerna.** Den första molnmiljön nådde varken kungsbacka.se,
   Internet Archive eller Hugging Face. Ägaren öppnade nätet i en ny miljö,
   så att jämförelsen gjordes på handlingar hämtade direkt från källan.
4. **Under skrivandet (agenten)** lades till att text från OCR under
   tröskeln inte skrivs alls, att tabeller på en OCR-sida inte blir CSV,
   och att en fil som inte går att öppna får en orsak i `fel`.
5. **Jämförelsen (agenten)** ändrade tre saker i utkastet:
   * Ritade linjer måste skiljas från fyllda ytor. pdfplumbers
     standardinställning tog tjänsteskrivelsernas rosa radbakgrunder för
     cellgränser och gav nio kolumner i stället för tre, och budgetens gula
     markering av en kolumn för en tabell där bara den kolumnen fanns.
   * En osäker tabell blir ingen CSV. Utkastet sparade den som CSV märkt
     osäker, men pdfplumbers kolumner efter mellanrum gav fel tal i 33 av
     de 73 budgetrader den läste ut – "4 078" och "4 054" blev "40784" och "054". Det är
     precis det fel som ser riktigt ut, och en märkning hindrar inte att
     det används.
   * Skannade sidor som redan har ett OCR-lager läses ändå med vår OCR.
     Handlingarna innehöll motioner och interpellationer som skannats med
     OCR av någon annan; deras säkerhet går inte att mäta.
6. **Varför inte B, när B läste fler tabeller?** Budgettabellerna är just
   de som analyserna behöver mest, och B fick 115 av dem rätt. Men det
   felaktiga talet i B såg ut som de rätta, och det fanns inget sätt att
   peka ut det utan att jämföra med texten. Agenten bedömde att en pool
   som andra bygger analyser på hellre ska sakna en CSV än innehålla en
   som kan vara fel, och att 6 GB beroenden och nästan fyra sekunder per
   sida väger tungt i #5. Underlaget är tunt: B:s fel är ett enda fall i
   ett budgetprov på sju sidor.
7. **Ägarens val.** Agenten lade fram tre vägar: A, B, eller A med ett
   eget issue för budgettabellerna. Ägaren valde det sista 2026-10-06, och
   det blev [#15](https://github.com/moggleif/kommunhandlingar/issues/15).
8. **Licensen ändrades.** När resultatet visades sa ägaren 2026-10-06
   att MIT bara var ett val för att välja något: kravet är öppen källkod,
   allt publikt och gratis. AGPL-uteslutningen ströks. Det ändrade inte
   valet, eftersom det avgjordes av tabellernas mekaniska säkerhet, men
   OCRmyPDF:s förberedelse av bilden, som läste blanketten bäst, får
   prövas när OCR-steget skrivs. Ägaren bad också att fler verktyg
   skulle finnas med som stöd för beslutet; Camelot, Tabula och
   PaddleOCR prövades då på samma prov (E och F), och MinerU och Marker
   övervägdes (G). Inget av dem ändrade valet.
9. **Granskningen (fas 6)** ledde till att reglerna fick en ordning och
   exakta definitioner, att de bara står i ARKITEKTUR, att skanningar
   känns igen på hur lite synlig text de har, så att omslag med
   helsidesfoto inte räknas, att ett textlager inte kastas för att sidan
   har en liten bild, och att en tom sida avgörs på den renderade bilden
   och inte på att OCR inte hittar något.
10. **Rätt före snabbt.** När valet var gjort sa ägaren 2026-10-06 att det
    viktiga är att det blir rätt, inte att det går fort. Agenten breddade
    då proven: fyra hela tabelldokument med ett facit som inte kom från
    något av verktygen, och åtta skannade sidor utskrivna för hand.
    Tabellprovet bekräftade A. OCR-provet visade att Tesseract läste
    vart åttonde tal fel på gamla skanningar utan att säkerheten sjönk,
    och agenten föreslog att RapidOCR och Tesseract skulle läsa varje sida
    och att oenighet skulle märkas.
11. **Kan det som blev fel läsas om?** Ägaren frågade 2026-10-07 varför
    inte agenten läste sidorna, eftersom alla motorer gör fel. Agenten
    svarade att det kostar pengar per sida, inte går att köra utan en
    session och inte ger samma läsning två gånger. Ägaren frågade då om
    det som blev fel kunde läsas om. Agenten prövade att låta PaddleOCR
    läsa om bara de oeniga raderna, och det avgjorde 20 av 21 rätt.
    Ägaren valde det 2026-10-07 (ändrat i punkt 12), och bestämde
    samtidigt att text och tal märks var för sig: talen ska vara 100 %
    bekräftade för att datat ur en handling ska användas, medan texten
    inte är lika viktig i dag.
12. **Behövs tal ur skanningar alls?** Ägaren frågade 2026-10-07, medan
    PR:en lästes, om skannade delar kunde vänta, eftersom datat
    troligen finns i de moderna handlingarna. Agenten höll med: det som är
    skannat är mest bilagor, och bara blanketterna för partistöd hade
    belopp. Agenten lade fram tre vägar: hoppa över skanningar, bara text
    från dem, eller H, och rekommenderade bara text. Att hoppa över dem
    riskerar att de är borta när de behövs, eftersom PDF:en raderas och
    kommunen bara visar ett par år bakåt. **Ägaren valde bara text**
    2026-10-07, med H som väg framåt vid behov, kanske med bättre verktyg
    då.

### Jämförelsen

Fem prov hämtade från kungsbacka.se 2026-10-06: kommunfullmäktiges
protokoll och handlingar från mötet 2026-08-11 och kommunbudget 2027.
Proven 1–4 är utdrag; prov 3 ur budgeten och prov 2 och 4 ur
handlingarna. Internet Archive gick inte att nå (anslutningen bröts varje
gång), så inga äldre handlingar från Episerver kom med.

| Prov                     | Sidor | Vad                                                         |
| ------------------------ | ----: | ----------------------------------------------------------- |
| Protokoll                |     9 | Löptext, närvarolista, underskriftssida                     |
| Tjänsteskrivelse         |     9 | Löptext och åtta tabeller med linjer och färgade rader      |
| Budget                   |     7 | Tabeller med bara vågräta linjer, en färgad kolumn, diagram |
| Inskannat                |    10 | Ifyllda blanketter för partistöd, och två skannade sidor med OCR-lager |
| Handlingar, hela         |   228 | Sammanslagen handlingar-PDF, 46 MB, 31 skannade sidor       |

Oläsliga tecken och skanningar räknades dessutom i de hela filerna: 228
sidor handlingar, 47 sidor protokoll och 68 sidor budget.

**Tabeller.** Facit för budgeten är `pdftotext -layout` (D:s verktyg),
kontrollerat mot sidbilden för kassaflödesanalysen. Varje rad med en
etikett och minst två tal är en facitrad (135 rader). En rad är rätt om
etiketten och alla tal stämmer i samma ordning.

| Alternativ                          | Linjerade tabeller (85 rader) | Budget, rätt | Budget, fel tal |
| ----------------------------------- | ----------------------------: | -----------: | --------------: |
| A, ritade linjer                    | 85                            | 0 (osäkra)   | 0               |
| A, kolumner efter mellanrum         | –                             | 40           | 33              |
| B, Docling                          | 85                            | 115          | 1               |
| C, pymupdf4llm                      | 85                            | 113          | 0               |
| D, pdftotext                        | 0 (text)                      | 0 (text)     | 0               |

**OCR.** Femton värden lästa för hand ur den första blanketten: parti,
rubriker, belopp och namn. Inom A gav olika förberedelse av bilden mellan
8 och 12; den bästa förberedelsen bestäms när konverteringen skrivs, mot
blanketten som testfixtur.

| Alternativ                                    | Hittade | Svenska tecken             |
| --------------------------------------------- | ------: | -------------------------- |
| A, Tesseract, sidan renderad i 300 dpi        | 8 / 15  | rätt                       |
| A, Tesseract, sidan renderad i 400 dpi        | 11 / 15 | rätt                       |
| A, Tesseract, skanningens egen bild (144 dpi) | 12 / 15 | rätt                       |
| B, Docling med RapidOCR                       | 15 / 15 | fel ("Kranor", "frán")     |
| C, pymupdf4llm                                | 15 / 15 | delvis fel ("Kvarstàende") |
| D, OCRmyPDF (Tesseract)                       | 14 / 15 | rätt                       |
| H, RapidOCR (PP-OCRv6 small), 300 dpi         | 15 / 15 | delvis fel ("frán", "Kvarstäende") |

**OCR-säkerhetens tröskel.** Sju sidor med textlager renderades,
försämrades i fem steg (300, 150 och 100 dpi, suddig och lågupplöst,
simulerad skanning med lutning och brus) och lästes med Tesseract.
Textlagret var facit, och ordningen räknades inte. På sidor med löptext
hittades över medelsäkerheten 75 minst 85 % av facits ord (oftast över
93 %) och minst 84 % av orden med å, ä eller ö. Under 67 hittades högst
74 %, oftast långt färre. De 31 riktiga skanningarna i handlingarna låg
mellan 71 och 96. Budgetsidan med tabeller är undantaget: i 150 och 100
dpi hittades bara 59–71 % av orden vid en medelsäkerhet på 85–92 – ännu
ett skäl till att OCR-sidor inte får CSV:er.

**Tid,** fyra processorkärnor utan GPU, hela handlingar-PDF:en:

| Alternativ | Tid                                     |
| ---------- | --------------------------------------- |
| A          | 113 s, med OCR av de 31 skannade sidorna |
| B          | 849 s                                   |
| C          | 112 s                                   |
| D          | 1 s text, 25 s OCRmyPDF                 |

**Prövat efter valet,** när licenskravet ändrats till öppen källkod,
med samma facit:

| Verktyg                 | Linjerade tabeller (85 rader) | Budget, rätt | Budget, fel tal |
| ----------------------- | ----------------------------: | -----------: | --------------: |
| Camelot, linjer         | 85                            | 0            | 0               |
| Camelot, mellanrum      | 11 av 236                     | 104          | 0               |
| Tabula, linjer          | 0 av 284                      | 52           | 0               |
| Tabula, mellanrum       | 11 av 213                     | 96           | 12              |
| PaddleOCR, blanketten   | 15 / 15 värden, å fel, 108 s för sidan | |               |

**Bredare prov för tabellerna.** Fyra hela, tabelltunga dokument från
kungsbacka.se: delårsrapport 2024, kommunbudget 2025, årsredovisning 2025
och kommunbudget 2027, sammanlagt 247 sidor. Facit togs fram oberoende av
verktygen som prövas: en rad (etikett och minst två tal) ur
`pdftotext -layout` godtogs bara om samma etikett och samma tal i samma
ordning fanns på en rad i pdfplumbers ord, grupperade efter mellanrummen.
Det gav 1 090 bekräftade rader. En rad räknas som **fel** om dess tal, i
ordning, inte finns som en sammanhängande följd på någon verklig rad i
dokumentet – talen har slagits ihop, delats eller flyttats mellan rader.
Felen kontrollerades för hand.

| Verktyg            | Rätt av 1 090 | Fel rader | Vad felen var                                              |
| ------------------ | ------------: | --------: | ---------------------------------------------------------- |
| A, ritade linjer   | 92            | 0         | –                                                          |
| Camelot, linjer    | 92            | 0         | –                                                          |
| B, Docling         | 720           | 26        | Rader ur två tabeller bredvid varandra lagda i samma rad   |
| C, pymupdf4llm     | 751           | 8         | Samma sak, och rubrikrader med år ihopslagna ("20242025") |
| Camelot, mellanrum | 959           | 8         | En fotnotssiffra eller ett sidnummer lagt till som sista tal |

De 92 raderna är delårsrapportens linjerade tabeller; resten av
dokumentens tabeller saknar lodräta linjer och är det #15 gäller. Docling
tog 2 508 sekunder för de 247 sidorna, ungefär tio sekunder per sida.

**Bredare prov för OCR.** Åtta skannade sidor ur handlingarna från
kommunfullmäktige 2024-03-05: protokoll skrivna på skrivmaskin 1989, och
protokoll från 2002, 2006, 2014 och en förenings protokoll från 2023.
Facit är sidorna utskrivna för hand, 1 327 ord och 117 tal och datum. Ett
tal räknas som rätt om det läses exakt, med skiljetecken, i rätt ordning.
Sidorna renderades i 300 dpi, samma upplösning som skanningarna.

| Motor                      | Ord rätt | Tal rätt  | Medelsäkerhet | Sekunder per sida |
| -------------------------- | -------: | --------: | ------------: | ----------------: |
| Tesseract, svensk modell   | 95,3 %   | 103 / 117 | 78–95         | 2–4               |
| Tesseract, `tessdata_best` | 95,5 %   | 106 / 117 | 80–95         | 2–7               |
| RapidOCR (PP-OCRv6)        | 94,7 %   | 116 / 117 | 97–99         | 5–11              |
| PaddleOCR (PP-OCRv6 medium) | 96,4 %  | 117 / 117 | 96–100        | 107–174           |

Tesseracts fel var tecken som
byttes: "80%" blev "803", "10%" blev "1020", "0446/87-455" blev
"0446/87-4535" och "§ 83" blev "883", i de här exemplen på sidor med
medelsäkerhet 88–95.
RapidOCR läste talen rätt men tappade en hel rad på en sida och ersatte
den med skräptecken, med samma höga säkerhet som annars. Där Tesseract
och RapidOCR läste samma tal var det rätt i 102 av 102 fall; alla fel
låg där de två var oense. Å, ä och ö lästes lika bra av båda på
protokollen, men RapidOCR läste å som á eller à på blanketten ("frán",
"Kvarstäende").

Kalibreringen ovan gjordes om med båda motorerna och med andelen av
textlagrets tal som läses exakt, oavsett ordning. På budgetsidan i 150 och
100 dpi läste Tesseract 25 och 12 % av talen vid säkerhet 92 och 85;
RapidOCR läste 83 och 72 % på samma bilder. På den simulerade skanningen
läste Tesseract 0–50 % av talen och RapidOCR 78–100 %. Tesseracts säkerhet
föll med läsningen men inte nog för att skydda talen; RapidOCR:s låg på
96–100 i alla försämringar och säger ingenting om hur bra läsningen är.

**Omläsning av oeniga rader.** På de åtta sidorna var RapidOCR och
Tesseract oense om talen på 21 rader, eller så hittade bara Tesseract
raden. Raderna skars ut med 15 bildpunkters marginal och lästes om av
PaddleOCR, på 35 sekunder för alla 21. På 20 rader hade PaddleOCR samma
tal som en av de två, och den läsningen var rätt varje gång; det gällde
också raden som RapidOCR tappat. På den sista fick utskärningen med text
från raderna intill, så att ingen läsning stämde, och raden blev
obekräftad fast talet var rätt läst. Inget fel tal blev kvar som
bekräftat.

### Vad som inte avgörs här

* Hur sammanslagna handlingar delas upp per ärende.
* Tabeller som fortsätter över en sidbrytning.
* Diagram och scheman. Texten i dem följer med i sidans text, men inte
  formen, och bilder lagras inte
  ([ADR-0001](0001-ett-repo-bara-text.md)). Att göra om dem till till
  exempel Mermaid kräver en modell som tolkar bilden; inget av de prövade
  verktygen gör det. Ägaren bestämde 2026-10-07 att agenten får tolka dem
  i en session, och hur sidorna märks och tolkas avgörs i
  [#17](https://github.com/moggleif/kommunhandlingar/issues/17).
* CSV-schemat och härkomsten för tabellfilerna
  ([#9](https://github.com/moggleif/kommunhandlingar/issues/9)).

### När beslutet bör omprövas

* Om budget- och uppföljningstabeller utan linjer visar sig vara det
  analyserna oftast behöver. Då kan ett andra steg läsa dem – med en
  layoutmodell som B eller med kolumner efter rubrikernas läge – om
  varje tal kan stämmas av mot textlagret innan CSV:n skrivs.
* Om OCR-säkerheten ofta hamnar under tröskeln på sidor som går att läsa
  för ögat.
* Om tal ur skanningar behövs, till exempel partistödets belopp. Då är H
  vägen, eller ett bättre verktyg om ett sådant finns då. H:s bekräftelse
  bygger på åtta sidor ur en handling och bör först prövas på fler
  skanningar, särskilt blanketter.
