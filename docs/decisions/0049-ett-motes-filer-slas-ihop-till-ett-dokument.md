---
status: accepted
date: 2026-10-14
decision-makers: projektägaren
consulted: AI-agenten
---

# Ett mötes filer av samma typ hos Episerver slås ihop till ett dokument, med delarnas adresser och sha256 i front matter

## Context and Problem Statement

I Episervers `globalassets`-generation (2017–2022) är handlingarna en
fil per ärende. Kommunstyrelsen hade cirka 480 sådana filer 2018–2019
([täckningen](../kallor/kungsbacka.md#täckning)). I den äldre
generationen förekommer också flera filer för samma möte och typ.
[ADR-0039](0039-episerver-ur-arkivet-med-mappar-och-monster.md) gör
varje fil till ett dokument: den första tar platsen utan namn, och de
andra får namn efter filen. ADR-0039 säger att frågan ska avgöras innan
organ med en fil per ärende får mappar
([#159](https://github.com/moggleif/kommunhandlingar/issues/159)).

Hur blir ett möte som består av många filer ett dokument i poolen?

## Decision Drivers

* **Ett möte, en fil per typ.** Ägaren vill att mötet finns i en
  Markdown-fil i den struktur poolen har, oavsett hur många PDF:er det
  är.
* **Varje textfil bär sin härkomst.** Varje dels adress och sha256 ska
  gå att se.
* **Tomt är inte noll.** Ett möte där en del saknas får inte se helt ut.
* **Enkelt först.** Bara Episerver-generationerna behöver det nu.

## Considered Options

* A – Delarna slås ihop till en PDF som konverteras som ett dokument
* B – Varje del konverteras för sig, och texterna läggs efter varandra
* C – Varje fil är ett dokument, som i ADR-0039

## Decision Outcome

Valt: A, eftersom konverteringen, sidnumren, tabellerna och kvaliteten
då fungerar som för vilket dokument som helst.

* **Upptäckten.** Ett organs filer i samma mapp i en Episerver-källa med
  samma datum och typ blir en kandidat i delar. Mappen hör till gruppen,
  eftersom nedlagda nämnder som fanns samtidigt läggs under samma organ
  och har var sin mapp. Delarna ordnas efter sökvägen, där en följd av
  siffror jämförs som ett tal. Källnyckeln är mappens, mötets och typens,
  `episerver:<mapp><datum>/<typ>`, så att den inte beror på vilken del som
  kom först. En ensam fil är som förut.
* **Hämtningen.** Delarna hämtas en i taget och slås ihop med pypdfium2,
  som redan finns i poolen. En kapad del eller en del som inte går att
  hämta gör hela dokumentet `ej-hamtad`, och nästa körning försöker
  igen. En del som inte går att öppna gör dokumentet `ej-konverterad`
  med orsaken i `fel`.
* **Front matter.** `kalla_url`, `sha256` och `bytes` blir listor, en per
  del i delarnas ordning. Den hopslagna filen blir inte byte för byte
  densamma två gånger, så sha256 står per del.
* **Platsen.** Ett dokument i delar placeras som andra dokument
  ([ADR-0003](0003-dokumentets-identitet-och-datamodell.md)) och fyller
  bara luckor som andra kandidater ur arkivet
  ([ADR-0018](0018-wayback-sist-nyast-forst-och-bara-luckor.md)). Gymnasium
  & Arbetsmarknads dokument ur Episerver är redan en fil per möte och typ,
  så inget i poolen blir en del.
* **Sitevision** rörs inte. Där är handlingarna redan en fil per möte.

Det ersätter konsekvensen om handlingar per ärende i ADR-0039.

### Consequences

* Bra, eftersom ett möte blir ett dokument med alla sidor i ordning.
* Bra, eftersom konverteringen inte ändras.
* Dåligt, eftersom `kalla_url`, `sha256` och `bytes` får två former, en
  adress eller en lista. Den som läser front matter måste känna till
  båda.
* Dåligt, eftersom ordningen följer filnamnen. Ett filnamn som inte
  följer ärendets nummer hamnar på fel plats i dokumentet. Sidorna finns
  ändå kvar.
* Dåligt, eftersom en del som alltid är kapad gör hela mötet `ej-hamtad`
  och hämtas om varje natt.
* Dåligt, eftersom två filer i samma mapp för samma möte och typ som inte
  hör ihop, till exempel två protokoll från två sammanträden samma dag,
  slås ihop. Episerver skiljer inte sådana sammanträden åt i sökvägen.
* Dåligt, eftersom en fil som innehåller de andra, till exempel en
  kallelse med alla handlingar, slås ihop med dem, så att texten står två
  gånger.
* Dåligt, eftersom ett möte som finns i båda generationerna blir två
  dokument, som i ADR-0039.
* Dåligt, eftersom en del som arkivet får senare inte hämtas när
  dokumentet redan är fullständigt: arkivet fyller bara luckor. Webbplatsen
  finns inte kvar, så arkivet får sällan nya kopior.

### Confirmation

`tests/test_sammanslagning.py` prövar att filerna blir en kandidat i
rätt ordning och att två mappar inte slås ihop, att delarna blir ett
dokument med listorna i front matter, att en kapad del eller en del som
inte går att hämta gör hela dokumentet `ej-hamtad`, att en del som inte
går att öppna märks, och att kvaliteten avgör mot en annan plattform åt
båda hållen (ADR-0048). `tests/test_figurer.py` prövar att delarna slås
ihop och prövas för tolkningen.

## Pros and Cons of the Options

### A – En hopslagen PDF

* Bra, eftersom sidnummer, tabeller och kvalitet följer en sida i
  dokumentet.
* Dåligt, eftersom sha256 för den hopslagna filen inte är stabil.

### B – Delarna konverteras var för sig

* Bra, eftersom varje del har sin egen kvalitet.
* Dåligt, eftersom sidnumren, tabellernas namn och kvaliteten per sida
  måste räknas om när texterna läggs ihop. Det blir ny kod för varje
  fält.

### C – Ett dokument per fil

* Bra, eftersom ingen kod ändras.
* Dåligt, eftersom ett möte blir hundratals dokument, och ägaren vill ha
  ett.

## More Information

Ägaren svarade 2026-10-13 att ärendefilerna ska slås ihop till en
Markdown-fil, "spelar ingen roll om mötet är i en pdf eller 100".

En provkörning mot arkivet 2026-10-14 läste alla 38 mappar: 2 204
kandidater, en mapp per nedlagd nämnd, och Funktionsstöds kallelser är
nämndens egna. Den visade också att arkivets prefix tar med syskonmappar
som `Kommunstyrelsens arbetsutskott/` för `Kommunstyrelsen/`; de filerna
hoppas nu över (K23).
