---
status: proposed
date: 2026-10-10
decision-makers: projektägaren
consulted: AI-agenten
---

# En tabell som fortsätter på nästa sida slås ihop vid konverteringen när ingenting står emellan, och filnamnet anger sidorna

## Context and Problem Statement

Konverteringen läser tabellerna en sida i taget. En tabell som går över
fyra sidor blir fyra CSV:er, och i `.md` och på webbplatsen fyra tabeller.
Markdown kräver ett tabellhuvud, så första raden i varje fortsättning
blir ett tabellhuvud, också när den är en vanlig rad eller halva rad som
brutits vid sidslutet
([#62](https://github.com/moggleif/kommunhandlingar/issues/62)).

Ett stickprov i poolen 2026-10-10 hittade 9 707 sidskarvar där en sida
slutar med en tabell och nästa börjar med en; 8 405 hade samma antal
kolumner, i 921 av 1 031 dokument med tabeller. I fem PDF:er där
tabellernas läge mättes uppfyllde 24 av 56 skarvar en sträng regel.
Delegationsordningar, ärendelistor i kallelser och taxor går nästan alltid
över flera sidor.

När räknas två tabeller som en, var slås de ihop, och hur syns det?

## Decision Drivers

* **Hellre märka än gissa** (`AGENTS.md`). Två tabeller som inte säkert
  hör ihop ska inte bli en.
* **Tal och tabeller ska vara rätt.** Sammanslagningen får inte ändra en
  cell.
* **Ett faktum på ett ställe** (ADR-0009). Sidnumret står i filnamnet.
* **Bara text lagras** (ADR-0001). Tabellernas läge på sidan finns bara
  medan PDF:en är öppen.
* **Maskningen** av personuppgifter (ADR-0022) får inte gå sönder.

## Considered Options

* A – Vid konverteringen, efter läge: samma kolumner och bara sidhuvud
  och sidfot emellan
* B – I efterhand ur CSV:erna: samma antal kolumner och samma första rad
* C – Ingen sammanslagning; webbplatsen visar fortsättningarna utan
  tabellhuvud

## Decision Outcome

Valt alternativ: "A – Vid konverteringen, efter läge", eftersom läget är
det enda som skiljer en fortsättning från nästa tabell med samma
uppställning, och det bara finns medan PDF:en är öppen.

* **Regeln** står i
  [03-ARKITEKTUR.md](../03-ARKITEKTUR.md#tabeller-över-flera-sidor): båda
  sidorna lästa ur textlagret, samma kolumngränser inom 3 punkter, och
  bara sidhuvud och sidfot emellan. Sidhuvud och sidfot är rader som,
  utan sina siffror, står på samma höjd på minst tre av dokumentets
  sidor.
* **En upprepad rubrik** tas bort ur fortsättningen när den är exakt
  lika med tabellens första rad.
* **En bruten rad** står kvar som två rader. Att foga ihop cellerna vore
  att gissa var raden bröts.
* **Filnamnet** är `<sida>-<sista sida>-<nr>.csv`, till exempel
  `9-12-1.csv`. En tabell på en sida heter som förut.
* **Poolen** rättas när den konverteras om
  ([#84](https://github.com/moggleif/kommunhandlingar/issues/84),
  ADR-0019). Versionen höjs till 0.6.0.

### Consequences

* Bra, eftersom en tabell blir en CSV och en tabell i texten, med sitt
  riktiga tabellhuvud.
* Bra, eftersom sidorna syns i filnamnet och sammanslagningen kan
  kontrolleras mot PDF:en utan att något annat läses.
* Bra, eftersom ingen cell ändras, så maskningen och talen står som förut.
* Dåligt, eftersom en tabell med en fotnot eller en rubrik mellan
  delarna inte slås ihop, fast den hör ihop.
* Dåligt, eftersom en rad som brutits vid sidslutet står kvar som två
  rader.
* Dåligt, eftersom ett dokument på två sidor inte har något sidhuvud som
  känns igen, och en numrerad rubrik på samma höjd på tre sidor räknas
  som sidhuvud.
* Dåligt, eftersom dokumenten i poolen har kvar en tabell per sida tills
  de konverterats om.
* Neutralt, eftersom filnamnen nu har två former, med två eller tre tal.

### Confirmation

Tester mot en PDF i `tests/fixtures/pdf/` med en tabell över tre sidor,
med sidhuvud, sidfot och upprepad rubrik, och med tabeller som inte ska
slås ihop: en rubrik emellan, en rubrik som bara skiljer i en siffra,
ett datum under tabellen och samma yttermått med andra kolumner.
Datakontrollen prövar namnet och spannet.

## Pros and Cons of the Options

### A – Vid konverteringen, efter läge

* Bra, eftersom läget skiljer en fortsättning från en ny tabell med
  samma uppställning, som två avsnitt i en bilaga med en fotnot emellan.
* Bra, eftersom det gäller både tabeller med och utan lodräta linjer.
* Dåligt, eftersom poolen måste konverteras om för att rättas.

### B – I efterhand ur CSV:erna

* Bra, eftersom poolen kan rättas utan att PDF:erna hämtas igen.
* Dåligt, eftersom samma antal kolumner inte räcker: i stickprovet var
  två olika tabeller med samma uppställning efter varandra vanligt.
* Dåligt, eftersom många fortsättningar saknar upprepad rubrik, och de
  skulle inte hittas.

### C – Ingen sammanslagning

* Bra, eftersom ingenting kan slås ihop fel.
* Dåligt, eftersom en tabell blir många CSV:er, och den som analyserar
  måste foga ihop dem själv, utan att veta vilka som hör ihop.
* Dåligt, eftersom det bara döljer problemet på webbplatsen.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet (projektägaren)** bad om ett stickprov, och om problemet var
   vanligt, att delar som hör ihop slås samman med sidorna angivna, och
   att det som inte säkert hör ihop lämnas.
2. **Stickprovet (agenten)** visade att det är vanligt, och att samma
   antal kolumner och en upprepad rubrik inte räcker som tecken. Med
   läget gick det att skilja dem åt; de skarvar som regeln avvisade hade
   löptext, en fotnot eller en underskrift emellan. Sidhuvudet räknas inte
   som text emellan, eftersom det står på varje sida.
3. **Agentens rekommendationer**, som projektägaren sa ja till: ta bort
   en upprepad rubrik bara när den är exakt lika, skriv sidorna i
   filnamnet, och konvertera om poolen som ett eget steg (#84).
4. **Granskningen (agenten, fas 6)** visade att den första regeln slog
   ihop för mycket. Den räknade en rad som sidhuvud om den, utan
   siffror, stod var som helst på grannsidan, så `Avsnitt 1` och
   `Avsnitt 2` blev sidhuvud, och en rad utan bokstäver, som ett datum,
   räknades som sidnummer. Den jämförde också bara tabellernas
   yttermått. Regeln skärptes: raden ska stå på samma höjd på minst tre
   sidor, och varje kolumngräns ska stämma.
5. **Utanför:** en rad som brutits vid sidslutet fogas inte ihop, och
   tabeller på OCR-sidor slås inte ihop.
6. **Omprövas** om det visar sig vanligt att en tabell har en rubrik
   eller fotnot mellan delarna.
