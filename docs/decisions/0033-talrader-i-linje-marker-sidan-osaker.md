---
status: proposed
date: 2026-10-12
decision-makers: projektägaren
consulted: AI-agenten
---

# Talrader i linje som inte blev någon tabell märker sidan osäker

## Context and Problem Statement

Facit ([ADR-0025](0025-facit-for-konverteringen.md)) hittade en tabell
som försvinner utan märkning
([#92](https://github.com/moggleif/kommunhandlingar/issues/92)). I
årsredovisningen står tabellen *Avfall & Återvinning* i den högra
spalten, bredvid löptext i den vänstra:

```text
pågår och är kostnadsdrivande … mark-    Inkomster   0,0   0,0   0,0   0,0
förhållanden och med hänsyn till …       Utgifter   -2,0 -14,8  -0,9  13,9
```

Raderna delar textrad med löptexten. Därför blir de ingen tabell utan
lodräta linjer ([ADR-0016](0016-tabeller-utan-lodrata-linjer.md)), där
radens första fält ska vara etiketten. I sidans text skiljs löptexten och
etiketten av ett enda mellanslag, så raderna blir inte heller en osäker
tabell, som kräver två mellanslag mellan fälten. Sidan blev `ok`, och
tabellens tal stod bara i texten. Hur ska en sådan tabell märkas?

## Decision Drivers

* Data ska vara rätt eller märkt: en tabell får inte försvinna tyst.
* Regeln ska vara kort och inte märka sidor med löptext som innehåller
  tal.
* Den ska fånga fler sätt att missa en tabell än just spalterna.

## Considered Options

* A – Talrader i linje som inte blev någon tabell märker sidan
* B – Läsa spalterna var för sig, så att tabellen blir CSV
* C – Som i dag

## Decision Outcome

Valt: A, eftersom den följer "hellre märka än gissa" och fångar varje
tabell vars rader står kvar i linje utanför de lästa tabellerna, oavsett
varför den inte lästes. Raderna tas ur sidans ord utanför de säkra
tabellerna och delas i fält som i tabellerna utan lodräta linjer, med
ett tvetydigt mellanrum räknat som en gräns. En rad räknas när minst två
fält är tal som inte är årtal (1900–2099). Två rader står i linje när
minst två tal har högerkanten högst 2 punkter från varandra. En rad i
linje med minst två andra gör sidan `tabell-osaker`. Raderna står kvar i
texten; de blir inget kodblock. Regeln står i
`konvertering/kvarvarande.py`.

Poolens version höjs till 0.8.3. Poolen rättas när den konverteras om
([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

### Consequences

* Bra, eftersom tabellen i #92 märks, och facit räknar den som osäker i
  stället för saknad.
* Bra, eftersom regeln också märker kommunbudgetens sida 87, där tre
  rader ur resultaträkningen (*Årets resultat enligt blandmodellen* med
  flera) stod omärkta i texten.
* Bra, eftersom ett stickprov på tio handlingar ur poolen, omkring 1 900
  sidor ur textlagret, märker 25 sidor till som var `ok`. På de elva av
  dem som lästes stod tabelldata omärkt i texten: taxor, nyckeltal i procent, en
  driftredovisning med hundra rader och belopp per stödområde. Två av
  dem är en riskmatris med produkterna 1–16, en figur snarare än en
  tabell, som märks i onödan.
* Dåligt, eftersom hela sidan märks, också de tabeller på den som lästs
  rätt. Det gäller redan för de andra sätten att märka en sida.
* Dåligt, eftersom en tabell i en spalt fortfarande inte blir CSV. Det
  är alternativ B, som kan bli ett eget issue.
* Dåligt, eftersom en innehållsförteckning i två spalter, med
  sidnumren högerställda i båda, ser ut som talrader i linje och märker
  en sida som lästs rätt. Granskningen visade det med påhittade ord; i
  stickprovet förekom det inte.
* Neutralt, eftersom rubrikrader med bara årtal inte räknas. En tabell
  vars värden bara är tal mellan 1900 och 2099 märks inte.

### Confirmation

`tests/test_kvarvarande.py` prövar regeln på påhittade ord och på sidan
med tabellen i #92. Bland testfixturernas sidor ändrar regeln bara de
två sidorna ovan, båda till rätt märkning. Facit ska inte bli sämre:
`saknade` går från 2 till 1 och `osakra` från 1 till 2. Stickprovet
ovan gjordes en gång för hand och är inget test.

## Pros and Cons of the Options

### A – Talrader i linje märker sidan

* Bra, eftersom den är kort och fångar fler fel än spalterna.
* Dåligt, eftersom den inte ger någon CSV.

### B – Läsa spalterna var för sig

* Bra, eftersom tabellen blir data.
* Dåligt, eftersom det kräver att spalterna känns igen på sidan, en ny
  och större regel som kan dela en vanlig tabell i två.

### C – Som i dag

* Bra, eftersom inget ändras.
* Dåligt, eftersom en tabell försvinner utan märkning.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet** kom ur facit (#61).
2. **AI-agenten** prövade först att låta en följd av talrader avgöra,
   som för den osäkra tabellen i texten. Det räcker inte: en rad
   löptext i den vänstra spalten står mellan *Utgifter* och *Netto* och
   bryter följden. Därför avgör att talen står i linje, inte att
   raderna följer på varandra.
3. **Rubriker med år:** utan undantaget för årtal skulle rubrikraderna
   över flera tabeller med samma kolumner kunna märka en sida där alla
   tabeller lästs rätt. Först undantogs alla fyrsiffriga heltal, som i
   tabellerna utan lodräta linjer, men granskningen (fas 6) visade att
   belopp som `1250` då inte räknas. Därför undantas bara 1900–2099.
4. **Stickprovet (AI-agenten)** hämtade tio handlingar från olika organ
   och prövade regeln på varje sida ur textlagret. Elva av de 25 sidor
   som regeln märker lästes en och en; alla utom riskmatrisen var
   tabeller som inte blev CSV.

Ompröva beslutet om spalterna blir vanliga i poolen; då är alternativ B
värt sin regel.
