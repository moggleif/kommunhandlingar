---
status: accepted
date: 2026-10-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Körningen sker varje natt i GitHub Actions och checkar in data direkt till `main` efter datakontrollerna

## Context and Problem Statement

Poolen ska fyllas på regelbundet, och historiken – 10–30 GB PDF per kommun
(ADR-0001) – ska hämtas en gång. Samtidigt gäller "Gren, inte `main`" och
PR-flödet i `AGENTS.md` för all ändring
([#5](https://github.com/moggleif/kommunhandlingar/issues/5)).
ADR-0004 lämnade öppet hur bara färdiga körningar checkas in.

Var sker den schemalagda körningen, hur når ny data `main`, och vilka
kontroller passerar datat innan det tas in?

## Decision Drivers

* **Enkelhet.** Så få konton, tjänster och hemligheter som möjligt
  (ADR-0001).
* **Gratis och öppen källkod.** Inga betalda tjänster.
* **Rätt före snabbt.** Ett fel i datat ska stoppas av en kontroll, inte
  upptäckas i efterhand. Historiken får ta den tid den tar.
* **Bara färdiga körningar.** Inget halvfärdigt får nå `main` (K8, K11).
* **Artig hämtning** (K10). Historiken ska inte hämtas fortare än
  källorna tål.
* **Spårbarhet.** Det ska gå att se vad varje körning ändrade.

## Considered Options

* A – GitHub Actions varje natt; commit direkt till `main` efter
  datakontrollerna
* B – GitHub Actions varje natt; en PR per körning som mergas automatiskt
* C – GitHub Actions varje natt; en PR per körning som en människa mergar
* D – GitHub Actions varje natt; datat på en egen gren som aldrig mergas
* E – En egen server med cron
* F – Manuell körning, lokalt eller i en agentsession

## Decision Outcome

Valt alternativ: "A – GitHub Actions varje natt, commit direkt till `main`
efter datakontrollerna", eftersom det är det enda som ger regelbundna
körningar utan nya konton eller hemligheter, och kontrollerna gör det en
människas granskning av en nattlig körning inte skulle göra: läser varje
fil.

Beslutet i korthet. Beteendet står i K11 och hur körningen går till i
[03-ARKITEKTUR.md](../03-ARKITEKTUR.md), under "Körning och incheckning".

* **Pipelinen är ett vanligt kommando** som inte vet var det körs. Actions
  startar det varje natt och för hand. En egen server kan starta samma
  kommando ([#18](https://github.com/moggleif/kommunhandlingar/issues/18)).
* **Varje körning börjar från en ren utcheckning av `main`,** så det som
  en avbruten körning lämnat efter sig, till exempel tabeller bredvid en
  gammal `.md` (ADR-0004), aldrig finns kvar till nästa körning.
* **Tidsbudget i stället för en historisk körning.** Varje körning
  hämtar så länge budgeten räcker och checkar in det som är klart. Nästa
  natt fortsätter där den slutade (K8). Historiken fylls natt för natt
  tills den är ikapp; därefter tar varje natt bara det nya.
* **Ett dokument som inte hinner bli klart lämnas till nästa körning.**
  Budgeten har en hård gräns före Actions gräns på 6 timmar. Där läggs
  det pågående dokumentet åt sidan: allt det skrivit tas bort eller
  återställs till `main`, det nämns i jobbets sammanfattning, och resten
  checkas in. Ett långt inskannat dokument kan därmed inte kasta
  hela nattens arbete.
* **Datakontrollerna körs före push**, och bara om de går igenom blir
  körningen en commit direkt till `main`, bara under `data/`. Körningen
  är det enda som skriver direkt till `main`; kod och dokument går via
  gren och PR som förut.
* **Ett fel stoppar körningen utan att något checkas in.** Ett oväntat
  fel i pipelinen, att jobbet dödas eller att runnern försvinner ger
  samma sak: ingenting pushas och körningen syns som misslyckad. Ett
  dokument som inte går att hämta eller konvertera är inget fel i den
  meningen; det skrivs med sin kvalitet (K6).

### Consequences

* Bra, eftersom det inte kostar något och inte kräver något konto eller
  någon hemlighet utöver repot: Actions egen token får skriva till repot.
* Bra, eftersom git-historiken visar vad varje körning ändrade, en commit
  per natt.
* Bra, eftersom ingenting halvfärdigt når `main`, och ADR-0004:s
  kvarlämnade tabeller inte kan checkas in.
* Bra, eftersom samma kommando kan köras någon annanstans när Actions inte
  räcker (#18).
* Dåligt, eftersom körningen är ett undantag från "Gren, inte `main`". Ett
  fel i pipelinen som kontrollerna inte fångar hamnar på `main` och rättas
  med en revert och en ny körning.
* Dåligt, eftersom Actions schema kan försenas, och ett jobb aldrig får ta
  mer än 6 timmar. Historiken tar flera nätter, och ett dokument som
  ensamt tar längre än budgeten blir aldrig klart. Med ADR-0005:s
  mätning av det valda alternativet, ungefär 3 sekunder per inskannad
  sida, är det ett inskannat dokument på flera tusen sidor; den största
  PDF:en som setts hittills har 228 sidor.
* Dåligt, eftersom ett fel i pipelinen kastar hela nattens arbete, och
  ett dokument som alltid får pipelinen att krascha stoppar poolen tills
  felet är rättat. Det är avsiktligt: hellre stanna än checka in något
  ingen vet är rätt, och felet syns som en röd körning.
* Dåligt, eftersom runnerns adress ligger hos en molnleverantör som en
  kommun skulle kunna blockera.
* Dåligt, eftersom GitHub stänger av schemat i ett publikt repo efter 60
  dagar utan aktivitet i repot, till exempel när historiken är ikapp och
  källorna står still. Det måste då slås på igen för hand.
* Dåligt, eftersom ett skydd av `main` som kräver PR för varje ändring
  inte går att slå på utan att körningen undantas, och om Actions egen
  token inte kan undantas behövs just den hemlighet som beslutet
  undviker.
* Neutralt, eftersom borttagning av dokument (#7) ska vara beslutad innan
  den första körningen checkar in data.

### Confirmation

* `AGENTS.md` säger att körningen är det enda som skriver direkt till
  `main`, och bara under `data/`.
* När workflow-filen skrivs, tillsammans med pipelinen: den har ett schema
  och `workflow_dispatch`, en `concurrency`-grupp utan
  `cancel-in-progress`, `contents: write` bara i det jobbet, och kör
  datakontrollerna före push.
* Ett test för varje datakontroll, för att inget nytt dokument startar
  när budgeten är slut, för att det pågående dokumentet blir färdigt när
  det hinner, och för att ett dokument som läggs åt sidan vid den hårda
  gränsen inte lämnar några filer kvar, så att kontrollerna går igenom.

## Pros and Cons of the Options

### A – GitHub Actions varje natt; commit direkt till `main` efter datakontrollerna

* Bra, eftersom Actions är gratis och utan minutgräns för publika repon.
* Bra, eftersom inga nya konton eller hemligheter behövs.
* Bra, eftersom en commit per körning ger en läsbar historik.
* Dåligt, eftersom det är ett undantag från "Gren, inte `main`".
* Dåligt, eftersom ett jobb får ta högst 6 timmar.

### B – GitHub Actions varje natt; en PR per körning som mergas automatiskt

* Bra, eftersom "Gren, inte `main`" gäller utan undantag.
* Bra, eftersom varje körning får en sida med diff och kontroller.
* Dåligt, eftersom en PR som skapas med Actions egen token inte startar
  några workflows av sig själv. Antingen behövs en personlig token eller
  en GitHub App, alltså en hemlighet till att sköta, eller så kör jobbet
  kontrollerna själv och mergar via API:t, och då är det A med en
  PR runt.
* Dåligt, eftersom en PR per natt är brus som ingen läser.

### C – GitHub Actions varje natt; en PR per körning som en människa mergar

* Bra, eftersom en människa ser varje körning.
* Dåligt, eftersom ingen läser tusentals filer; granskningen blir en
  stämpel.
* Dåligt, eftersom PR:erna staplas på varandra under den historiska
  hämtningen och krockar.
* Dåligt, eftersom poolen står still när ingen har tid.

### D – GitHub Actions varje natt; datat på en egen gren som aldrig mergas

* Bra, eftersom `main` bara innehåller kod och dokument.
* Dåligt, eftersom det blir två sanningar: koden på en gren, datat på en
  annan.
* Dåligt, eftersom pipelinen läser poolen som sitt tillstånd (ADR-0004)
  och då måste läsa en annan gren än den kör ifrån.
* Dåligt, eftersom det blir svårare att söka i och länka till datat.

### E – En egen server med cron

* Bra, eftersom det inte finns någon tidsgräns per körning.
* Dåligt, eftersom den kostar eller måste skötas, och är ett konto till.
* Dåligt, eftersom körningen inte syns där koden finns.

### F – Manuell körning, lokalt eller i en agentsession

* Bra, eftersom det inte kräver någon infrastruktur.
* Dåligt, eftersom poolen bara fylls på när någon kommer ihåg det.
* Dåligt, eftersom körningarna inte blir lika varandra.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Två frågor i en.** Issuet frågade både var körningen sker och hur
   datat checkas in. Agenten delade upp det i fas 0: var (Actions, egen
   server, egen runner i Actions, manuellt), intag (direkt till `main`,
   PR med automerge, PR som en människa mergar, datagren) och kontroller.
   Alternativen ovan är de kombinationer som var värda att väga.
2. **Egen runner i Actions** föll redan i fas 0: GitHub avråder från egna
   runners i publika repon, eftersom en PR från vem som helst kan köra kod
   på dem.
3. **Varför inte en PR per körning?** "Gren, inte `main`" finns för att en
   människa eller en granskare ska se en ändring innan den tas in. För en
   nattlig körning med hundratals filer gör ingen det; det som faktiskt
   granskar datat är kontrollerna. B ger samma kontroller, men Actions
   egen token startar inga workflows på en PR den själv skapat, så B
   kräver antingen en hemlighet eller att jobbet kontrollerar och mergar
   själv – och då tillför PR:en bara brus. Agenten rekommenderade A och
   att undantaget skrivs ut i `AGENTS.md`, så att regeln och
   verkligheten säger samma sak.
4. **Den historiska hämtningen.** Issuet frågade hur länge en historisk
   hämtning får ta. Agenten föreslog ingen egen körning för historiken:
   K8 gör redan varje körning avbrytbar, så en tidsbudget räcker. Med
   artigt avstånd mellan anropen och OCR på de skannade sidorna tar
   historiken några nätter. Hur många vet vi när adaptrarna körs mot
   källorna (#10).
5. **Ägarens val.** Ägaren godkände 2026-10-07 alla fyra förslagen:
   Actions, direkt till `main` efter kontrollerna, en körning per natt med
   tidsbudget och manuell start, och att workflow-filen skrivs med
   pipelinen. Ägaren tillade att en egen server är på väg och bad om ett
   eget issue för att kunna köra där; det blev #18. Därför säger beslutet
   att pipelinen är ett kommando som inte vet var det körs.

### Vad som inte avgörs här

* Workflow-filen och datakontrollernas kod – med pipelinen.
* Hur en egen server kör och får skriva – #18.
* Borttagning av dokument innan den första datan checkas in – #7.
* Var front matter-schemat bor – #9. Det här beslutet säger bara att
  det kontrolleras.
* Hur Tesseract och språkmodellen installeras i körningen med den version
  som `pipeline` anger (ADR-0005) – med pipelinen.

### Granskningen

Den oberoende granskningen (fas 6) fann en motsägelse: kontrollerna
sades köras i CI på varje PR, men en av dem – att bara `data/` ändrats –
kan inte gå igenom på en PR med kod. Kontrollerna delades i de som gäller
datat och de som bara gäller körningen. Granskningen visade också att ett
fel i pipelinen mitt i natten inte var bestämt; det stoppar nu körningen
utan att något checkas in. Avstängt schema efter 60 dagar och skydd av
`main` lades till bland konsekvenserna, och skälet mot B skrevs mindre
kategoriskt. En gräns för filstorlek ströks, eftersom inget krav
motiverade den.

Den andra granskningen visade att ett långt inskannat dokument som
startar strax före budgetens slut kunde få jobbet dödat vid 6 timmar,
natt efter natt, utan att något checkades in. Budgeten fick därför en
hård gräns där det pågående dokumentet avbryts och lämnas till nästa
körning. Detaljerna som stod både här och i arkitekturen står nu bara i
arkitekturen.

Den tredje granskningen fann inget blockerande. Den visade att ett
dokument som läggs åt sidan måste ta bort sina ospårade filer, annars
faller kontrollerna natt efter natt, och att sekundtalet per sida var
hämtat från ett bortvalt alternativ. Båda rättades, och dokumentet som
läggs åt sidan nämns i jobbets sammanfattning.

### GitHubs gränser

Beslutet bygger på GitHubs villkor som de stod 2026-10-07. De kan
ändras, och då ska beslutet läsas om:

* Ett jobb på GitHubs runners får ta högst 6 timmar –
  [Actions limits](https://docs.github.com/en/actions/reference/limits).
* Ett schema i ett publikt repo stängs av efter 60 dagar utan aktivitet –
  [Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), under `schedule`.
* En push eller PR med Actions egen token startar inga nya workflows –
  [GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token).
* Standardrunners är gratis för publika repon –
  [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

### När beslutet bör omprövas

Om ett dokument inte hinner bli klart inom budgeten, om Actions inte
räcker – jobbgränsen, schemat eller en kommun som blockerar runnern –,
när en egen server finns (#18), eller om `main` behöver ett skydd som
körningen inte kan undantas från. Om
kontrollerna visar sig släppa igenom fel som en människa hade sett,
bör en PR per körning (B eller C) prövas igen.
