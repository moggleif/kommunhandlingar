---
status: proposed
date: 2026-10-13
decision-makers: projektägaren
consulted: AI-agenten
---

# Rubriker över flera kolumner och på flera textrader i tabeller utan lodräta linjer

## Context and Problem Statement

Efter [ADR-0037](0037-rubrikrader-och-sidfot-i-tabeller-utan-linjer.md)
räknade facit ([ADR-0025](0025-facit-for-konverteringen.md)) en tabell
som ofullständig: driftredovisningen i årsredovisningen
([#123](https://github.com/moggleif/kommunhandlingar/issues/123)).
Tabellen blev en CSV, men rubriken stod kvar i texten. Rubriken har två
rader med två textrader var, `Budget⏎2025` och `Netto-⏎anslag`. I den
översta raden står `Bokslut 2025` över fyra kolumner och `Bokslut 2024`
över tre, fast texten bara når in i två kolumners fack. Rubrikerna är centrerade i sina celler, medan talen står till
höger. [ADR-0016](0016-tabeller-utan-lodrata-linjer.md) tar bara med en
rubrik vars högerkant står i linje med kolumnens tal, så ingen av raderna
gick att läsa. Hur ska en sådan rubrik läsas, och när ska den stå kvar i
texten?

## Decision Drivers

* Data ska vara rätt eller märkt. En rubrik på fel kolumn är värre än en
  rubrik som står kvar i texten.
* En tabell ska bli en CSV med sin rubrik överst.
* Det som inte går att avgöra ska inte gissas.

## Considered Options

* A – Kolumnens fack, lodräta linjer för en rubrik över flera kolumner,
  och täta textrader fogas ihop
* B – Rubriken över flera kolumner fördelas efter läget, utan linjer
* C – Som i dag

## Decision Outcome

Valt: A. En rubrik hör till en kolumn när den ryms i kolumnens fack, som
börjar där föregående kolumn slutar och slutar vid kolumnens egen
högerkant. Då följer också en centrerad rubrik med, inte bara en som står
i linje med talen. Det ersätter regeln i ADR-0016 att varje rubrik ska
stå med högerkanten i linje med sin kolumn; resten av ADR-0016 gäller.

En rubrik som står över flera fack spänner över kolumnerna mellan de
lodräta linjerna närmast på var sida om den, när den står mitt emellan
dem och varje linje står i ett mellanrum mellan kolumnerna. Kanterna på
rutor räknas som linjer, så en linje kan också vara kanten på en ruta
bakom rubriken. Rubriken står i den första av sina kolumner, och resten
av cellerna är tomma. Saknas en linje på någon sida, står en linje inte
mellan kolumnerna, som en sidram, eller står rubriken inte mitt emellan
linjerna, går det inte att avgöra, och rubriken står kvar i texten som
förut.

Textrader som står tätare än en halv teckenhöjd är samma rubrikrad. En
cell fogas till cellen ovanför med ett mellanslag. När cellen ovanför
slutar med ett avstavningsstreck och cellen under börjar med liten
bokstav fogas de utan strecket, så att `Netto-⏎anslag` blir
`Nettoanslag`, men inte när cellen under börjar med `och`, `eller` eller
`samt`, som i `Kultur-⏎och fritid`. Den översta rubrikraden ska stå
över varje kolumn, som förut, så att rubriken aldrig blir halv. Står en
cell under en rubrik som spänner över flera
kolumner och täcker andra kolumner än den, står rubriken kvar i texten.
Reglerna står i `konvertering/spann.py`.

Poolens version höjs till 0.8.10. Poolen rättas när den konverteras om
([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

### Consequences

* Bra, eftersom driftredovisningen får hela sin rubrik. I facit går
  `ratt` från 15 till 16 och `ofullstandiga` från 1 till 0.
* Bra, eftersom ett stickprov på tio handlingar ur poolen, 1 978 sidor ur
  textlagret, ändrar tre sidor, och alla till det bättre: tre tabeller
  med centrerade rubriker, som `Utfall 2020` och `tim/ärende`, får sin
  rubrik. På en av sidorna stod rubrikens årtal tidigare kvar i texten
  som en rad med tal, och sidan var `tabell-osaker`; nu blir den `ok`.
* Dåligt, eftersom en rubrik över flera kolumner utan lodräta linjer
  fortfarande står kvar i texten, och tabellen blir en CSV utan rubrik.
* Dåligt, eftersom två rubrikrader som står tätare än en halv teckenhöjd
  blir en, till exempel `Budget` ovanför `2026` blir `Budget 2026`.
  Texten finns kvar, men inte radindelningen.
* Dåligt, eftersom en kort rad tätt ovanför rubriken, som en enhet
  `tkr` över den sista kolumnen, fogas in i cellen under och blir
  `tkr Plan`. Texten och talen står rätt, men cellen får ett ord till.
  Samma regel gör att `Budget-⏎avvikelse 2024`, som står bredvid en rad
  med enradiga rubriker, blir en cell.
* Dåligt, eftersom vilken text som helst som ryms i facken nu räknas som
  rubrik, också korta ord som inte står i linje med talen. Den måste
  fortfarande stå direkt ovanför tabellen och över varje kolumn.

### Confirmation

`tests/test_spann.py` prövar reglerna på påhittade ord, och facit visar
driftredovisningen som rätt.

## Pros and Cons of the Options

### A – Fack, linjer och täta textrader

* Bra, eftersom varje regel bygger på något som syns på sidan: var
  kolumnerna slutar, var linjerna står och hur tätt raderna står.
* Dåligt, eftersom en rubrik över flera kolumner bara läses i en tabell
  som har linjer eller färgade rutor runt sina celler.

### B – Fördelning efter läget

* Bra, eftersom också tabeller helt utan linjer får sin rubrik.
* Dåligt, eftersom läget inte räcker. `Bokslut 2025` står nästan lika
  mitt över två kolumner som över fyra. Rubriken skulle kunna hamna på
  fel kolumner utan att det märks.

### C – Som i dag

* Bra, eftersom inget ändras.
* Dåligt, eftersom en centrerad rubrik aldrig följer med, också när den
  bara står över en kolumn.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet** kom ur facit och #117. Projektägaren bad AI-agenten ta det
   utan avstämningar och välja det rekommenderade alternativet vid varje
   vägval.
2. **AI-agenten** mätte rubriken. Talen står till höger i sina celler,
   och rubrikerna är centrerade, så ingen rubrik står i linje med sina
   tal. Varje rubrik ryms däremot i sitt fack. `Bokslut 2025` står över
   två fack, och dess mitt står nästan lika nära mitten av två kolumners
   fack som av fyra (2,8 och 3,4 punkter). Det som avgör är linjerna:
   sidan har lodräta linjer
   mellan grupperna av kolumner, och färgade rutor bakom rubrikens översta
   rad.
3. **Första försöket** lät tabellens kant räknas som linje där linje
   saknades. I ett stickprov på tio handlingar ur poolen, 1 978 sidor,
   gav det en felaktig rubrik: två rubriker så tätt att de blev ett fält,
   `Antal/år tim/ärende`, stod i en ruta över två kolumner och hamnade
   över den första av dem. Därför krävs nu en linje på var sida och att
   rubriken står mitt emellan dem.
4. **Granskningen** fann att en sidram, eller en sidstor osynlig ruta,
   gav linjer som en centrerad sidrubrik stod mitt emellan; därför ska
   linjerna stå i ett mellanrum mellan kolumnerna. Granskningen fann
   också att en ofullständig textrad tätt ovanför rubriken, som `tkr`,
   fogades in i cellen under, och att `Kultur-⏎och fritid` blev
   `Kulturoch fritid`. Strecket står nu kvar före `och`, `eller` och
   `samt`. AI-agenten prövade att kräva att den översta textraden ensam
   står över varje kolumn, men då föll en rubrik i stickprovet där
   `Budget-⏎avvikelse 2024` står bredvid de enradiga rubrikerna och börjar
   ovanför dem. Det går inte att skilja från `tkr` ovanför `Plan` på
   läget, så `tkr Plan` står kvar som en nackdel.

Ompröva beslutet om poolen visar många tabeller utan linjer vars rubriker
spänner över flera kolumner.
