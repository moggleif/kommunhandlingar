---
status: proposed
date: 2026-10-08
decision-makers: projektägaren
consulted: AI-agenten
---

# Ett dokument från en annan version av poolen hämtas igen och konverteras om, efter alla andra kandidater

## Context and Problem Statement

När konverteringen ändras gäller det bara dokument som hämtas efteråt.
De 1 342 dokument som fanns i poolen 2026-10-08 är lästa av version
0.1.0. De saknar regeln för tabeller utan lodräta linjer (ADR-0016) och
har `figurer: null` (ADR-0017). PDF:en raderas efter konverteringen
(ADR-0001), och enligt ADR-0004 hämtas ett dokument med samma källnyckel
och adress aldrig igen
([#44](https://github.com/moggleif/kommunhandlingar/issues/44)).

Vilka dokument ska konverteras om, när ryms det i nattkörningen, och
var kommer PDF:en ifrån?

## Decision Drivers

* **Bara text lagras** (ADR-0001). Ingen PDF finns kvar mellan
  körningarna.
* **Nya dokument går först.** En omkonvertering förbättrar det som redan
  finns; ett dokument som saknas är värre.
* **Artig hämtning** (K10). En omhämtning är ett anrop till med 5
  sekunders avstånd; tiden går till konverteringen, ungefär 40 sekunder
  per dokument i nattkörning 2.
* **Enkelt först.** Ingen regel per ändring, inget nytt tillstånd, inget
  nytt konto.

## Considered Options

* A – Versionen i `pipeline` styr; dokumentet hämtas igen och
  konverteras om efter alla andra kandidater
* B – Bara dokument som en viss ändring berör, till exempel sidor som är
  `tabell-osaker`
* C – PDF:erna mellanlagras utanför repot, i en molntjänst eller i
  Actions cache, och omkonverteringen läser dem därifrån
* D – Ett eget arbetsflöde för omkonverteringen, skilt från
  nattkörningen

## Decision Outcome

Valt: A, eftersom versionen redan står i varje dokument och redan höjs
när konverteringen ändrar vad den skriver. Det behövs ingen ny signal,
ingen lagring och inget nytt arbetsflöde.

* **Signalen.** Ett fullständigt dokument, alltså inte `ej-hamtad`, vars
  `pipeline` börjar med en annan version av poolen än den som körs, och
  som har en kandidat med samma källnyckel och adress, hämtas igen.
  Versionerna jämförs som lika eller olika, inte som äldre eller nyare;
  en nyare version i poolen än i koden kan bara uppstå om en äldre
  utcheckning körs, och då är det den som gäller.
* **Ordningen.** Sådana kandidater tas efter alla andra, i K13:s ordning
  sinsemellan. Den mjuka gränsen i K11 avgör hur många som hinns med;
  resten väntar på nästa natt. Wayback (#51) körs efter de levande
  källornas kandidater, och därmed också efter deras omkonvertering.
* **Samma sha256** ger en ny konvertering på samma sökväg, med text,
  tabeller och alla fält från den nya versionen, och `hamtad` och
  `konverterad` från den här körningen. Sammanfattningen räknar det som
  "konverterad om".
* **En annan sha256** är en ny version enligt K9, som förut.
* **Filen går inte att hämta.** Den gamla `.md` står orörd, som vid varje
  misslyckat försök (ADR-0004), och nästa körning försöker igen.

### Consequences

* Bra, eftersom varje framtida höjning av versionen konverterar om hela
  poolen utan ny kod.
* Bra, eftersom en omhämtning prövar att originalet är detsamma; ett
  utbytt original under samma adress, som ADR-0004 inte upptäcker,
  blir då en ny version.
* Bra, eftersom omkonverteringen aldrig tränger undan ett nytt dokument.
* Dåligt, eftersom hela poolen hämtas och konverteras igen vid varje
  höjning. 1 342 dokument är ungefär 15 timmars körning, tre nätter
  efter de nya dokumenten, och tiden växer med poolen.
* Dåligt, eftersom ett original som försvunnit försöks igen varje natt
  tills versionen i dokumentet stämmer, vilket den aldrig gör. Det kostar
  ett anrop per natt och syns i sammanfattningen.
* Dåligt, eftersom ett dokument som ingen kandidat längre pekar på (K12)
  inte konverteras om.
* Dåligt, eftersom en omkonvertering tar bort dokumentets tolkade figurer
  (ADR-0017). 2026-10-08 är inget dokument tolkat.
* Neutralt, eftersom en höjning som bara ändrar ett fält också
  konverterar om allt. Den som höjer versionen avgör.

### Confirmation

Tester i `tests/test_hamta.py`:

* ett dokument med en annan version och samma adress hämtas och
  konverteras om, med den nya versionen i `pipeline`, och räknas som
  "konverterad om",
* ett dokument med samma version och samma adress hämtas inte,
* ett misslyckat försök att hämta det skriver inte över det,
* ett dokument med en annan version under en ny adress och samma
  sha256 konverteras om, i stället för att bara få en ny adress,
* omkonverteringens kandidater tas efter de andra, och sinsemellan i
  listans ordning.

## Pros and Cons of the Options

### A – Versionen i `pipeline` styr

* Bra, eftersom signalen redan finns i varje dokument.
* Bra, eftersom koden blir ett villkor till i steg 2 och en sortering.
* Dåligt, eftersom allt konverteras om, också dokument som ändringen inte
  rör.

### B – Bara dokument som en viss ändring berör

* Bra, eftersom färre dokument hämtas.
* Dåligt, eftersom varje ändring behöver en egen regel för vad den rör,
  och #17 rör alla dokument ändå: `figurer` saknas överallt.
* Dåligt, eftersom en fel regel lämnar dokument kvar i en gammal version
  utan att det syns.

### C – PDF:erna mellanlagras utanför repot

* Bra, eftersom källan inte belastas igen, och ett original som
  försvunnit ur källan går att konvertera om.
* Dåligt, eftersom det bryter ADR-0001: PDF:erna finns kvar.
* Dåligt, eftersom en molntjänst kräver konto, hemlighet och kod, och
  Actions cache rymmer 10 GB och rensas efter en vecka utan användning,
  så den räcker inte som lager.
* Dåligt, eftersom hämtningen inte är det som tar tid.

### D – Ett eget arbetsflöde för omkonverteringen

* Bra, eftersom den inte tar tid från nattkörningen.
* Dåligt, eftersom två arbetsflöden skriver i samma filer och ger två
  grenar att merga varje dag.
* Dåligt, eftersom steg 2 ändå behöver regeln; arbetsflödet blir en kopia
  av nattkörningen med en flagga.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Frågan (projektägaren).** Måste omkonverteringen vara klar före
   nästa nattkörning, och borde PDF:erna ligga i en tillfällig lagring,
   till exempel en molntjänst, efter natten?
2. **Läget (agenten).** Nattkörning 2 tog hela budgeten: 420
   konverterade, 921 oförändrade och 321 som väntade. De 321 får
   `figurer` direkt, eftersom nattkörningen redan kör version 0.3.0.
   Hämtningen tar 5 sekunder per fil, konverteringen och OCR resten.
3. **Agentens rekommendation.** Omkonverteringen behövs inte till nästa
   natt. PDF:erna hämtas igen från källan, eftersom en lagring strider
   mot ADR-0001 och inte sparar den tid som räknas. Versionen i
   `pipeline` styr, och omkonverteringen går efter de nya dokumenten och
   före Wayback, som ägaren vill ha med lägst prioritet.
4. **Beslutet (projektägaren).** Ja på alla tre: versionen styr,
   ordningen nya, omkonvertering, Wayback, och omhämtning utan lagring.
5. **Omprövas** när poolen är så stor att en omkonvertering tar mer än
   en vecka av nätter, eller om källorna börjar ta bort gamla original.
