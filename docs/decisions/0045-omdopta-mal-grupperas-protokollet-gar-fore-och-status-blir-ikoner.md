---
status: accepted
date: 2026-10-13
decision-makers: projektägaren
consulted: AI-agenten
---

# Omdöpta mål grupperas i målfilen med tolkade kopplingar märkta, protokollet går före handlingarna, status blir ikoner, och sidan räknar antal per år

## Context and Problem Statement

Sidan om GA:s mål och direktiv (K26,
[ADR-0044](0044-namndens-mal-och-direktiv-las-ur-dokumenten-och-skrivs-for-hand.md))
visar varje rubrik som ett eget mål. Projektägaren vill kunna följa mål
som bytt namn, med rubrikerna under varandra
([#146](https://github.com/moggleif/kommunhandlingar/issues/146)). När
protokollet och handlingarna från samma möte säger olika ska protokollet
gälla. Budgeten 2026 är ett sådant fall: protokollet 2025-10-16, § 121,
ändrar "Hälsofrämjande livsstil" till "Hälsofrämjande och fysisk aktiv
livsstil". Statusen ska visas med ikoner som går att återanvända, och
sidan ska visa hur många mål och direktiv nämnden haft per år och hur
många uppföljningar som redovisat dem.

Källan säger bara på ett ställe uttryckligen att ett mål bytt namn. Hur
blir kopplingen synlig utan att sidan ser säkrare ut än källan?

## Decision Drivers

* **Hellre märka än gissa.** En koppling som är en bedömning ska synas
  som en bedömning.
* **Varje uppgift bär sin härkomst.** En grupp ska bestå av rubriker som
  står i källan, inte av ord som agenten hittat på.
* **Tomt är inte noll.** Ett år utan mål i filen kan vara ett år där
  dokumenten saknas i poolen.
* **Ingen information bärs av färgen ensam.**
* **Ingen kod för säkerhets skull.**

## Considered Options

* A – Två kolumner i målfilen: `grupp`, en rubrik i filen som rubrikerna i
  gruppen samlas under, och `tolkad`, som märker en rubrik vars plats i
  gruppen är en bedömning
* B – En separat fil med kopplingar mellan rubriker
* C – Kopplingen räknas fram ur likheten mellan formuleringarna
* D – Bara de kopplingar källan själv gör (alternativ D i ADR-0044)

## Decision Outcome

Valt: A, eftersom kopplingen står på samma rad som målet och granskas i
samma diff, gruppen är en rubrik som finns i källan, och bedömningen syns
på sidan.

* **`grupp`** är tom eller en rubrik i filen för samma organ, oftast den
  senaste, som inte själv står i en grupp. Rader med samma grupp, eller
  med en rubrik som är gruppen, är ett spår. Alla rader med samma rubrik
  har samma grupp, och ett spår har en rubrik per år: två mål som står
  bredvid varandra samma år är inget namnbyte och grupperas inte.
* **`tolkad`** är tom eller `ja`, och `ja` bara i en grupp. Den sätts när
  källan inte säger att det är samma mål och formuleringen inte är
  densamma. Kopplingen gäller rubriken i gruppen: en rubrik som har samma
  formulering som gruppens senare rubriker är inte tolkad.
* **Protokollet går före handlingarna.** Står samma spår samma år ur både
  protokollet och handlingarna från ett möte (samma katalog i poolen),
  stoppas bygget. Bara protokollets rad ska stå med.
* **Uppföljning och bedömning står i målfilen.** `uppfoljning` är tom
  för budgeten, annars `prognos` (delårsrapport), `utfall`
  (årsredovisning) eller `rapport` (annan rapport till nämnden).
  `bedomning` är agentens läsning av statusen: `uppnatt`, `delvis`, `ej`
  eller `ingen`. Den finns på varje uppföljning och bara där.
* **Status som ikon.** `webbplats/statusikon.py` visar bedömningen som en
  liten SVG-figur med egen form, med källans formulering i pekrutan, och
  en prognos har en streckad ram. Stilen står i den gemensamma sidmallen.
* **Antal per år.** Sidan har en tabell och en linjegraf i SVG, utan
  skript. Tabellen och grafen visar antal rubriker per år och slag. Tabellen
  visar också antal uppföljningsdokument och antal rubriker med en status.
  Ett år utan rader är tomt, inte noll.

### Consequences

* Good, eftersom ett mål som bytt namn går att följa i översikten.
* Good, eftersom en bedömning syns som "tolkad" på sidan och i filen.
* Good, eftersom en rad ur handlingarna som protokollet ändrat inte går
  att lägga in av misstag.
* Good, eftersom ikonerna kan användas av andra sidor, och inget om en
  kommuns formuleringar eller arbetsår står i koden.
* Bad, eftersom gruppen är agentens arbete och inte prövas mot källan
  på annat sätt än att rubrikerna finns.
* Bad, eftersom ikonen förenklar: "Vi har inte nått målet men är på rätt
  väg" och "Delvis uppnått" får samma ikon.
* Bad, eftersom bedömningen och slaget av uppföljning är agentens arbete
  och skrivs på varje rad.
* Bad, eftersom antalet uppföljningar bara räknar dokument i målfilen.
  Andra rapporter till nämnden, som kvartalsuppföljningen av
  arbetsmarknadsprocessen, räknas inte förrän deras rader står där.

### Confirmation

`tests/test_malgrupper.py` prövar grupperna, kontrollerna, ikonerna,
antalet och grafen med en påhittad kommun. `tests/test_mal.py` prövar ikonerna och
att Kungsbackas fil går igenom kontrollen mot poolen.

## Pros and Cons of the Options

### A – `grupp` och `tolkad` i målfilen

* Good, eftersom kopplingen granskas rad för rad i samma diff som målet.
* Good, eftersom gruppens namn är en rubrik ur källan.
* Bad, eftersom samma grupp skrivs på många rader.

### B – En separat fil med kopplingar

* Good, eftersom varje koppling skrivs en gång.
* Bad, eftersom en fil till ska hållas i takt med målfilen.

### C – Likheten mellan formuleringarna

* Good, eftersom ingen behöver bedöma.
* Bad, eftersom formuleringen saknas för de flesta mål från 2024, och
  likhet mellan texter är en gissning som ser ut som ett faktum.

### D – Bara källans egna kopplingar

* Good, eftersom inget är tolkat.
* Bad, eftersom källan bara gör en koppling. De flesta spår förblir
  brutna, också där formuleringen är ordagrant densamma.

## More Information

Agenten gick igenom alla GA-protokoll i poolen som tar upp nämndbudget,
nämndmål, delårsrapport eller årsredovisning. Bara protokollet
2025-10-16 skiljer sig från handlingarna. Protokollet 2018-10-23 höjer
bara målvärden för två indikatorer. Budgetmötena för 2019, 2020, 2022
och 2023 har inget protokoll i poolen.

Agenten föreslog sju grupper. Projektägaren svarade ja till alla
rekommendationerna:

* att handlingarnas rad tas bort när protokollet säger annat,
* att tolkade kopplingar tas med och märks,
* att uppdraget om en demokratifond i samma paragraf inte räknas som
  direktiv, eftersom protokollet inte kallar det så,
* att statusen visas som ikoner,
* att ADR-0044 accepteras.

Grupperna, och om de är tolkade, står i `mal/kungsbacka.csv`.
Kopplingar med samma formulering är inte tolkade, till exempel
Trelleborgsmodellen och Kungsbackas unika arbetsmarknadsprocess, eller
koppling till yrkeslivet och till arbetslivet. Tolkade är till exempel
Främja välmående och Hälsofrämjande livsstil.

Projektägaren bad samtidigt om antalet mål och direktiv per år som tabell
och graf, och frågade hur uppföljningarna kan räknas. Agenten
valde två tal ur målfilen: uppföljningsdokumenten och rubrikerna med en
status. Andra rapporter under året kan läggas till som rader senare.

Statusen är en ikon för fyra bedömningar och inte för varje formulering.
Annars skulle ikonerna bli lika många som formuleringarna och inte gå att
jämföra mellan åren.

Granskningen fann tre fel i första utkastet:

* Översättningen från formulering till bedömning stod i koden, med
  Kungsbackas ord och ett stavfel ur källan. Det bröt regeln att inget om
  en kommun hårdkodas.
* Uppföljning och prognos räknades ur dokumentets datum. Då blev
  uppföljningen av den digitala transformationsplanen i juni 2021 en
  prognos.
* Rubriken "… - fokus på SFI" saknade märkningen tolkad.

Båda uppgifterna står nu i målfilen, och rubriken är märkt. Två rubriker
som stod bredvid varandra samma år togs ur sina grupper, eftersom de
inte är namnbyten: Arbetsmarknadsprocess med fokus på näringslivet
(2019) och Flexibel undervisning (2022). Kontrollen stoppar nu två
rubriker i samma spår samma år.

Märkningen tolkad sätts inte när formuleringen är densamma. Det är
snävare än issuet ("en koppling som källan inte gör själv"). Agenten
redovisade avgränsningen i fas 0, med styrkorna A och B, och
projektägaren svarade ja.
