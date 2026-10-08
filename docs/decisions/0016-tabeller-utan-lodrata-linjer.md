---
status: proposed
date: 2026-10-08
decision-makers: projektägaren
consulted: AI-agenten
---

# Tabeller utan lodräta linjer läses ur textlagrets ord och blir CSV bara när talen står i linje

## Context and Problem Statement

Enligt [ADR-0005](0005-konvertering-verktyg-ocr-och-kvalitet.md) är en
tabell säker bara när ritade linjer avgränsar cellerna. Budget- och
uppföljningstabeller har oftast bara vågräta linjer, eller inga alls, så
just de tal som analyserna behöver mest blir ingen CSV. De står i stället
i ett kodblock märkt `osaker-tabell`
([#15](https://github.com/moggleif/kommunhandlingar/issues/15)).

Efter första nattkörningen fanns 588 sådana block på 391 sidor i 91
dokument, alla handlingar från nämnderna. Fullmäktiges budgetar och
årsredovisningar hade inte kommit in än.

Hur kan en tabell utan lodräta linjer bli CSV utan att ett enda tal hamnar
i fel cell?

## Decision Drivers

* **Ett fel tal som ser riktigt ut är värre än ett som saknas**
  (ADR-0005). Varje tal i en CSV ska kunna användas som data. Det gäller
  också vilken rad och kolumn det står i.
* **Avstämt mot textlagret.** Projektägaren valde 2026-10-06 att en
  olinjerad tabell blir CSV bara när varje tal kan stämmas av mot
  textlagret.
* **Hellre märka än gissa.** Den tabell som inte går att stämma av förblir
  osäker, som i dag.
* **Inga nya beroenden** om det går. pdfplumber ger redan varje ord med
  koordinater.

## Considered Options

* A – Egna kolumner efter talens högerkant, ur textlagrets ord
* B – Camelot efter mellanrum, med talen avstämda mot textlagret
* C – En layoutmodell (Docling), med cellerna avstämda mot textlagret
* D – Som i dag: ingen CSV utan lodräta linjer

## Decision Outcome

Valt: A, eftersom det är det enda alternativet där varje cell byggs direkt
ur textlagrets ord och där varje villkor för att tabellen ska godtas går
att pröva mekaniskt. B och C ger celler som sedan måste stämmas av, och
avstämningen blir då samma regler som A ändå.

Reglerna står i
[ARKITEKTUR](../03-ARKITEKTUR.md#tabeller-utan-lodrata-linjer). I korthet:

* raderna är textlagrets ord grupperade efter överkanten, och ett ord
  delas där teckenstorleken ändras,
* ett mellanrum är antingen inom ett fält (högst en halv teckenhöjd) eller
  mellan två fält (minst en hel), och ett mellanrum däremellan gör raden
  oanvändbar,
* varje rad är en etikett följd av minst ett tal eller streck, och
  raderna står högst tre teckenhöjder isär,
* talen står med högerkanten i linje (högst 2 punkter ifrån), varje
  kolumn har minst två tal, strecken står i linje med en kolumn,
  kolumnerna överlappar inte varandra eller etiketterna, och den första
  kolumnen är inte bara år eller koder,
* rubrikraderna ovanför följer med bara om hela rubriken står i linje
  och den översta raden har en rubrik i varje kolumn,
* inget annat ord, inte heller i en tabell med linjer, ligger inom
  tabellens yta.

Mätningen visade också en brist i ADR-0005:s regel för tabeller med
linjer: två rader eller kolumner som linjerna inte skiljer åt hamnar i
samma cell, till exempel `2 445,1 -8 323,3 -5 878,2 143,4` eller
`4 078⏎4 054`. Talen är rätt, men cellen är fel. I poolen gällde det 324 av 8 403 CSV:er. **En
tabell med linjer där en cell rymmer mer än ett tal är därför inte längre
säker.** Det prövas både på cellens text och på ordens lägen, med samma
regel för fält som ovan. Tabellen prövas i stället enligt reglerna ovan, och klarar den inte
dem blir den osäker. Det skärper ADR-0005:s definition av en säker
tabell; resten av ADR-0005 gäller som förut.

Poolens version höjs till 0.2.0, eftersom konverteringen skriver annat än
förut.

### Consequences

* Bra, eftersom budgettabeller med talen i linje blir CSV: i fyra
  budgetdokument 98 tabeller med 612 rader, utan ett enda fel tal.
* Bra, eftersom inget nytt beroende behövs, och regeln är kort nog att
  läsa i ARKITEKTUR.
* Bra, eftersom en cell med flera tal, i de former reglerna känner igen,
  inte längre blir en del av en CSV.
* Dåligt, eftersom många tabeller förblir osäkra: tabeller med en
  kodkolumn före etiketten, med centrerade tal, med åldrar eller år som
  etikett, eller med ett sidnummer eller en fotnot direkt under. I de fyra
  dokumenten var 21 av 41 sidor fortfarande `tabell-osaker`.
* Dåligt, eftersom en rad med bara årtal direkt ovanför tabellen, högst
  tre teckenhöjder ifrån, blir en talrad i följden, och då blir hela
  tabellen osäker.
* Dåligt, eftersom text i en spalt bredvid en tabell utan etiketter, där
  den första kolumnen är tal men inte år eller koder, kan bli tabellens
  etiketter. Granskningen visade fallet med år; i de 33 dokumenten fanns
  inget av det andra slaget.
* Dåligt, eftersom en etikett som bryts över två rader står i CSV:n med
  den del som står på talens rad; resten står i texten.
* Dåligt, eftersom rubrikerna oftast inte följer med: bara 14 av 98
  tabeller fick rubrikrader. Rubrikerna står kvar i texten ovanför.
* Dåligt, eftersom en tabell med linjer som har flera tal i en cell nu
  blir osäker också när en människa kan läsa den. 324 av poolens 8 403
  CSV:er hade en sådan cell; i stickproven var nästan alla
  sammanslagna rader, men också listor som `240304 1 st⏎240318 1 st`.
* Neutralt, eftersom en upphöjd fotnotssiffra direkt efter ett tal
  fortfarande står ihop med talet i texten, som förut. Den blir bara inte
  en del av en CSV.
* Dåligt, eftersom dokument som redan finns i poolen inte ändras förrän de
  konverteras om, och det kräver ny hämtning (ADR-0004). Hit hör de 324
  CSV:erna med flera tal i en cell.
* Neutralt, eftersom diagrammens axlar och teckenförklaringar, som också
  blir talrader, förblir osäkra. De hör till
  [#17](https://github.com/moggleif/kommunhandlingar/issues/17).

### Confirmation

* Fixturer i `tests/fixtures/pdf/sidor.pdf` med facit som går att räkna
  för hand: en tabell utan lodräta linjer, en med rubrikrad, tom cell och
  streck, en där talen inte står i linje, en tabell med linjer där en
  cell rymmer två tal, och en med en upphöjd fotnotssiffra direkt efter
  ett tal (`tests/test_olinjerade.py`, `tests/test_konvertering.py`).
* Påhittade ord med koordinater prövar varje regel för sig: fälten, rader
  utan etikett, tal och streck ur linje, en kolumn med ett enda tal, text
  mellan kolumnerna, ett tvetydigt mellanrum, radavståndet, en tabell med
  linjer mellan två tabeller, ett ord till inom tabellens yta, för få
  rader och varje regel för rubrikraderna.

## Pros and Cons of the Options

### A – Egna kolumner efter talens högerkant

* Bra, eftersom varje cell är textlagrets ord, så inget tal kan delas,
  slås ihop eller flyttas till en annan rad.
* Bra, eftersom varje villkor prövas mekaniskt, och en tabell som inte
  klarar alla blir osäker i stället för fel.
* Bra, eftersom talen i budgetar och bokslut nästan alltid är
  högerställda.
* Dåligt, eftersom det missar tabeller som en människa ser direkt, till
  exempel med centrerade tal eller en kodkolumn.

### B – Camelot efter mellanrum, avstämt mot textlagret

* Bra, eftersom det fick flest rader rätt i ADR-0005:s bredare prov:
  959 av 1 090.
* Dåligt, eftersom det lade en fotnotssiffra eller ett sidnummer till som
  sista tal i 8 rader; det måste stämmas av, och avstämningen kräver
  samma regler som A.
* Dåligt, eftersom samma läge förstörde tabellerna med linjer, så det
  måste veta vilken sorts tabell det är.
* Dåligt, eftersom det är ett nytt beroende.

### C – En layoutmodell, avstämd mot textlagret

* Bra, eftersom den ser tabeller utan linjer som en människa gör.
* Dåligt, eftersom Docling flyttade tal mellan rader i 26 rader i
  ADR-0005:s prov utan att något i utdata visade det.
* Dåligt, eftersom det kräver 6,4 GB beroenden och ungefär tio sekunder
  per sida utan GPU.

### D – Som i dag

* Bra, eftersom ingenting kan bli fel.
* Dåligt, eftersom budgetarnas tal aldrig blir data.

## More Information

1. **Uppdraget.** Projektägaren valde 2026-10-06 att budgettabellerna
   skulle få ett eget steg (ADR-0005, punkt 7), och i fas 0 2026-10-08 att
   #15 och #17 görs i var sin PR, #15 först.
2. **Mätningen.** Fyra dokument hämtades från kungsbacka.se 2026-10-08:
   kommunbudget 2027 och 2025 och årsredovisning 2025 och 2024. Med A
   blev 98 tabeller med 612 rader CSV, och 41 sidor med osäker tabell
   blev 21. Ingen rad skilde sig från samma rad i pdfplumbers text med
   uppställning: etiketten och talen i samma ordning. Kolumnerna
   kontrollerades för hand mot sidan i nio tabeller. I 29 slumpvis valda
   handlingar från nämnderna (1 876 sidor) blev 6 tabeller med 61 rader
   CSV, och 53 sidor med osäker tabell blev 51. Där blev också 3 av 485
   tabeller med linjer osäkra, eftersom en cell rymde en hel rad med tal. Där var de flesta osäkra
   "tabellerna" diagramaxlar, innehållsförteckningar och tabeller med en
   kodkolumn.
3. **Varför rubrikerna kräver hela raden.** En rubrik som bara delvis
   följer med, till exempel bara den nedre raden av en tvåradig rubrik,
   ger en kolumn ett missvisande namn. Agenten valde att hellre lämna
   rubriken i texten än att ta med en halv.
4. **Varför minst två värden per kolumn.** Ett ensamt tal som står ur
   linje skulle annars bli en egen kolumn, utan rubrik och mellan de
   riktiga. I proven var det oftast ett sidnummer under tabellen.
5. **Bristen i tabellerna med linjer** hittades när ett bokslut fick halva
   tabellen som "säker", med fyra tal i en cell, och resten utan linjer.
   Agenten bedömde att det strider mot ADR-0005:s krav att varje tal i en
   CSV ska gå att använda som data, och att rättelsen hör hit eftersom
   reglerna nu läser samma tabeller.
6. **Granskningen (fas 6)** hittade fyra fall där en cell kunde bli fel:
   en upphöjd fotnotssiffra som pdfplumber lade ihop med talet (`40` och
   `3` blev `403`), två tabeller som slogs ihop över en tabell med linjer
   emellan, ett centrerat streck som blev en egen kolumn, och celler med
   flera tal som den första regeln för tabeller med linjer släppte igenom
   (`65 %⏎70 %`, `4 078⏎-`). Orden delas därför där teckenstorleken
   ändras, avståndet mellan raderna begränsas, tabellerna med linjer
   räknas med när tabellens yta prövas, strecken måste stå i en kolumn med
   tal, och en cell prövas rad för rad. Granskningen ledde också till att
   den översta rubrikraden måste ha en rubrik i varje kolumn, så att en
   titel eller en enhet för hela tabellen inte blir en kolumns rubrik.
   Det andra varvet hittade tre fall till: löptext i en spalt bredvid
   en tabell med år som första kolumn blev tabellens etiketter, celler
   som `(2 100)⏎1 978` och `1 234 (1 150)` räknades som ett tal, och tre
   kolumner tresiffriga tal utan lodräta linjer emellan, `120 135 142`,
   såg ut som ett tal med tusentalsmellanrum. En första kolumn med bara
   år eller koder gör därför tabellen osäker, en cell prövas rad för rad
   med parenteser och snedstreck som skiljetecken, och mellanrummen
   mellan orden i en cell prövas med samma regel som fälten. Agenten
   valde regeln om år och koder framför en regel om stycken, eftersom
   den inte ändrade någon av de 104 tabellerna i proven, medan en regel
   om text ovanför och under också hade fällt tabeller med en titel.
7. **Omprövas** om en vanlig sorts tabell förblir osäker, till exempel
   tabeller med kodkolumn; då kan reglerna utökas med fler etikettfält.
