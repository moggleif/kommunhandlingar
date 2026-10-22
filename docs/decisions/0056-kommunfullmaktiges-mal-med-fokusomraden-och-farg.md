---
status: proposed
date: 2026-10-22
decision-makers: projektägaren
consulted: AI-agenten
---

# Kommunfullmäktiges mål står på en egen målsida, med fokusområdena under sina mål och färgen i källan som bedömning

## Context and Problem Statement

Målsidan finns för Nämnden för Gymnasium & Arbetsmarknad
([ADR-0044](0044-namndens-mal-och-direktiv-las-ur-dokumenten-och-skrivs-for-hand.md),
[ADR-0045](0045-omdopta-mal-grupperas-protokollet-gar-fore-och-status-blir-ikoner.md),
[ADR-0050](0050-malsidan-visas-som-tidslinje-och-malkort.md),
[ADR-0051](0051-tidslinjen-visar-varje-rubrik-och-nya-formuleringar.md)).
Projektägaren vill ha samma sida för kommunfullmäktige
([#183](https://github.com/moggleif/kommunhandlingar/issues/183)).
Kommunstyrelsen har inga egna mål utan arbetar direkt med fullmäktiges,
enligt revisionen i årsredovisningarna 2024 och 2025 (KF 2025-04-08 och
2026-04-14, Bilaga 4), så den får ingen egen sida.

Fullmäktiges mål ser annorlunda ut än nämndens. Det finns fem
kommunövergripande mål, och under varje mål två till fyra fokusområden.
Det är fokusområdena som bedöms, och årsredovisningen visar bedömningen
med färg: grön för i mål eller nära målet, gul för på väg mot målet och
röd för långt kvar till målet. Färgen följer inte med in i texten; bara
trendpilen gör det. Målen bedöms i en mening ("Den samlade bedömningen är
att vi inte nått målet"), som i årsredovisningens två spalter ofta hamnar
blandad med annan text. Fokusområdena står i tabeller där pilen hamnar
mitt i texten och ord delas med `-<br>`, och budgeten sätter målen i
versaler. Budgeten och uppföljningen skriver dessutom ibland samma
fokusområde på olika sätt samma år ("god vård och omsorg" och "god
omsorg").

Hur ska fokusområdena, färgen och den nya texten in på sidan, utan att
sidan blir en annan än nämndens?

## Decision Drivers

* **Samma sida som nämndens**, så att den som läser känner igen den
  (projektägarens val).
* **Varje uppgift bär sin härkomst**, och bygget prövar att texten står
  på källans sida.
* **Hellre märka än gissa.** En bedömning som inte står i texten ska
  synas som det.
* **Ingen kod för säkerhets skull.** Det ska vara samma kod för alla
  organ, utan något om kommunfullmäktige.

## Considered Options

* A – Fokusområden som ett eget slag med ett huvudmål, under sitt mål i
  tidslinjen och i målets kort; färgen avläses ur PDF:en som bedömning
* B – Fokusområdena som vanliga mål, var för sig, och målen som grupper
* C – Bara de fem målen, med fokusområdena i formuleringen
* D – Som A, men utan färgen: fokusområdena står utan bedömning

## Decision Outcome

Valt: A, eftersom den visar fullmäktiges egen indelning i mål och
fokusområden med en bedömning per fokusområde, med samma tidslinje, kort
och kontroller som nämndens sida.

* **Två nya slag**: `kommunmål` och `fokusområde`. Målfilen får kolumnen
  `huvudmal`, som är kommunmålets rubrik för ett fokusområde och tom för
  allt annat. Huvudmålet ska stå på källans sida och vara ett kommunmål
  utan grupp i filen, och samma rubrik har alltid samma huvudmål.
* **Färgen är bedömningen.** AI-agenten läser färgen per fokusområde ur
  PDF:en på källans sida, och skriver bedömningen utan status. Kortets
  historik säger "enligt färgen i källan", och sidans metodtext förklarar
  färgerna och att de inte står i texten. Ett mål får en status bara där
  källans samlade bedömning står sammanhängande i texten.
* **Under sitt mål.** I tidslinjen står fokusområdena direkt under sitt
  kommunmål, indragna och märkta för skärmläsare. Varje fokusområde har
  ett eget kort inuti målets kort, så att grupperingen av omdöpta
  fokusområden (ADR-0045) och rubrikraderna (ADR-0051) fungerar som för
  nämndens mål.
* **Antalet per år** har en kolumn och en linje per slag som finns för
  organet, och varje spår räknas en gång per år, också när budgeten och
  uppföljningen skriver det på olika sätt.
* **Två rubriker i samma spår samma år** stoppar bygget bara när de står
  i samma dokument, eftersom budgeten och uppföljningen får skriva samma
  mål olika.
* **Texten jämförs** också utan `<br>`, avstavning över en radbrytning,
  mjukt bindestreck, tankstreck, pilar och privata tecken ur
  symbolfonter. Versalerna räknas, utom när källan sätter hela texten i
  versaler.

### Consequences

* Good, eftersom fullmäktiges mål går att följa år för år med samma sida
  som nämndens.
* Good, eftersom en bedömning som bara står i färg syns, och är märkt
  som avläst ur färgen.
* Bad, eftersom färgen inte går att pröva i bygget. Den som vill
  kontrollera en bedömning får öppna PDF:en.
* Bad, eftersom målens egen status ofta saknas: årsredovisningens
  spalter blandas ihop i texten, och då står den bedömningen inte med.
* Neutral, eftersom sidan börjar 2022: årsredovisningarna före dess har
  inte text i poolen.

### Confirmation

`tests/test_fokusomraden.py` prövar läsningen med pilar, avstavning och
versaler, felen för huvudmålet och samma dokument, att fokusområdena står
under sitt mål i tidslinjen och i kortet, texten för färgen och antalet
per slag.

## Pros and Cons of the Options

### A – Eget slag med huvudmål, färgen avläst

* Good, eftersom indelningen är källans.
* Good, eftersom samma kod bygger nämndens och fullmäktiges sidor.
* Bad, eftersom det kräver en kolumn till i målfilen och färgen avläst
  för hand.

### B – Fokusområdena som vanliga mål

* Good, eftersom ingen ny kolumn behövs.
* Bad, eftersom grupperna är till för mål som bytt rubrik
  ([ADR-0045](0045-omdopta-mal-grupperas-protokollet-gar-fore-och-status-blir-ikoner.md)),
  och fokusområden som bytt rubrik skulle inte gå att gruppera.
* Bad, eftersom det inte syns vilket mål ett fokusområde hör till.

### C – Bara de fem målen

* Good, eftersom sidan blir kort.
* Bad, eftersom det är fokusområdena som bedöms, och bedömningarna då
  inte står med.

### D – Utan färgen

* Good, eftersom allt på sidan prövas av bygget.
* Bad, eftersom nästan inget fokusområde då har en bedömning, och sidan
  inte visar det årsredovisningen säger.

## More Information

Projektägaren valde i fas 0 att bara ta med kommunfullmäktige, att läsa
färgen ur PDF:en, ett kort per mål med fokusområdena i, och direktiven
till alla nämnder, och bad om att målen skulle kopplas ihop som för
nämnden. AI-agenten grupperade fokusområden som bytt rubrik, till exempel
"god vård och omsorg" i budgeten och "god omsorg" i uppföljningen, och
märkte kopplingarna som tolkade, eftersom källan inte säger att det är
samma fokusområde.

Fokusområdena ur årsredovisningen 2022 (KF 2023-04-04) och
delårsrapporten 2023 (KF 2023-11-07) står inte med än: PDF:erna finns
bara i webbarkivet, så färgen har inte gått att läsa.
