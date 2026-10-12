---
status: proposed
date: 2026-10-12
decision-makers: projektägaren
consulted: AI-agenten
---

# En etikett som fortsätter på nästa rad gör en tabell som delats i rader osäker

## Context and Problem Statement

En etikett som bryts över två rader bredvid två staplade tal, ett värde
och dess andel, ser ut så här:

```text
Kostnader för    -1 845    -2 001
verksamheten       12 %      13 %
```

Tabellerna utan lodräta linjer
([ADR-0016](0016-tabeller-utan-lodrata-linjer.md)) och delningen av
tabeller med linjer
([ADR-0028](0028-tabeller-med-linjer-delas-efter-linjer-och-textrader.md))
läser rutan som två rader, `Kostnader för | -1 845 | -2 001` och
`verksamheten | 12 % | 13 %`, med var sin halva av etiketten.
Geometriskt går det inte att skilja från två etiketter med var sitt tal,
som `Intäkter⏎Kostnader`. Hur känns det igen
([#97](https://github.com/moggleif/kommunhandlingar/issues/97))?

## Decision Drivers

* Data ska vara rätt eller märkt: hellre en osäker tabell än tal under
  en halv etikett.
* En regel gemensam för båda vägarna.
* Riktiga etiketter som börjar med liten bokstav, som `varav bidrag`,
  ska inte fälla tabellen.

## Considered Options

* A – Etikettens text: den första slutar ofullständigt och nästa börjar
  med liten bokstav
* B – Bara liten bokstav i nästa etikett
* C – Som i dag

## Decision Outcome

Valt: A, eftersom båda raderna då visar att etiketten fortsätter, och
`varav …` efter en hel etikett inte gör det. En etikett i tabellens
första kolumn med text fortsätter på nästa rad när

* dess sista textrad slutar med ett ord som binder till nästa (`och`,
  `eller`, `samt`, `för`, `av`, `i`, `till`, `med`, `på`, `om`, `från`,
  `vid`, `som`, `inom`, `per`, `mot`, `utan`, `under`, `över`, `efter`),
  med ett avstavningsstreck efter en bokstav, som `Kommun-`, eller med en
  parentes som inte stängts, och
* nästa rads etikett börjar med liten bokstav.

Då blir tabellen ingen CSV, utan står kvar som förut: en tabell utan
lodräta linjer står i texten som en osäker tabell, och en tabell med
linjer som inte delas märker sidan `tabell-osaker`. Regeln står i
`konvertering/ombrutna.py` och gäller tabellerna utan lodräta linjer och
de delade tabellerna med linjer, men inte en tabell med linjer där varje
rad har sina egna celler.

Poolens version höjs till 0.8.1. Poolen rättas när den konverteras om
([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

### Consequences

* Bra, eftersom `Kostnader för⏎verksamheten`, `Kommun-⏎område` och
  `Studsvik (13§ 5⏎och 13§ 6)` inte längre blir rader med halva
  etiketter.
* Bra, eftersom regeln är kort och delas av båda vägarna.
* Dåligt, eftersom en etikett som bryts utan ett sådant ord, som
  `Kostnader⏎verksamhet`, inte känns igen och blir två rader som förut.
* Dåligt, eftersom en riktig etikett som slutar med ett bindeord, och
  följs av en som börjar med liten bokstav, fäller tabellen. I poolen har
  vi inte sett något sådant fall.
* Neutralt, eftersom orden är svenska. En kommun som skriver på ett
  annat språk behöver en ny lista.

### Confirmation

`tests/test_ombrutna.py` prövar regeln, `tests/test_olinjerade.py` en
tabell utan lodräta linjer och sidan 10 i
`tests/fixtures/pdf/delade.pdf` (`tests/test_delade.py`) en delad tabell
med linjer. Facit ([ADR-0025](0025-facit-for-konverteringen.md)) ska inte
bli sämre.

## Pros and Cons of the Options

### A – Etikettens text på båda raderna

* Bra, eftersom båda raderna måste visa att etiketten fortsätter.
* Dåligt, eftersom den bygger på en lista med svenska ord.

### B – Bara liten bokstav i nästa etikett

* Bra, eftersom den är enklast.
* Dåligt, eftersom `varav …` börjar med liten bokstav. I poolen står det
  i över 200 tabeller.

### C – Som i dag

* Bra, eftersom inget ändras.
* Dåligt, eftersom halva etiketter står kvar som om de vore hela.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet** kom ur granskningen av #60. Projektägaren bad att
   följd-issues görs och mergas.
2. **Mätningen i poolen (AI-agenten)** gick igenom poolens alla CSV:er.
   Den letade efter två rader i följd med tal, där nästa etikett börjar
   med liten bokstav. `varav` stod för de flesta, följt av notbokstäver
   som `c)`, så liten bokstav ensam räcker inte (alternativ B). Med
   kravet på en ofullständig rad före träffade regeln 22 av 16 919
   CSV:er. Det var riktiga ombrytningar som `Kommun-⏎område`,
   `Program-⏎inriktning`, `hantering av⏎brottsmisstänkta` och
   `Studsvik (13§ 5⏎och 13§ 6)`, och lodrät eller spegelvänd text som
   ändå är fel.

Ompröva beslutet om facit eller poolen visar en riktig etikett som
fälls av regeln.
