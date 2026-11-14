---
status: proposed
date: 2026-11-14
decision-makers: projektägaren
consulted: AI-agenten
---

# Ett dokument får konverteras i högst 30 minuter och blir annars `ej-konverterad` med `fel: tidsgrans`

## Context and Problem Statement

Nattkörningen 2026-11-14 ägnade fem timmar åt ett enda dokument,
`Geotekniknisk utredning 2025-10-08.pdf` under `bygg-projekt`, och checkade
inte in något ([#274](https://github.com/moggleif/kommunhandlingar/issues/274)).
Dokumentet lades åt sidan vid budgetens hårda gräns (K11, ADR-0006), men
ett dokument som läggs åt sidan skrivs inte, så nästa körning tar det
först igen och fastnar på samma ställe. 223 kandidater väntade, och
arkivet fick aldrig tid.

Orsaken är en enda sida. Sida 94 är ett borrdiagram med 5,1 miljoner
tecken, 120 000 linjer och 82 000 rektanglar; bara att läsa in sidans
tecken tar pdfplumber omkring 2,5 minuter, och sidläsningen blir inte
klar på 20 minuter. Rapportens andra 120 sidor läses på under en minut.

Hur ska ett dokument som inte blir klart hindras från att stoppa resten,
och hur ska det registreras?

## Decision Drivers

* **Tomt är inte noll.** Det som inte gick att konvertera registreras som
  det, med en orsak.
* **Ett dokument får inte stoppa körningen,** varken i natt eller nästa
  natt.
* **Vanliga dokument ska inte drabbas.** Den längsta konverteringen i
  poolen hittills tog 19 minuter (KS-handlingar på 1 716 sidor, räknat
  från `hamtad` till `konverterad`), och 99 procent tar under 8 minuter.
* **Enkelt först.** Den hårda gränsen finns redan som ett larm
  (`SIGALRM`); ingen ny process, inget nytt tillstånd.

## Considered Options

* A – En egen tidsgräns per dokument, och det skrivs som `ej-konverterad`
  med `fel: tidsgrans`
* B – Dokumentet skrivs som `ej-konverterad` först när budgetens hårda
  gräns nås
* C – Dokumentet som lades åt sidan prövas sist i nästa körning
* D – Ett tak för antalet tecken per sida, så att bara den tunga sidan
  blir `ej-konverterad`

## Decision Outcome

Valt: A, eftersom det är det enda som både låter samma körning gå vidare
och hindrar att dokumentet prövas igen varje natt, för varje sorts
dokument som tar för lång tid, inte bara det här.

* **Gränsen** är 30 minuter för konverteringen, alltså efter hämtningen.
  Den räknas för varje dokument för sig; projektägaren valde 30 framför
  agentens förslag på 60.
* **När gränsen nås** avbryts konverteringen, och dokumentet skrivs som
  vilket `ej-konverterad` som helst: med sha256, `hamtad` och
  `konverterad`, `fel: tidsgrans` och utan sidor. Körningen tar nästa
  kandidat.
* **Nästa körning.** `ej-konverterad` är ett fullständigt dokument
  (ADR-0004), så med samma `kalla_url` är det oförändrat. Med
  omkonverteringen påslagen prövas det igen när poolens version är en
  annan (ADR-0019), och med ny `kalla_url` som en ny version (K9).
* **En omkonvertering som når gränsen** lämnar ett dokument som har text
  orört, när originalet är detsamma (samma sha256). Annars kunde en
  långsammare runner ta bort text som en tidigare version läste. Det
  registreras inte, så nästa körning försöker igen. En ny version med
  en annan sha256 skrivs som `fel: tidsgrans`, som varje ny version som
  inte går att konvertera (K9).
* **Budgetens hårda gräns går före.** Kommer den före dokumentets 30
  minuter läggs dokumentet åt sidan som förut (K11), utan att något
  skrivs. Annars ställs larmet om till den hårda gränsen när
  konverteringen är klar.
* **Ett larm.** Dokumentets gräns använder samma `SIGALRM` som den hårda
  gränsen, med ett eget undantag (`Dokumentgrans`) som konverteringen
  fångar, medan den hårda gränsens undantag går vidare till steg 2 som
  förut.

### Consequences

* Bra, eftersom ett dokument kostar högst 30 minuter en gång, och sedan
  inget förrän versionen höjs.
* Bra, eftersom orsaken syns i poolen och på webbplatsen som ett `fel`,
  som för en trasig fil.
* Dåligt, eftersom dokumentet får ingen text alls, också för de sidor
  som gick att läsa. Taket per sida (D) är ett eget issue,
  [#275](https://github.com/moggleif/kommunhandlingar/issues/275).
* Dåligt, eftersom gränsen beror på hur snabb maskinen är: samma dokument
  kan bli klart på en snabbare runner. Med 30 minuter mot 19 för det
  längsta hittills är marginalen liten men tydlig; ett vanligt dokument
  som når gränsen syns som `fel: tidsgrans` och kan prövas igen.
* Dåligt, eftersom larmet bara bryter mellan Pythons instruktioner: ett
  enskilt anrop i C som aldrig blir klart, eller en sida som tar slut på
  minnet, stoppas inte av gränsen. Taket i #275 hjälper mot det senare.
* Dåligt, eftersom en omkonvertering som når gränsen kostar 30 minuter
  varje natt tills versionen i dokumentet stämmer, vilket den inte gör
  förrän konverteringen blir snabbare. Sammanfattningen visar adressen,
  så att det syns. Inget dokument i poolen har hittills tagit mer än 19
  minuter.
* Dåligt, eftersom larmet kan gå i ögonblicket mellan konverteringens
  slut och att det stängs av; då blir ett färdigt dokument `tidsgrans`.
  Fönstret är mikrosekunder.
* Neutralt, eftersom gränsen gäller varje anrop till `konvertera`, också
  facit (K20), där inget dokument kommer nära den.
* Neutralt, eftersom en omkonvertering vid varje ny version prövar
  dokumentet igen och kostar 30 minuter av den natten.

### Confirmation

Tester i `tests/test_tidsbudget.py`: en konvertering som når dokumentets
gräns skrivs som `ej-konverterad` med `fel: tidsgrans` och klarar
datakontrollerna, nästa kandidat tas, nästa körning räknar dokumentet som
oförändrat, en omkonvertering vid gränsen lämnar texten orörd medan en ny
version skrivs över, och larmet för den hårda gränsen ställs tillbaka efter
konverteringen, minus tiden den tog också när den är kort, eller går före
när det kommer först.

## Pros and Cons of the Options

### A – En egen tidsgräns per dokument

* Bra, eftersom körningen går vidare samma natt.
* Bra, eftersom det gäller varje orsak till en lång konvertering.
* Dåligt, eftersom resultatet beror på maskinens fart.

### B – Registreras vid den hårda gränsen

* Bra, eftersom ingen ny gräns behövs.
* Dåligt, eftersom körningen ändå förlorar hela natten på dokumentet.
* Dåligt, eftersom skrivningen då måste ske efter den hårda gränsen, i
  tiden som är till för kontrollerna och pushen.

### C – Prövas sist nästa gång

* Bra, eftersom inget skrivs som kanske hade blivit klart.
* Dåligt, eftersom det kräver ett tillstånd mellan körningarna som inte
  finns: poolen är tillståndet (ADR-0004), och PDF:en raderas.
* Dåligt, eftersom dokumentet ändå tar resten av varje natt när det väl
  står på tur.

### D – Tak för tecken per sida

* Bra, eftersom resten av dokumentet blir text, och taket inte beror på
  maskinen.
* Dåligt, eftersom det bara fångar den här orsaken; en annan sorts tung
  sida stoppar körningen som förut.
* Dåligt, eftersom gränsen måste mätas mot poolens tyngsta vanliga sidor
  först. Det görs i #275, som ett tillägg till A.

## More Information

Agenten mätte rapporten sida för sida lokalt innan förslaget. 120 sidor
tog sammanlagt under en minut, sida 94 blev inte klar och tog så mycket
minne att processen fick avbrytas. Det talade för att problemet är en
sida, inte storleken på filen (28 MB), och att en gräns på filens storlek
inte hade hjälpt.

Agenten föreslog 60 minuter, tre gånger den längsta konverteringen i
poolen. Projektägaren valde 30: ett dokument som tar längre än en halv
timme är ovanligt nog att märkas, och en lägre gräns lämnar mer av natten
åt resten. Invändningen att ett stort men vanligt dokument kan nå gränsen
besvarades med att det då syns som `fel: tidsgrans` och kan prövas igen;
inget tas bort.

Alternativ C föll på att det kräver ett nytt tillstånd utanför poolen.
B föll på att natten ändå går förlorad. D tas som ett eget issue, eftersom
det förbättrar texten men inte ersätter skyddet.
