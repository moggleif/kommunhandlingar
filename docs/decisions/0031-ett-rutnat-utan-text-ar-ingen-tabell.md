---
status: accepted
date: 2026-10-12
decision-makers: projektägaren
consulted: AI-agenten
---

# Ett rutnät utan text är ingen tabell

## Context and Problem Statement

pdfplumber läser ett diagrams stödlinjer, en ritnings ramar eller en
ikons rutor som en tabell med linjer. Står diagrammets etiketter i
rutorna kan de bli en CSV med tal som inte är data, och ett rutnät utan
text blir en CSV med bara tomma celler. Rutnätet räknas dessutom som
tabell när sidan prövas för figurer, så det som står i det räknas inte. Hur känns
ett diagram igen så att det inte blir en CSV
([#100](https://github.com/moggleif/kommunhandlingar/issues/100))?

## Decision Drivers

* Data ska vara rätt eller märkt: tal ur ett diagram ska inte stå som en
  tabell.
* En riktig tabell, också ett formulär med tomma eller färgade celler,
  ska inte förloras.

## Considered Options

* A – Ett rutnät utan text är ingen tabell
* B – Ett rutnät med figurinnehåll (staplar, kurvor) och få ifyllda
  celler är ett diagram
* C – Som i dag

## Decision Outcome

Valt: A, eftersom det är det enda mönster stickprovet visade, och regeln
inte kan förlora data. En tabell med linjer ska ha minst ett ord inom
sin yta. Ett rutnät utan text blir ingen tabell, och dess linjer och
ytor räknas när sidan prövas för figurer.

Poolens version höjs till 0.8.2. Poolen rättas när den konverteras om
([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

### Consequences

* Bra, eftersom diagrammens och ritningarnas tomma rutnät inte längre
  blir CSV:er. Poolen har 139 CSV:er med bara tomma celler, de flesta
  från diagram och ritningar och några från tomma formulär.
* Bra, eftersom regeln är en rad och inte kan ta bort en cell med text.
* Dåligt, eftersom ett diagram vars etiketter står inne i rutorna
  fortfarande kan bli en CSV, som säker tabell eller genom delningen
  (ADR-0028). Bara etiketter som står över rutnätets linjer stoppas.
  Stickprovet hittade inget sådant diagram, och frågan står kvar i
  [#100](https://github.com/moggleif/kommunhandlingar/issues/100).
* Neutralt, eftersom CSV:erna på en sida numreras om när poolen
  konverteras om, och en sidas första eller sista tabell kan bli en
  annan, så att en tabell över två sidor kan slås ihop på ett annat
  sätt ([ADR-0024](0024-tabeller-over-flera-sidor-slas-ihop.md)).
  Stickprovet jämförde inte det.
* Dåligt, eftersom ett tomt formulär med linjer inte heller blir en CSV.
  Det har ingen data att förlora.

### Confirmation

`tests/test_celler.py` prövar ett rutnät med och utan text. Facit
([ADR-0025](0025-facit-for-konverteringen.md)) ska inte bli sämre.

## Pros and Cons of the Options

### A – Ett rutnät utan text är ingen tabell

* Bra, eftersom inget med text försvinner.
* Dåligt, eftersom ett diagram med etiketter i rutorna inte fångas.

### B – Figurinnehåll och få ifyllda celler

* Bra, eftersom ett diagram med etiketter i rutorna skulle fångas.
* Dåligt, eftersom riktiga tabeller har färgade tomma celler, som
  statusrutor och skuggade fält. I stickprovet föll en tabell över
  verksamheternas volym och kostnad och en tabell över lärares behörighet
  bort, med mindre än en fjärdedel av cellerna ifyllda och fler än åtta
  fyllda ytor.

### C – Som i dag

* Bra, eftersom inget ändras.
* Dåligt, eftersom tomma rutnät blir CSV:er och döljer diagram för
  figurprövningen.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet** kom ur stickprovet för #95, där ett stapeldiagrams
   etiketter blev en delad tabell. Det rättades i PR #101, eftersom
   etiketterna stod över rutnätets linjer. Projektägaren bad att
   följd-issues görs och mergas.
2. **Stickprovet (AI-agenten)** tog tolv dokument ur poolen med sidor
   som både har en figur och en CSV, 77 sidor. Inget diagram gav en CSV
   med tal. Diagrammen och ritningarna gav rutnät utan text, eller med
   en adressruta eller ett ändringsblock. Med regel A försvann åtta
   tomma tabeller. Ingen sida fick en annan kvalitet eller figurmärkning
   (alla hade redan en figur), och stickproven för #60 och #95 är
   oförändrade.
3. **Regel B** prövades på samma stickprov och på stickproven för #60
   och #95. Den fångade ritningarna, men också två riktiga tabeller.

4. **Granskningen (fas 6)** visade att ADR:n först beskrev luckan för
   diagram med etiketter i rutorna som mindre än den är, och att
   effekten på figurprövningen inte är mätt. Därför löser ändringen bara
   en del av #100, som står kvar öppet.

Ompröva beslutet när ett diagram med tal i rutorna hittas i poolen.
