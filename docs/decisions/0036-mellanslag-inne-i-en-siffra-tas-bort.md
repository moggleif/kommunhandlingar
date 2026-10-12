---
status: proposed
date: 2026-10-12
decision-makers: projektägaren
consulted: AI-agenten
---

# Ett mellanslag som börjar inne i en siffra tas bort innan texten läses

## Context and Problem Statement

Facit ([ADR-0025](0025-facit-for-konverteringen.md)) hittade 15 tal som
inte stämde i en budget ur ett kalkylark
([#91](https://github.com/moggleif/kommunhandlingar/issues/91)). I
texten stod `4 76,7` för `476,7`, `1 43,0` för `143,0` och `4 4,5` för
`44,5`. Det ser ut som tusentalsavgränsning men är fel tal.

Kalkylarket fyller ut cellerna med mellanslag, och ett av dem ligger
ovanpå talets första siffra: siffran `4` och mellanslaget börjar på
samma punkt. pdfplumber sorterar tecknen efter läget, lägger
mellanslaget efter siffran och delar talet där. Hur tas ett sådant
mellanslag bort utan att ändra annan text?

## Decision Drivers

* Ett tal i texten ska vara det som står på sidan.
* Mellanslag som skiljer ord, och tusentalsavgränsning, ska stå kvar.
* Regeln ska gälla alla dokument, inte en kommun eller ett kalkylark.

## Considered Options

* A – Ett mellanslag som börjar inne i en siffra och till mer än hälften
  täcks av den tas bort
* B – Alla mellanslag tas bort, och ord skiljs bara efter avståndet
* C – Talen fogas ihop efteråt i texten när de ser ut att vara delade

## Decision Outcome

Valt: A, eftersom det bara träffar mellanslag som ligger ovanpå en
siffra, där pdfplumber annars delar talet. Ett mellanslag tas bort när
det står på samma rad som en siffra, börjar där siffran börjar eller
inne i den, och till mer än hälften täcks av den. Ett mellanslag som
börjar före siffran står kvar, eftersom det skiljer siffran från texten
framför, som sidnumret i en innehållsförteckning. Regeln står i
`konvertering/mellanslag.py` och gäller hela sidan, text som tabeller.

Poolens version höjs till 0.8.7. Poolen rättas när den konverteras om
([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

### Consequences

* Bra, eftersom de 15 talen i facit stämmer: `tal_avviker` går från 15
  till 0.
* Bra, eftersom ett stickprov på tio handlingar ur poolen, omkring
  2 000 sidor ur textlagret, ändrar fem sidor: två taxetabeller där
  talen var delade (`4 0` blir `40`, `1 6` blir `16`) och nu blir CSV, en
  rad där fotnotssiffran i `timtaxa3 .` blir `timtaxa3.`, en sida med
  roterad text som var oläslig före och efter, och en sida med överlagrad
  text (se nedan).
* Dåligt, eftersom ett mellanslag som verkligen står mellan två tal men
  ritats ovanpå den första siffran försvinner. I stickprovet hände det en
  gång, i två textrader som ritats ovanpå varandra: `stö2d0 225-05-21`
  blev `stö2d0225-05-21`. Texten var oläslig redan förut, men sidan är
  märkt `ok`; att överlagrad text inte märks är ett äldre fel.

### Confirmation

`tests/test_mellanslag.py` prövar regeln på påhittade tecken och på
budgeten i #91. Facit ska inte bli sämre.

## Pros and Cons of the Options

### A – Mellanslag som börjar inne i en siffra

* Bra, eftersom regeln är kort och bara rör mellanslag ovanpå siffror.
* Dåligt, eftersom ett mellanslag ovanpå en bokstav står kvar och kan
  dela ett ord.

### B – Alla mellanslag bort

* Bra, eftersom inga utfyllnadsmellanslag kan dela något.
* Dåligt, eftersom ord i liten stil står tätare än pdfplumbers gräns och
  flyter ihop.

### C – Foga ihop talen efteråt

* Bra, eftersom tecknen lämnas orörda.
* Dåligt, eftersom `4 76,7` inte går att skilja från två tal i följd
  eller från tusentalsavgränsning utan att gissa.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet** kom ur facit (#61). Projektägaren bad AI-agenten ta det
   utan avstämningar och välja det rekommenderade alternativet vid varje
   vägval.
2. **AI-agenten** prövade först att ta bort varje mellanslag som till
   mer än hälften täcks av ett annat tecken. I stickprovet försvann då
   mellanslaget före sidnumret i innehållsförteckningar, där det börjar
   strax före siffran. Att i stället ta bort varje mellanslag som börjar
   inne i en siffra gjorde facit sämre, eftersom tätt satta
   tusentalsmellanslag börjar strax innan siffran framför slutar. Båda
   villkoren behövs.

Ompröva beslutet om poolen visar ett tal som slagits ihop med ett annat.
