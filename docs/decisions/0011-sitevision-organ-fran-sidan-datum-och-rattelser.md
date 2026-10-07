---
status: accepted
date: 2026-10-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Sitevision-adaptern tar organet från sidan, datumet ur filnamnet eller rubriken, och avvikande datum rättas i kommunfilen

## Context and Problem Statement

Den första adaptern läser Kungsbackas mötessidor på Sitevision
([#25](https://github.com/moggleif/kommunhandlingar/issues/25)). Hur
sidorna är byggda står i
[docs/kallor/kungsbacka.md](../kallor/kungsbacka.md). Varje fil har två
handskrivna uppgifter om sig själv: filnamnet och rubriken för mötet den
står under. De säger inte alltid samma sak, och ett dokuments plats
bestäms första gången det hittas och ändras sedan inte
([ADR-0003](0003-dokumentets-identitet-och-datamodell.md)). Ett fel
datum blir alltså kvar.

Var tar adaptern organ, datum och typ ifrån, och vad gör den när
uppgifterna inte stämmer?

## Decision Drivers

* **Hellre märka än gissa** (AGENTS.md). Ett dokument på fel plats är
  värre än ett som syns som ej taget.
* **Inget hårdkodat om en kommun.** Rubrikens form, månadernas namn och
  rättelserna är kommunens, inte kodens.
* **Ingen kod för säkerhets skull.** Varje regel ska motiveras av filer
  som finns.
* **Tomt är inte noll.** En fil som inte blir kandidat ska synas.

### Vad siffrorna säger

De 17 mötessidorna hade 2026-10-07 1 672 filer (unika nod-id:n). Läst
med kommunfilens mönster blir de:

| Fall | Filer |
| --- | ---: |
| Typ och datum i filnamnet, samma som rubriken eller rubriken utan datum | 1 613 |
| Typ i filnamnet, datum bara i rubriken | 24 |
| Typ i filnamnet, och filnamnets datum skiljer sig från rubrikens | 25 |
| Ingen av de fyra typerna | 10 |

* **Datum bara i rubriken:** "Valnämnden protokoll 24-11-11",
  "… protokoll § 22", "Protokoll GA januari.signerad.pub".
* **Avvikande datum:** ingen av uppgifterna har rätt varje gång.
  Filnamnet har rätt i "22 januari 2024" med filer 2025-01-22, och i
  Gymnasium & Arbetsmarknads filer från 2025-04-24 under "27 mars 2025".
  Rubriken har rätt i Individ & Familjeomsorgs "protokoll 2026-09-19"
  under "17 september 2026" (protokollet självt säger 2026-09-17) och i
  Byggnadsnämndens arbetsutskott, där kallelsen säger 4 april men
  rubriken "5 april 2024 (flyttat från 4 april)".
* **Ingen typ:** 9 är budget, årsredovisning, delårsrapport, nämndbudget,
  särredovisning och avfallsföreskrifter, och 1 är ett enskilt ärende.
  Protokollsutdrag med bara "§" i namnet och revisionens
  sammanträdesanteckningar räknas som protokoll (nedan).
* **Organnamnen i filnamnen** har stavfel ("Arbetmarknad",
  "arbetutskott") och kortformer ("GA"). Sidan säger alltid vilket organ
  det är.

## Considered Options

* A – Filnamnet avgör organ, datum och typ, som mönstren redan beskrevs
* B – Sidan ger organet och filnamnet typen; datumet ur filnamnet, annars
  ur rubriken; avvikande datum rättas i kommunfilen
* C – Som B, men filnamnets datum vinner när de avviker
* D – Som B, men rubrikens datum vinner när de avviker

## Decision Outcome

Valt alternativ: "B – Sidan ger organet och filnamnet typen; datumet ur
filnamnet, annars ur rubriken; avvikande datum rättas i kommunfilen",
eftersom det tar in nästan alla filer utan att gissa när källans egna
uppgifter säger emot varandra.

* **Organet** är sidans. Kommunfilen anger vilken sida som hör till
  vilket organ. Ett mönster för Sitevision har därför ingen grupp
  `organ`.
* **Typen** kommer ur filnamnet genom kommunfilens mönster. Mönstren får
  sakna datum, och då kommer datumet ur rubriken.
* **Datumet** kommer ur filnamnet när mönstret har ett. Annars läses
  rubriken med kommunfilens rubrikmönster, och månadens namn slås upp i
  kommunfilens månadslista. Det är ADR-0008:s skäl att ompröva ("datum
  med månadens namn"), och det löses här utan att ändra ADR-0008:s
  beslut: grupperna `ar`, `manad` och `dag` står kvar, och `manad` får
  vara ett namn ur listan.
* **Avviker filnamnets datum från rubrikens** blir filen ingen kandidat
  och nämns i sammanfattningen, om inte kommunfilen har en rättelse:
  källnyckeln och det rätta datumet. Rättelsen gäller före både filnamn
  och rubrik. Kungsbackas 25 rättelser är belagda med datumet i
  kallelsens eller protokollets egen text, eller med rubrikens
  uppgift om att mötet flyttats.
* **En fil på flera ställen** blir en kandidat: det första stället som
  ger en kandidat gäller, och stället som inte gjorde det nämns inte.
* **Revisionens "sammanträdesanteckningar" och protokollsutdrag med bara
  "§"** blir protokoll genom mönster i kommunfilen.
* **Budget, årsredovisning och liknande tas inte in.** De har ingen av de
  fyra typerna (K2) och nämns i sammanfattningen.
* **Två sammanträden samma dag** har inte setts på sidorna, och adaptern
  ger inga löpnummer. Det avgörs när ett fall finns.
* **Adaptern läser HTML som text** och hämtar ingenting själv. Den artiga
  HTTP-klienten (K10) och kommandot som hämtar sidorna och skriver
  kandidatlistan är ett eget arbete
  ([#29](https://github.com/moggleif/kommunhandlingar/issues/29)). Där hör också filer som `robots.txt`
  stänger hemma: kandidaten finns, och hämtningen nekas (K6).

### Consequences

* Bra, eftersom 1 662 av 1 672 filer blir kandidater, och alla andra
  syns i sammanfattningen med sin orsak.
* Bra, eftersom stavfel i organnamnen inte kostar något: organet står
  aldrig i filnamnet för den här adaptern.
* Bra, eftersom inget datum gissas. Varje avvikelse är antingen rättad av
  en människa, med belägg, eller syns.
* Dåligt, eftersom en ny avvikelse håller filen utanför poolen tills
  någon skrivit en rättelse.
* Dåligt, eftersom rättelserna är kunskap om enskilda filer i
  kommunfilen. De är kommunfakta, inte kod, men listan kan växa.
* Dåligt, eftersom en fil som står under fel möte men har samma datum i
  rubrik och filnamn inte upptäcks. Inget sådant fall har setts.
* Neutralt, eftersom ett mönster utan datum gör rubriken till den enda
  källan för datumet, och rubrikens fel då inte märks. Det gäller 24
  filer, och rubrikerna har bara setts ha fel när filnamnet också har ett
  datum att jämföra med.

### Confirmation

Testerna läser alla 17 sparade mötessidor i `tests/fixtures/` med
`kommuner/kungsbacka.toml` och jämför utfallet med siffrorna ovan:
antalet kandidater, varje fil som inte blev kandidat och dess orsak, att
rättelserna gäller, att en fil under två möten blir en kandidat, och att
båda formerna av fillista läses. Granskaren kontrollerar att inget om
Kungsbacka står i koden.

## Pros and Cons of the Options

### A – Filnamnet avgör allt

* Bra, eftersom det är det arkitekturen redan beskrev och kräver minst
  ny kod.
* Dåligt, eftersom varje stavning av varje organ måste stå som ett namn i
  kommunfilen, och nya stavfel faller bort.
* Dåligt, eftersom de 24 filerna utan datum i namnet aldrig blir
  kandidater.
* Dåligt, eftersom rubrikens rätta datum inte används när filnamnet har
  fel.

### B – Sidan, filnamnet och rubriken, med rättelser

* Bra, eftersom varje uppgift tas där den är säkrast: organet från
  sidan, typen ur filnamnet, datumet ur båda.
* Bra, eftersom en avvikelse aldrig avgörs av koden.
* Dåligt, eftersom kommunfilen får tre nya fält för adaptern och en lista
  med rättelser.

### C – Filnamnets datum vinner

* Bra, eftersom inga rättelser behövs, och filnamnet har rätt oftast.
* Dåligt, eftersom fem filer hamnar på fel datum för gott: hos
  Individ & Familjeomsorg, Byggnadsnämndens arbetsutskott och Service.

### D – Rubrikens datum vinner

* Bra, eftersom rubriken är sidans egen ordning.
* Dåligt, eftersom 20 filer hamnar på fel datum för gott, bland dem
  ett helt möte för Förskola & Grundskola ett år fel.

## More Information

### Diskussionen

1. **Issuet** listade fyra frågor: båda formerna av fillista, avvikande
   datum och typ, andra dokument på mötessidorna, och filer som
   `robots.txt` stänger.
2. **Agenten räknade igenom alla sidor** i fas 0 (tabellen ovan) och
   rekommenderade B, att budget och liknande står utanför, och att
   HTTP-klienten blir ett eget arbete så att adaptern kan testas helt mot
   sparade sidor.
3. **Det som avgjorde avvikelserna** var att platsen bestäms en gång
   (ADR-0003). Varken C eller D klarar alla fall, och ett fel blir kvar.
   Rättelser kostar en rad per fil och gör varje undantag till ett
   beslut med belägg.
4. **Ägarens beslut** 2026-10-07: alla rekommendationer.
5. **Agentens belägg för rättelserna** 2026-10-07: kallelsen eller
   protokollet för varje avvikande möte hämtades och datumet lästes ur
   texten. Handlingarna har samma datum som mötets kallelse. För
   Byggnadsnämndens arbetsutskott säger kallelsen 4 april och rubriken
   att mötet flyttades till 5 april; rättelsen är 5 april, så att mötets
   alla dokument hamnar på samma datum. Revisionens anteckningar från ett
   tvådagarsmöte (19–20 augusti 2024) får den första dagen. Avfallsföreskrifterna
   har också olika datum i filnamn och rubrik, men ingen typ, och behöver
   ingen rättelse.
6. **Ett belägg för att organet ska tas från sidan** kom under
   implementationen: "Sammanträdesprotokoll Nämnden för Förskola &
   Grundskolas arbetsutskott 21 augusti" står på nämndens sida, och
   protokollet självt är nämndens, 2024-08-21. Filnamnet hade gett fel
   organ.
7. **En fil med två typer i namnet**, "Kallelse och handlingar för möte
   …", blir den typ som står först, `kallelse`.

### När beslutet bör omprövas

* När rättelserna blir så många att de inte går att belägga för hand.
* När ett organs filer börjar stå på ett annat organs sida.
* När två sammanträden hålls samma dag.
* När budget och liknande dokument behövs i poolen.
