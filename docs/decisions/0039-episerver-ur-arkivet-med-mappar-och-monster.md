---
status: proposed
date: 2026-10-13
decision-makers: projektägaren
consulted: AI-agenten
---

# Episerver-generationerna läses ur arkivet med organens mappar och mönster för sökvägen, och ett sammanträde får inte samma typ från två plattformar

## Context and Problem Statement

Kungsbackas webbplats hade två Episerver-generationer före Sitevision,
2013–2017 och 2017–2022. De finns bara i Internet Archive
([källorna, avsnitt 2](../kallor/kungsbacka.md#2-internet-archive-wayback)).
Det finns ingen mötessida att läsa. Organ, typ och år står i filernas
sökväg, och datumet står i filnamnet i en rad olika former:
`Dagordning_18 septemberi 2013_GV.pdf`, `GV protokoll 20 nov.pdf`,
`210120.pdf`, `kallelse-220223.pdf`. Några filer saknar datum helt
(`1.pdf`, `kallelse-jan.pdf`). Mappen för 2021 har också möten från
2022. Åren 2021–2022 finns dessutom redan i poolen från
Sitevision-generationen ([ADR-0018](0018-wayback-sist-nyast-forst-och-bara-luckor.md)).
Där har samma möte andra filer och andra källnycklar.

Ägaren vill ha Gymnasium & Arbetsmarknads dokument ur de här
generationerna först ([#88](https://github.com/moggleif/kommunhandlingar/issues/88)).
Det som redan finns ska inte hämtas igen, och det som inte gick att
hämta ur Sitevision-kopiorna ska prövas härifrån.

Hur läses filerna, och hur hindras samma möte från att komma in två gånger?

## Decision Drivers

* **Inget hårdkodat om en kommun.** Mappar och datumformer står i
  kommunfilen.
* **Hellre märka än gissa.** En fil vars datum inte går att läsa blir
  ingen kandidat, utom med en rättelse som är belagd i filens egen text
  (som i [ADR-0011](0011-sitevision-organ-fran-sidan-datum-och-rattelser.md)).
* **Samma möte en gång.** Ett sammanträde ska inte få samma protokoll
  två gånger, en gång per plattform.
* **Enkelt först.** Bara det som Gymnasium & Arbetsmarknad behöver nu.

## Considered Options

* A – En adapter, `episerver`, för båda generationerna: organens mappar,
  och var sin lista med mönster för typ och datum mot sökvägen under
  mappen
* B – Två adaptrar, en per generation
* C – Sitevision-adapterns `monster`, där varje mönster ger både typ och
  datum
* D – En lista i kommunfilen med varje fil, dess typ och datum

## Decision Outcome

Valt: A. Generationerna skiljer sig bara i adress och filnamn, och det står
i kommunfilen. Var sin lista för typ och datum gör listorna korta. I C
skulle varje typkälla behöva ett mönster för varje datumform.

* **Mapparna.** `mappar` anger organets mappar som adressprefix utan
  protokoll. Ett organ utan mappar läses inte, på samma sätt som
  `wayback` i [ADR-0027](0027-arkivet-slas-pa-per-organ.md). Ett organ med
  ett äldre namn, som Gymnasie och Vuxenutbildning, kan ha sin mapp
  under det nuvarande organet. Ägaren valde det för `ga`.
* **Filerna.** CDX-tjänsten ger varje PDF under mappen. Samma fil under
  http och https, med och utan `www`, är en fil. Källnyckeln är
  `episerver:` och adressen utan protokoll, `www` och port, med sökvägen
  kodad på ett enda sätt. Kodningen gör att nyckeln aldrig innehåller
  `, `, som skiljer nycklarna i `tidigare_kallnycklar` åt. Den största
  kopian tas, och vid lika storlek den äldsta.
* **Typ och datum.** Mönstren prövas i ordning mot sökvägen under mappen,
  till exempel `Protokoll/2013/GV protokoll 20 nov.pdf`. Det första
  typmönster som matchar ger typen. Ordningen bestämmer därför om mappen
  eller filnamnet går först. Det första datummönster som matchar ger
  datumet. Ett tvåsiffrigt år är 2000-talets. En rättelse går före
  mönstren.
* **Samma typ från en annan plattform.** En kandidat ur arkivet hämtas
  inte om sammanträdet redan har ett fullständigt dokument av samma typ
  med en källnyckel från en annan plattform. Plattformen är källnyckelns
  första del.
* **Ett misslyckat försök från en annan plattform** ger plats åt
  kandidaten. Den hämtas till platsen, och den gamla nyckeln blir en
  tidigare källnyckel. Det undantaget går före regeln i
  [ADR-0003](0003-dokumentets-identitet-och-datamodell.md) att båda
  nycklarna blir dokument när båda finns i listan.

### Consequences

* Bra, eftersom ett organ till är en rad under `mappar`.
* Bra, eftersom ett protokoll som Sitevision-kopian inte gav (`kapad`)
  kan komma från Episerver-kopian.
* Dåligt, eftersom en fil vars datum inte går att läsa kräver en rättelse
  för hand, med belägg ur filen. För Gymnasium & Arbetsmarknad var det sju
  filer.
* Dåligt, eftersom handlingar som är en fil per ärende, som hos
  kommunstyrelsen och fullmäktige, ännu inte får ett namn var
  ([ADR-0003](0003-dokumentets-identitet-och-datamodell.md)). Den första
  tar platsen utan namn och de andra får namn efter filen. Gymnasium &
  Arbetsmarknad har en fil per möte. Frågan avgörs innan ett sådant organ
  får mappar.
* Dåligt, eftersom regeln om samma typ jämför med alla dokument i poolen
  för varje kandidat ur arkivet. Med några tusen dokument tar det någon
  sekund.

### Confirmation

`tests/test_episerver.py` prövar kommunfilens fält och hur typ och
datum läses. `tests/test_episerver_arkiv.py` prövar att samma fil under
flera adresser blir en kandidat med rätt kopia, och att en fil utan datum
och en mapp utan svar nämns. `tests/test_plattformar.py` prövar att ett
möte som redan har typen inte får den igen, och att ett misslyckat försök
från en annan plattform tas över. Upptäckten provades mot arkivet från
GitHub Actions 2026-10-13.

## Pros and Cons of the Options

### A – En adapter med mappar och två listor med mönster

* Bra, eftersom båda generationerna ryms och resten står i kommunfilen.
* Dåligt, eftersom kommunfilens schema får två nya fält, `typer` och
  `datum`.

### B – En adapter per generation

* Bra, eftersom varje adapter bara känner en adressform.
* Dåligt, eftersom koden blir dubbel. Skillnaden är data, och data hör
  hemma i kommunfilen.

### C – Sitevision-adapterns `monster`

* Bra, eftersom schemat redan finns.
* Dåligt, eftersom typen ibland står i mappen och ibland i filnamnet,
  och datumet i fem former. Varje kombination skulle bli ett eget mönster.

### D – En lista med varje fil

* Bra, eftersom inget gissas.
* Dåligt, eftersom arkivet har omkring 2 900 filer från de här
  generationerna. Listan skulle bli lång och skrivas för hand.

## More Information

Ägaren valde 2026-10-13 att börja med Gymnasium & Arbetsmarknad, att lägga
Gymnasie och Vuxenutbildning under `ga` i stället för att göra det till
ett eget organ, att inte leta efter något äldre än 2013, att inte hämta
det som redan finns, och att pröva det som inte gick att hämta från det
här stället.

Agenten listade organets filer i arkivet från GitHub Actions, eftersom
molnmiljön inte når `web.archive.org`. Resultatet blev 83 PDF:er:

* 20 från 2013–2014 i den äldre generationen.
* 63 från 2018, 2020 och 2021 i `globalassets`.

Agenten läste första sidan av de sju filer vars namn saknade ett läsbart
datum, och av två filer i handlingarnas mapp med "kallelse" i namnet. De
två senare var kallelsen med alla handlingar. Därför går
handlingarnas mapp före filnamnet i typmönstren.

Agenten föreslog först ett eget organ för Gymnasie och Vuxenutbildning,
med `ga` som efterföljare. Ägaren valde att lägga det direkt under `ga`.
Datamodellen skiljer därför inte de två nämnderna åt. Rubriken i varje
dokument gör det.
