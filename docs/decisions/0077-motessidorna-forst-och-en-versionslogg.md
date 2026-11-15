---
status: proposed
date: 2026-11-15
decision-makers: projektägaren
consulted: AI-agenten
---

# Mötessidorna hämtas först i ett eget jobb, och varje ny version av ett dokument skrivs i en versionslogg

## Context and Problem Statement

Projektägaren vill att poolen varje dag kollar om ett mötes kallelse,
handlingar eller protokoll har kommit eller ändrats, och att det från nu
lagras hur ofta det sker inför och efter ett möte
([#276](https://github.com/moggleif/kommunhandlingar/issues/276)).

Nattkörningen läser redan alla mötessidor två gånger om dygnet och tar in
varje ny fil och varje utbytt fil, eftersom Sitevision ger en utbytt fil en
ny tidsstämpel i adressen ([ADR-0004](0004-inkrementell-korning-poolen-ar-tillstandet.md)).
Men det som hämtats ur mötessidorna når `main` först när arkivet är klart,
upp till sex timmar senare, och en ny version skriver över den gamla, så att
när den kom bara syns i git-historiken. Hur blir mötenas dokument tidiga och
oberoende av arkivet, och var lagras versionerna så att det går att räkna på?

## Decision Drivers

* **Mötessidorna går absolut först och är en egen del** (projektägaren).
* **Om inget har hänt görs inget**: ingen gren, ingen PR, ingen rad.
* **Statistiken lagras, visas inte än**, och ska gå att räkna på senare.
* **Inget hårdkodat om en kommun eller plattform**, och inget härlett
  lagras.
* **Inga krockande PR:er**: två körningar som skriver samma filer från
  olika utgångslägen fastnar i auto-mergen (#260, #264).

## Considered Options

* A – Nattkörningen delas i två jobb, mötessidorna först och arkivet ovanpå,
  och steg 2 skriver en versionslogg per kommun
* B – Ett eget dagligt jobb som bara kollar organ med ett möte i ett fönster
  ur kalendern och öppnar en egen PR
* C – Ingen ny fil: statistiken räknas fram ur git-historiken när den behövs
* D – Versionerna som en lista i dokumentets front matter

## Decision Outcome

Valt alternativ: "A", eftersom nattkörningen redan kollar allt och det
enda som saknades var att mötessidorna inte väntar på arkivet och att
versionerna lagras.

* **Jobbet `moten`** kör upptäckt och steg 2 för de levande källorna i
  varje kommun, utan omkonvertering (`hamta --utan-omkonvertering`), så
  att bara det nya och ändrade tas, och sedan datakontrollerna och
  incheckningen på grenen
  `nattkorning/<datum>-<id>-moten`, och dess PR öppnas och mergas som
  i [ADR-0052](0052-nattkorningen-mergar-sin-pr-sjalv.md).
* **Jobbet `arkiv`** startar när `moten` är klart, från dess gren eller,
  utan gren eller om `moten` föll, från `main`. Det gör upptäckten om och
  kör steg 2 för de levande källorna, som då har omkonverteringen kvar
  (ADR-0019) och det som kommit sedan mötenas jobb, eller allt levande om
  `moten` föll, och sedan arkivet, om det levande steget gick igenom. Det
  checkar in på
  `nattkorning/<datum>-<id>-arkiv`. Grenen bygger på mötenas, så att de två
  PR:erna aldrig krockar: mergas arkivets först följer mötenas commit med.
  Varje jobb har sin egen tidsbudget.
* **PR-jobbet** är ett återanvänt workflow som båda anropar, så att token
  fortfarande bara når ett jobb utan utcheckning. De levande källornas
  steg och incheckningen är var sin composite action som båda jobben
  använder. Bara arkivets steg har `continue-on-error`, som i dag.
* **`versioner/<kommun>.csv`** får en rad för varje källnyckel som efter
  ett levande steg 2 är ny i poolen eller har en annan `kalla_url` eller
  `sha256` än före, också när steg 2 stoppas av ett fel:
  `sedd` (körningens tid), `organ`, `datum`, `typ`, `kallnyckel`,
  `kalla_url`, `sha256` och `dokument`. Raden räknas fram ur poolens front
  matter före och efter steg 2, inte i behandlingen av varje dokument.
  "Ny" och "ändrad", källans tidpunkt i adressen och dagar före eller efter
  mötet räknas fram när statistiken byggs.

### Consequences

* Bra, eftersom nya kallelser och protokoll når `main` minuter efter
  körningens start, också när arkivet tar hela sin budget eller faller.
* Bra, eftersom omkonverteringen och arkivet får en egen budget på sex
  timmar.
* Neutralt, eftersom mötessidorna läses två gånger per körning.
* Bra, eftersom loggen bara växer när något kommit eller ändrats, och
  källans egen tidsstämpel i `kalla_url` gör statistiken oberoende av hur
  ofta körningen tittar.
* Neutralt, eftersom en natt kan ge två PR:er i stället för en.
* Dåligt, eftersom en fil som tas bort från en mötessida inte syns i loggen
  (den upptäcks inte i dag heller, K12).
* Dåligt, eftersom en version som både kommer och byts ut mellan två
  körningar inte syns.
* Dåligt, eftersom adresserna i loggen kan ha personnamn i filnamnet,
  som front matter under `data/`; undantaget i AGENTS.md utvidgas därför
  till `versioner/`.
* Dåligt, eftersom arkivets jobb checkar ut mötenas gren medan dess PR kan
  mergas, så att GitHub inte får ta bort grenar efter merge.

### Confirmation

Testerna för loggen i `tests/test_versionslogg.py`. Att jobben går i rätt
ordning syns i första körningen efter mergen: mötenas PR öppnas innan
arkivet är klart.

## Pros and Cons of the Options

### A – Två jobb och en versionslogg

* Bra, eftersom mötessidorna går först och blir en egen del.
* Bra, eftersom inget nytt verktyg behövs och hämtningen fortsätter att
  titta på alla mötessidor, också på dokument som kommer sent.
* Dåligt, eftersom workflowet blir längre.

### B – Eget jobb med fönster ur kalendern

Kallelse och handlingar 7 dagar före till 7 dagar efter mötet, protokoll
mötesdagen till 14 dagar efter, som projektägaren först beskrev.

* Bra, eftersom bara de mötessidor som är aktuella hämtas.
* Dåligt, eftersom det kollar färre sidor än nattkörningen redan gör, så
  nattkörningen behövs ändå för det som kommer sent.
* Dåligt, eftersom två jobb som skriver i `data/` från olika utgångslägen
  krockar i auto-mergen, eller får vänta i samma kö bakom arkivet.
* Dåligt, eftersom en ny modul för fönstren behövs.

### C – Ur git-historiken

* Bra, eftersom ingen ny fil behövs, och historiken sedan 2026-10-07 finns.
* Dåligt, eftersom en squash, en omkonvertering eller en sammanslagen
  nattkörning gör historiken svår att tolka, och den inte går att läsa
  utan git.

### D – I front matter

* Bra, eftersom versionerna står vid dokumentet.
* Dåligt, eftersom front matter beskriver den version som finns
  ([ADR-0003](0003-dokumentets-identitet-och-datamodell.md)), och
  schemat, datakontrollerna och varje skrivning skulle ändras.

## More Information

Projektägaren beskrev först ett eget jobb med fönster ur kalendern. AI-agenten
visade i fas 0 att nattkörningen redan läser alla mötessidor och tar in
utbytta filer, med GA:s protokoll 2026-10-22 som exempel: den första
versionen hämtades 2026-10-23 och den justerade, med ny tidsstämpel i
adressen, samma natt som den lades upp 2026-10-29. Ett eget jobb skulle
kolla färre sidor och krocka med nattkörningen. Projektägaren valde
versionsloggen i nattkörningen och lade till att mötesdelen ska köras
absolut först och vara en egen del, vilket gav de två jobben.

Fönstren 7/7 och 0/14 dagar blir regler för statistiken när den byggs.
Loggen fylls inte bakåt ur git-historiken nu; det går att göra senare.

Granskningen (fas 6) fann att adresserna kan bära personnamn, till
exempel i en motions filnamn. Loggen citerar samma värden som dokumentets
front matter, maskade på samma sätt (ADR-0022), och utan adressen går
källans tidpunkt förlorad. AI-agenten valde därför att utvidga undantaget
för poolens innehåll till loggen i stället för att ta bort kolumnen; det
avgörs av projektägaren vid kontrollpunkten i fas 7.

Granskningen fann också att en rad som först skrivs med tom `sha256`,
när dokumentet inte gick att hämta, aldrig fick sitt innehåll när det
senare hämtades under samma adress. En ändrad `sha256` ger därför också en
rad. Och loggen skrivs i en `finally`, så att ett oväntat fel i steg 2 inte
lämnar ändrade dokument utan rad.

Radens `sedd` är körningens tid, inte `hamtad`, eftersom en ny adress med
samma innehåll inte ändrar `hamtad`
([ADR-0004](0004-inkrementell-korning-poolen-ar-tillstandet.md)).
Projektsidornas filer (ADR-0068) kommer ur en levande källa och loggas
också; de har inget möte, vilket statistiken får ta hänsyn till.

Omkonverteringen av de levande källorna (#84) låg sist i samma steg 2 och
kunde ta hela budgeten; i mötenas jobb hade den hållit PR:en i timmar. Den
flyttades därför till det andra jobbet, som en flagga och inte som en ny
väg genom koden.

Omprövas när statistiken ska visas, eller om loggen blir för stor för en
fil per kommun.
