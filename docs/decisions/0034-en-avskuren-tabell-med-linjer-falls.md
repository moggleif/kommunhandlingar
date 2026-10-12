---
status: proposed
date: 2026-10-12
decision-makers: projektägaren
consulted: AI-agenten
---

# En tabell med linjer som bara ramar in en del av sig själv fälls

## Context and Problem Statement

Facit ([ADR-0025](0025-facit-for-konverteringen.md)) hittade en tabell
som läses som en del av sig själv
([#90](https://github.com/moggleif/kommunhandlingar/issues/90)). I
trafikförsörjningsprogrammet har tabellen över stråken lodräta linjer
bara mellan kolumnerna, inte i kanterna, och ingen linje under den sista
raden:

```text
Stråk           │ Mån-fre │ Lör  │ Sön
Mycket starka   │   24    │  12  │  8
Starka          │   18    │  12  │  8
Lokalt mycket … │   54    │  36  │  32
Lokalt starkt     28        20      12
```

pdfplumber hittar bara rutnätet mellan linjerna. Det blev en säker
tabell med tre rader tal utan etiketter (`24,12`, `18,12`, `54,36`).
Resten av tabellen stod i texten, och sidan märktes `ok`. Hur känns det
igen?

## Decision Drivers

* Data ska vara rätt eller märkt: tal utan sina etiketter får inte bli
  en CSV.
* En tabell bredvid en annan tabell, eller bredvid löptext, ska inte
  fällas i onödan.
* Regeln ska vara kort.

## Considered Options

* A – Ett tal utanför tabellen på samma höjd fäller den
* B – Fyllda cellrutor räknas som linjer, så att hela rutnätet hittas
* C – Som i dag

## Decision Outcome

Valt: A, eftersom ett tal på en rads höjd utanför tabellen visar att
raden fortsätter förbi linjerna. Orden utanför de tabeller med linjer
som hittats delas i fält som i tabellerna utan lodräta linjer, med ett
tvetydigt mellanrum räknat som en gräns. Står ett fält som är ett tal,
men inte ett årtal, på en rad vars mittpunkt ligger mellan tabellens
över- och underkant, till vänster eller till höger om den, är tabellen
avskuren. Den fälls och delas inte. Dess ord prövas som en tabell utan
lodräta linjer, och siffrorna i den som inte lästs märker sidan
`tabell-osaker`, som för andra fällda tabeller. Regeln står i
`konvertering/avskurna.py`.

Poolens version höjs till 0.8.4. Poolen rättas när den konverteras om
([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

### Consequences

* Bra, eftersom tabellen i #90 inte längre blir tal utan etiketter. I
  facit går `fel_rader` från 3 till 0, `saknade` från 1 till 0 och
  `osakra` från 2 till 3.
* Bra, eftersom ett stickprov på tio handlingar ur poolen, omkring
  1 900 sidor ur textlagret, fäller två tabeller till, båda med samma
  fel: tal utan etiketter, och en kolumn utanför linjerna.
* Dåligt, eftersom tabellen inte blir CSV, bara märkt. Den blir CSV bara
  när den går att läsa som en tabell utan lodräta linjer, och i #90 står
  talen i den sista kolumnen inte i linje.
* Dåligt, eftersom ett ensamt tal i en marginalanteckning bredvid en
  tabell, som ett fotnotsnummer med stort mellanrum, fäller en tabell
  som lästs rätt. Ett tal i en mening fäller den inte.
* Dåligt, eftersom talen i en tabell utan lodräta linjer bredvid
  tabellen fäller den: den tabellen läses först efteråt. I stickprovet
  förekom det inte.

### Confirmation

`tests/test_avskurna.py` prövar regeln på påhittade ord och på sidan
med tabellen i #90. Bland testfixturernas sidor fälls bara den tabellen.
Facit ska inte bli sämre.

## Pros and Cons of the Options

### A – Ett tal utanför på samma höjd

* Bra, eftersom regeln är kort och fångar fler sätt som en tabell kan
  vara avskuren på.
* Dåligt, eftersom tabellen märks i stället för att läsas.

### B – Fyllda cellrutor som linjer

* Bra, eftersom tabellen i #90 skulle bli en hel CSV.
* Dåligt, eftersom färgade rader och kolumner då blir linjer, vilket
  [ADR-0005](0005-konvertering-verktyg-ocr-och-kvalitet.md) och
  [ADR-0016](0016-tabeller-utan-lodrata-linjer.md) undviker med avsikt.
  Det ändrar fler tabeller än det rättar, och kräver en egen mätning.

### C – Som i dag

* Bra, eftersom inget ändras.
* Dåligt, eftersom tal utan etiketter står i en CSV som om de vore
  riktiga.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet** kom ur facit (#61).
2. **AI-agenten** prövade först att låta varje ord som är ett tal fälla
   tabellen. I stickprovet fällde det en driftredovisning som lästs
   rätt, eftersom en anteckning i marginalen bredvid den hade `typ 3`
   och `2 000 kr` i löptexten. Därför räknas bara fält som är ett tal,
   inte ett tal i en mening.
3. **Stickprovet** gav sedan två tabeller till utöver #90. Båda lästes
   för hand: en tabell med svaren Ja, Delvis och Nej, där frågornas
   nummer och den sista kolumnen stod utanför, och en tabell med två
   kolumner där den tredje stod utanför.

Ompröva beslutet om facit eller poolen visar en tabell som fälls i
onödan. Alternativ B är värt att mäta om sådana tabeller är vanliga.
