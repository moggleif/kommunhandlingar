---
status: proposed
date: 2026-10-22
decision-makers: projektägaren
consulted: AI-agenten
---

# Lokalbehoven följs steg för steg ur alla organs dokument, i en CSV per kommun, och visas som målsidan

## Context and Problem Statement

Varje år beslutar en nämnd om sina lokalbehov för de kommande fem åren
och prioriterar ibland bland dem. Behoven går till kommunens lokalgrupp.
Några kommer in i lokalplanen i kommunfullmäktiges budget, får
startbeslut i kommunstyrelsen och byggs av servicenämnden
([#186](https://github.com/moggleif/kommunhandlingar/issues/186)). Ingen
handling följer upp förra årets prioriteringar. En genomgång av GA:s
lokalbehov 2023–2026 visade att två behov med prioritet 3 försvann ur
listorna utan att någon handling säger varför, och att det ena av dem ändå byggdes som en mindre
anpassning hos servicenämnden. Det syntes bara i servicenämndens bokslut.

Webbplatsen ska visa varje behov över tid, med en källa för varje steg,
så att det går att se om prioriteringarna håller och vad som levereras.
Hur kommer stegen in på sidan när de står i fyra olika organs dokument,
och hur blir sidan pålitlig?

## Decision Drivers

* **Varje uppgift bär sin härkomst**, med en länk till sidan som visar
  den.
* **Hellre märka än gissa.** Servicenämndens projekt har egna namn och
  nummer och nämner inte nämndens behov.
* **Ingen kod för säkerhets skull**, och återanvänd målsidans delar
  (projektägaren: "kopiera mål-modellen").
* **Inget hårdkodat om en kommun.**
* **Sidan drar inga slutsatser** om behoven, som "tappat" eller "försenat".

## Considered Options

* A – AI-agenten skriver en CSV per kommun med en rad per steg, där
  källan får vara vilket organs dokument som helst; bygget prövar texten
  på sidan
* B – Som A, men bara nämndens egna dokument som källor
* C – En rad per behov och år, med en kolumn per fas
* D – Kod letar upp lokalbehoven i poolen när webbplatsen byggs

## Decision Outcome

Valt: A, eftersom bara de andra organens dokument visar om ett behov kom
in i lokalplanen, fick startbeslut eller blev utfört, och en rad per
steg rymmer steg som inte följer budgetåret.

* **Filen** är `lokalbehov/<kommun>.csv` med kolumnerna `organ`, `behov`,
  `ar`, `fas`, `varde`, `text`, `kalla` och `tolkad`. Faserna är
  `forslag`, `lokalbehov`, `prioritet`, `lokalplan`, `startbeslut`, `pagar` och
  `utfort`. `organ` är nämnden som äger behovet; `kalla` får vara ett
  dokument från vilket av kommunens organ som helst.
* **Texten och värdet är källans** och prövas mot källans sidor på samma
  sätt som målfilen (ADR-0044). En prioritet måste ha ett värde och en
  lokalplan ett löpnummer. Som för målen går protokollet före
  handlingarna (ADR-0045): ett förslag inför ett möte är fasen `forslag`
  tills protokollet visar beslutet.
* **Ett behov har ett namn** på sidan, valt av agenten, även när källorna
  kallar det olika. När källan inte själv säger att steget gäller
  behovet står `tolkad = ja`, och ikonen får en streckad ram.
* **Sidan** är `<kommun>/<organ>/lokalbehov.html`, länkad från organets
  sida. Den följer målsidan (ADR-0050): sammandrag, urval, tidslinje med
  en rad per behov och en kolumn per år, och ett kort per behov. Varje
  fas är en ikon med egen form som länkar till källans sida. Stilen och
  skriptet är målsidans, med en liten egen stil för ikonerna.

### Consequences

* Good, eftersom varje steg går att kontrollera med ett klick, också när
  det står i ett annat organs dokument.
* Good, eftersom ett behov som försvinner ur nämndens listor syns som ett
  spår som tar slut, utan att sidan säger varför.
* Good, eftersom målsidans stil, skript och mandatperioder återanvänds.
* Bad, eftersom filen skrivs på för hand varje år, och servicenämndens
  projekt måste kopplas till behoven för hand.
* Bad, eftersom en sida utan ikon ett år inte skiljer mellan "inget
  hände" och "det står inte i poolen". Sidan säger det, men visar det
  inte per år, som målsidan gör med luckor.
* Bad, eftersom ett dokument som flyttas eller konverteras om med en
  annan text fäller raderna och stoppar webbplatsbygget, som för
  målfilen. Det gäller nu också andra organs dokument.

### Confirmation

`tests/test_lokalbehov.py` prövar läsningen, kontrollerna, sidan och
bygget med en påhittad kommun, och att Kungsbackas fil går igenom
kontrollen mot poolen.

## Pros and Cons of the Options

### A – En rad per steg, källor från alla organ

* Good, eftersom lokalplanen, startbeslutet och leveransen bara står i
  andra organs dokument.
* Good, eftersom ett år kan ha flera steg och samma steg flera källor.
* Bad, eftersom länkarna går utanför organets egen del av poolen.

### B – Bara nämndens egna dokument

* Good, eftersom sidan blir organets egen, som målsidan.
* Bad, eftersom nämnden inte får någon återrapport, så leveransen syns
  inte: tekniksalen på Elof Lindälv står bara i servicenämndens bokslut.

### C – En rad per behov och år

* Good, eftersom raden liknar tabellen på sidan.
* Bad, eftersom ett startbeslut eller ett bokslut inte följer
  lokalbehovets år, och en cell skulle behöva flera källor.

### D – Kod letar upp lokalbehoven

* Good, eftersom nya år kommer med av sig själva.
* Bad, eftersom behoven heter olika i nämndens lista, i budgeten och hos
  servicenämnden, och kopplingen är en bedömning som kod inte kan göra
  pålitligt.

## More Information

Projektägaren bad om sidan efter genomgången av GA:s lokalbehov inför
nämndens möte 2026-10-22. Agenten föreslog i fas 0 en rad per händelse,
källor från alla organ och tolkade kopplingar märkta. Projektägaren bad
sedan om en tabell med ett behov per rad och ett år per kolumn, där
ikoner visar var behovet är i faserna och länkar till dokumenten som
belägg, och om att kopiera målsidans modell. Det blev tidslinjen, korten
och sammandraget.

`pagar` kom till under arbetet: projektägaren ville se både det som är
gjort och det som är på gång, och flera källor säger att arbete pågår
utan att något beslut eller bokslut finns, som servicenämndens
månadsvisa redovisning av projekten och nämndens delårsrapport.

`forslag` kom till efter granskningen, som visade att förslaget till
mötet 2026-10-22 stod som nämndens lokalbehov fast protokollet inte fanns.
Projektägaren ville ändå se dagens lokalbehov på sidan, så förslaget fick
en egen fas i stället för att vänta.

En prioritet som är ett ord, som "aktualiserade" när nämnden 2025 tog
med Kompetenscentrum och Marios gata utöver de nya prioriteringarna,
visas med första bokstaven i ikonen och hela ordet i pekrutan.
