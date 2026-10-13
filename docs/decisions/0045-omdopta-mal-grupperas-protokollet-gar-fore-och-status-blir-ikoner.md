---
status: proposed
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
  senaste. Rader med samma grupp, eller med en rubrik som är gruppen, är
  ett spår. Alla rader med samma rubrik har samma grupp.
* **`tolkad`** är tom eller `ja`, och `ja` bara i en grupp. Den sätts när
  källan inte säger att det är samma mål och formuleringen inte är
  densamma. Kopplingen gäller rubriken i gruppen: en rubrik som har samma
  formulering som gruppens senare rubriker är inte tolkad.
* **Protokollet går före handlingarna.** Står samma spår samma år ur både
  protokollet och handlingarna från ett möte (samma katalog i poolen),
  stoppas bygget. Bara protokollets rad ska stå med.
* **Status som ikon.** Varje formulering i filen översätts i
  `webbplats/statusikon.py` till en av fyra bedömningar: uppnått, delvis
  uppnått eller på väg, ej uppnått, och ingen bedömning i källan. En ny
  formulering stoppar bygget tills den fått en bedömning. Ikonerna är
  små SVG-figurer med olika form, med källans formulering i pekrutan, och
  stilen står i den gemensamma sidmallen.
* **Uppföljning och prognos räknas ur källans datum.** Budgeten beslutas
  året före. En rad ur ett dokument från samma år eller senare är därför
  en uppföljning, och en uppföljning från samma år är en prognos.
* **Antal per år.** Sidan har en tabell och en linjegraf i SVG, utan
  skript. Tabellen och grafen visar antal rubriker per år och slag. Tabellen
  visar också antal uppföljningsdokument och antal rubriker med en status.
  Ett år utan rader är tomt, inte noll.

### Consequences

* Good, eftersom ett mål som bytt namn går att följa i översikten.
* Good, eftersom en bedömning syns som "tolkad" på sidan och i filen.
* Good, eftersom en rad ur handlingarna som protokollet ändrat inte går
  att lägga in av misstag.
* Good, eftersom ikonerna kan användas av andra sidor, och en ny
  formulering inte kan få fel ikon i tysthet.
* Bad, eftersom gruppen är agentens arbete och inte prövas mot källan
  på annat sätt än att rubrikerna finns.
* Bad, eftersom ikonen förenklar: "Vi har inte nått målet men är på rätt
  väg" och "Delvis uppnått" får samma ikon.
* Bad, eftersom datumregeln gör en rad ur ett dokument från samma år till
  en uppföljning, också om dokumentet är ett utkast till budgeten.
* Bad, eftersom antalet uppföljningar bara räknar dokument i målfilen.
  Andra rapporter till nämnden, som kvartalsuppföljningen av
  arbetsmarknadsprocessen, räknas inte förrän deras rader står där.

### Confirmation

`tests/test_malgrupper.py` prövar grupperna, kontrollerna, antalet och
grafen med en påhittad kommun. `tests/test_mal.py` prövar ikonerna och
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
