---
status: proposed
date: 2026-10-13
decision-makers: projektägaren
consulted: AI-agenten
---

# Rubrikrader, radavstånd och sidfot i tabeller utan lodräta linjer

## Context and Problem Statement

Efter [ADR-0035](0035-avsnittsrubriker-och-artal-i-tabeller-utan-linjer.md)
räknade facit ([ADR-0025](0025-facit-for-konverteringen.md)) tre tabeller
i årsredovisningen som ofullständiga
([#117](https://github.com/moggleif/kommunhandlingar/issues/117)):

* Nyckeltalens rubrikrad `Kommunen 2021 … 2025` stod 22,7 punkter ovanför
  den första raden, och gränsen var tre teckenhöjder (22,5).
* Driftredovisningen delades i två vid ett radavstånd på 24,8 punkter före
  `Finans`.
* Investeringstabellen föll, eftersom sidfoten `Kungsbacka kommuns
  årsredovisning 2025 79` stod strax under den och sidnumret blev en egen
  kolumn med ett enda tal. Rubriken föll också, eftersom raden
  `(belopp i mnkr)  tom december  2025  2025` räknades som en talrad och
  en rad löptext stod strax ovanför.

Granskningen av #93 fann dessutom att en rad med bara årtal mellan två
tabeller hörde till följden ovanför och fällde båda. Hur ska tabellerna
hållas ihop med sina rubriker utan att annan text dras in?

## Decision Drivers

* Data ska vara rätt eller märkt: en rad får inte falla ur en tabell som
  sparas som säker.
* En tabell ska bli en CSV med sin rubrik överst.
* Det som inte hör till tabellen, som en sidfot eller tabellen ovanför,
  ska inte dras in.

## Considered Options

* A – Fyra teckenhöjder, sidfot och årtalsrader skiljs efter läget
* B – Avståndet mäts mot tabellens eget radavstånd
* C – Som i dag

## Decision Outcome

Valt: A. Raderna i en följd och rubrikraderna får stå högst fyra
teckenhöjder isär i stället för tre. En tabellrad vars etikett börjar
till höger om det första talet i följden fortsätter inte följden: så
står en sidfot, där texten börjar inne bland kolumnerna, men aldrig en
rad i tabellen. En rad där varje tal är ett årtal, också med en etikett
som `Kommunen 2021 2022`, börjar ingen följd, och står den direkt ovanför
en rad med tal är den nästa tabells rubrikrad i stället för en rad i
tabellen ovanför. Rubrikraderna tas med uppåt till en rad med ett tal
som inte är ett årtal, som tabellen ovanför, eller till ett ensamt fält
som börjar där etiketterna står, som en rad löptext; en sådan rad gör
inte längre rubriken osäker. Reglerna står i `konvertering/olinjerade.py`,
`rader.py` och `rubriker.py`.

Poolens version höjs till 0.8.8. Poolen rättas när den konverteras om
([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

### Consequences

* Bra, eftersom nyckeltalens två tabeller och investeringstabellen blir
  hela med sina rubriker, och driftredovisningen blir en CSV. I facit går
  `ratt` från 13 till 15 och `ofullstandiga` från 3 till 1.
* Bra, eftersom ett stickprov på tio handlingar ur poolen, 1 978 sidor ur
  textlagret, ändrar två sidor, och båda till det bättre: två tabeller vars
  rubrikrad `Skolform 2026 2027` och `Kostnadsslag 2026 … 2029` räknades
  som en rad med tal, och fällde tabellen, blir CSV. Årtalen står några
  punkter ur linje med kolumnerna, så rubriken står kvar i texten.
* Dåligt, eftersom driftredovisningens rubrik står kvar i texten. Den har
  rubriker som spänner över flera kolumner (`Bokslut 2025` över fyra) och
  avstavade ord i två rader (`Netto-⏎anslag`), och ingen av dem står i
  linje med en kolumn. Det lämnas till ett eget issue.
* Dåligt, eftersom en rad där varje värde ser ut som ett årtal, som
  `Antal 2010 2050`, räknas som en rubrikrad när den står överst eller
  direkt ovanför en tabell. Talen står kvar, men i rubriken.
* Dåligt, eftersom en fortsättning med stor bokstav, som `GBG-KBA` under
  `Åtgärder reservvatten`, fortfarande blir en avsnittsrubrik, som i
  ADR-0035. Talen står på rätt rad.

### Confirmation

`tests/test_rubrikrader.py` prövar reglerna på påhittade ord, och facit
visar nyckeltalen och investeringstabellen som rätta.

## Pros and Cons of the Options

### A – Fyra teckenhöjder, sidfot och årtalsrader efter läget

* Bra, eftersom varje regel bygger på något som syns på sidan: var
  etiketten börjar och vilka tal raden har.
* Dåligt, eftersom en större gräns kan dra in en rad som står lite längre
  bort; den måste ändå ha tal i tabellens kolumner för att tabellen ska
  bli säker.

### B – Avståndet mot tabellens eget radavstånd

* Bra, eftersom gränsen följer tabellens egen sättning.
* Dåligt, eftersom nyckeltalens rubrik och avståndet mellan nyckeltalens
  två tabeller är nästan lika stora (22,7 och 23,3 punkter) och inte går
  att skilja med något avstånd; det som skiljer dem är vad raderna
  innehåller.

### C – Som i dag

* Bra, eftersom inget ändras.
* Dåligt, eftersom tabellerna delas, faller eller förlorar sin rubrik
  för en bråkdel av en punkt.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet** kom ur facit (#61) och granskningen av #93. Projektägaren
   bad AI-agenten ta det utan avstämningar och välja det rekommenderade
   alternativet vid varje vägval.
2. **AI-agenten** prövade först att skilja sidfoten efter teckenhöjden.
   Då föll budgetens kursiva `varav`-rader, som står i mindre stil, ur
   tabellen. Sedan prövades att kräva att varje tal står i linje med ett
   tal ovanför; då blev en tabell med ett tal ur linje säker utan den
   raden, i stället för att falla, och befintliga tester föll. Etikettens
   läge träffar sidfoten men ingen tabellrad.
3. **Fyra teckenhöjder** behövs för driftredovisningen (3,3) och
   nyckeltalens rubrik (3,03). Då drogs nyckeltalens två tabeller ihop,
   eftersom de står 3,1 teckenhöjder isär; därför räknas en rad med
   etikett och årtal som rubrik. Ett befintligt test krävde att en rad
   med bara årtal under en tabell fäller den; det gäller fortfarande när
   ingen tabell följer under årtalen. Ett annat test krävde att en rad
   med tal ovanför rubriken gör den osäker; nu är den gränsen för
   rubriken, och testet ändrades.

Ompröva beslutet om poolen visar en sidfot eller en rad text som dragits
in i en tabell.
