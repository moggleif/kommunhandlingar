---
status: proposed
date: 2026-10-12
decision-makers: projektägaren
consulted: AI-agenten
---

# Avsnittsrubriker och årtal håller ihop en tabell utan lodräta linjer

## Context and Problem Statement

Facit ([ADR-0025](0025-facit-for-konverteringen.md)) räknade sju tabeller
som ofullständiga
([#93](https://github.com/moggleif/kommunhandlingar/issues/93)). I
kommunbudgeten delades en tabell utan lodräta linjer på upp till sju
CSV:er, och rubrikraden med årtal stod kvar i texten. Förenklat:

```text
                         2025    2026    2027
Verksamhetens intäkter  1 184   1 471   1 367
Skulder
Lån                       300     310     320
Avskrivningar på          389     453     478
byggnader
```

Reglerna i [ADR-0016](0016-tabeller-utan-lodrata-linjer.md) kräver att
varje rad i en följd har tal. En rad med bara en etikett, som avsnittet
`Skulder` eller fortsättningen `byggnader`, bröt därför tabellen, och en
rubrikrad med bara årtal räknades som en talrad, inte som en rubrik. Hur
ska en sådan tabell hållas ihop utan att annan text dras in?

## Decision Drivers

* Data ska vara rätt eller märkt: en etikettrad får inte flytta talen
  till fel rad.
* En tabell ska bli en CSV med sin rubrik överst
  ([K19](../02-KRAV.md#k19--en-tabell-som-fortsätter-på-nästa-sida-blir-en-tabell)).
* Löptext mellan två tabeller ska inte slå ihop dem.

## Considered Options

* A – En följd får gå över högst två etikettrader mellan två tabellrader,
  och en rad med bara årtal är en rubrikrad
* B – En följd får gå över valfritt många rader utan tal
* C – Som i dag

## Decision Outcome

Valt: A, eftersom en eller två korta etikettrader mellan raderna är
avsnittsrubriker eller ombrutna etiketter, medan längre text bryter
tabellen som förut. En etikettrad är en rad med ett enda fält med minst en
bokstav. En följd går över högst två sådana när raderna närmast ovanför och
under dem är tabellrader och alla står nära varandra. En etikettrad som
börjar med liten bokstav fogas till etiketten ovanför med ett mellanslag,
också under den sista raden, och en etikettrad ovanför en rad vars
etikett börjar med liten bokstav är början på den etiketten. En etikett
som slutar med kolon fogas inte. Annars blir en etikettrad en rad med
tomma celler. Blir följden över etikettraderna ingen tabell, prövas
delarna mellan dem var för sig, som förut. En rad med bara årtal
(1900–2099) börjar ingen följd utan kan bli tabellens rubrikrad. Står den
direkt under en tabell fäller den tabellen, som förut. En eller två
etikettrader mellan rubriken och tabellen tas med som avsnittsrubriker
när rubriken tas med. Reglerna står i
`konvertering/olinjerade.py`, `rader.py`, `rubriker.py` och
`mellanrader.py`.

Poolens version höjs till 0.8.6. Poolen rättas när den konverteras om
([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

### Consequences

* Bra, eftersom kommunbudgetens tre tabeller blir hela med sina rubriker.
  I facit går `ratt` från 9 till 13 och `ofullstandiga` från 7 till 3.
* Bra, eftersom en fortsättning som `byggnader` blir en del av etiketten
  i stället för att bryta tabellen.
* Bra, eftersom ett stickprov på tio handlingar ur poolen, omkring
  2 000 sidor ur textlagret, ändrar tre sidor, och alla tre till det
  bättre: två tabeller som inte lästs blir CSV, och en tabell som delats
  vid en avsnittsrubrik blir hel. Stickprovet visade också en etikett i
  tre rader, `Antal⏎medarbetare per chef`, där talen står på den
  mellersta; därför fogas också en etikettrad till raden under, och en
  fortsättning under den sista raden till den.
* Dåligt, eftersom en fortsättning som börjar med stor bokstav blir en
  avsnittsrubrik. Talen står ändå på rätt rad.
* Dåligt, eftersom en kort rad löptext mellan två tabeller med samma
  kolumner, som `Not 3`, inte går att skilja från en avsnittsrubrik: de
  två tabellerna blir en. I stickprovet förekom det inte.
* Dåligt, eftersom tre tabeller i årsredovisningen fortfarande är
  ofullständiga: en rubrikrad som står en bråkdel av en punkt för långt
  ovanför, en rubrik i två rader med avstavade ord och en etikett som
  fortsätter efter den sista raden. De lämnas till ett eget issue.

### Confirmation

`tests/test_mellanrader.py` prövar reglerna på påhittade ord, och facit
visar kommunbudgetens tabeller som rätta.

## Pros and Cons of the Options

### A – Högst två etikettrader och årtal som rubrik

* Bra, eftersom regeln är kort och löptext mellan två tabeller håller
  dem isär.
* Dåligt, eftersom en avsnittsrubrik i tre rader fortfarande bryter
  tabellen.

### B – Valfritt många rader utan tal

* Bra, eftersom fler tabeller hålls ihop.
* Dåligt, eftersom två tabeller med en kort text emellan slås ihop, och
  texten blir rader i tabellen.

### C – Som i dag

* Bra, eftersom inget ändras.
* Dåligt, eftersom tabellen delas på flera CSV:er och rubriken står i
  texten.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet** kom ur facit (#61). Projektägaren bad AI-agenten ta det
   utan avstämningar och välja det rekommenderade alternativet vid varje
   vägval.
2. **AI-agenten** prövade först att låta en följd gå över etikettrader
   utan villkor. Då drogs rubrikraden med årtal in i följden och
   kommunbudgetens tabeller försvann. Därför krävs tabellrader på båda
   sidor om etikettraderna, och en rad med bara årtal börjar ingen
   följd. Ett befintligt test visade att en rad med bara årtal under
   tabellen ska fälla den, så den får fortfarande avsluta en följd.
3. **Granskningen** fann en etikett som kapades: `per enhetschef` stod
   under den sista raden och föll bort, så att etiketten blev `Antal
   medarbetare`. Fortsättningar under den sista raden hör nu till
   tabellen. Granskningen fann också att `Varav:` fogades till raden
   under, och att en kort rad löptext mellan två tabeller slår ihop dem;
   det första rättades, det andra står som en nackdel.

Ompröva beslutet om facit eller poolen visar två tabeller som slagits
ihop över en avsnittsrubrik.
