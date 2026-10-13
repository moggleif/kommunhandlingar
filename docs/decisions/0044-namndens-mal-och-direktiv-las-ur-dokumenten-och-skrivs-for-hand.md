---
status: proposed
date: 2026-10-13
decision-makers: projektägaren
consulted: AI-agenten
---

# Nämndens mål och direktiv läses ur dokumenten av AI-agenten, skrivs i en CSV per kommun med sidan som källa, och bygget prövar att texten står där

## Context and Problem Statement

Webbplatsen ska visa hur en nämnds egna mål och direktiv har utvecklats
år för år, med status ur uppföljningarna, som en undersida till organet
([#144](https://github.com/moggleif/kommunhandlingar/issues/144)). Först
gäller det Nämnden för Gymnasium & Arbetsmarknad, vars dokument i poolen
spänner från 2013 till 2026 med luckor.

Målen står i nämndbudgetarna och statusen i delårsrapporterna och
årsredovisningarna. Formen har skiftat: 2013 och 2014 har nämndbudgetar
med egna rubriker, 2018 en tabell med "Status direktiv", och sedan 2021
avsnitt märkta "Beslutats av Nämnd" bland kommunfullmäktiges mål. Samma
mål kan byta rubrik mellan åren. Hur kommer målen in på sidan, och hur
blir sidan pålitlig?

## Decision Drivers

* **Varje uppgift bär sin härkomst**, så nära källan som möjligt.
* **Hellre märka än gissa.** Sidan ska inte påstå att två mål är samma
  mål när källan inte säger det.
* **Ingen kod för säkerhets skull.** En tolkning av fem format som byts
  vart annat år är mycket kod för ett hundratal rader.
* **Inget hårdkodat om en kommun.**
* **Bara nämndens egna mål och direktiv**, inte kommunfullmäktiges
  (projektägarens val).

## Considered Options

* A – AI-agenten läser dokumenten och skriver en CSV per kommun med
  dokument och sida per rad; bygget prövar att texten står på sidan
* B – Kod tolkar målen ur poolen när webbplatsen byggs
* C – Som A, men med en sammanfattning per år i egna ord i stället för
  källans text
* D – Som A, men AI-agenten kopplar också ihop mål som bytt namn

## Decision Outcome

Valt: A, eftersom det ger rätt mål med en källa som går att öppna på
rätt sida, och bygget fäller en rad vars text inte står där.

* **Filen** är `mal/<kommun>.csv`, i samma format som kalendern
  (ADR-0032), med kolumnerna `organ`, `ar`, `slag`, `rubrik`,
  `formulering`, `status` och `kalla`. `slag` är `nämndmål` eller
  `direktiv`. `kalla` är ett dokument i poolen med sidan,
  `<organ>/<år>/<datum>/<namn>.md#sida-N`.
* **Texten är källans.** `rubrik`, `formulering` och `status` skrivs
  ordagrant; bara radbrytningar blir mellanslag. En rad per mål, år och
  dokument: budgeten ger formuleringen, uppföljningen statusen.
* **Kontrollen:** bygget stoppas om ett organ inte står i kommunfilen,
  året inte är fyra siffror, `slag` är något annat, källan inte är en
  sida i ett dokument i poolen för organet, eller rubriken, formuleringen
  eller statusen inte står på den sidan.
* **Samma mål** är samma organ, slag och rubrik, utan hänsyn till
  versaler. Ett mål som bytt rubrik står som två.
* **Sidan** är `<kommun>/<organ>/mal-och-direktiv.html`, länkad från
  organets sida. Överst en översikt med ett mål per rad och ett år per
  kolumn, där år utan dokument i poolen står som luckor; under den ett
  avsnitt per år. Ett litet skript väljer slag och visar ett mål i taget.
  Utan skript står allt.

### Consequences

* Good, eftersom varje rad går att kontrollera med ett klick, och bygget
  fäller en rad som inte står i källan.
* Good, eftersom ingen tolkningskod behöver underhållas.
* Bad, eftersom filen inte följer med när nya budgetar kommer; den skrivs
  på för hand.
* Bad, eftersom kontrollen prövar att texten står på sidan, inte att den
  är nämndens eget mål; den bedömningen är agentens och syns bara i
  källan.
* Bad, eftersom ett mål som bytt rubrik bryter spåret i översikten.
* Bad, eftersom ett dokument som flyttas i poolen (till exempel när
  ärendefiler slås ihop) fäller raderna tills de skrivs om.

### Confirmation

`tests/test_mal.py` prövar läsningen, kontrollerna och sidan med en
påhittad kommun, och att Kungsbackas fil går igenom kontrollen mot
poolen.

## Pros and Cons of the Options

### A – AI-agenten skriver en CSV med sidan som källa

* Good, eftersom läsningen klarar alla format, också tabellerna från 2018.
* Good, eftersom CSV:n går att granska rad för rad i en diff.
* Good, eftersom kontrollen mot sidan fångar felskrivningar och fel sida.
* Bad, eftersom någon måste läsa de nya dokumenten varje år.

### B – Kod tolkar målen

* Good, eftersom nya budgetar kommer med av sig själva.
* Bad, eftersom formen skiljer sig mellan åren och "Beslutats av Nämnd"
  bara finns sedan 2021; koden blir stor och gissar vem som beslutat.
* Bad, eftersom kommunfullmäktiges mål står i samma avsnitt och måste
  skiljas ut.

### C – Sammanfattning i egna ord

* Good, eftersom sidan blir kortare och lättare att läsa.
* Bad, eftersom en sammanfattning är en tolkning som inte går att pröva
  mot källan.

### D – Agenten kopplar ihop mål som bytt namn

* Good, eftersom spåren i översikten blir längre.
* Bad, eftersom kopplingen är en bedömning som källan sällan gör själv,
  och sidan skulle se säkrare ut än den är.

## More Information

Agenten föreslog i fas 0 en CSV för hand med källa och sida per rad,
nämndens mål och direktiv med kommunfullmäktiges mål som en länk, och
status ur uppföljningarna. Projektägaren svarade ja på CSV:n och
statusen, och att bara nämndens egna mål och direktiv ska med, inget
annat; därför står kommunfullmäktiges mål och direktiv inte heller som
länkar.

Kontrollen prövar texten efter att radbrytningar gjorts till mellanslag
och Markdown-escapningen tagits bort, så att en rad kan skrivas som den
läses i PDF:en.

Sidnumret i källan pekar på ankaret `sida-N` på dokumentets sida
(ADR-0023), så att länken öppnar rätt sida.

D prövas om översikten visar sig full av brutna spår, och då med en
kolumn som bara får fyllas när källan själv säger att målet fortsätter.
