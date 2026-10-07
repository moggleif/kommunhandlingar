# Arkitektur

Det här beskriver hur poolen är tänkt att byggas. Inget av det är kod än;
när koden kommer är det koden som gäller och dokumentet rättas efter den.
*Varför* står i [docs/decisions/](decisions/).

## Flödet

```
kommuner/<kommun>.toml
        │
        ▼
1. upptäck   adaptrar per plattform  →  kandidatlista: organ, datum, typ, URL,
                                         källa, källnyckel
        │
        ▼
2. hämta och konvertera, ett dokument i taget
             jämför med front matter →  hoppa över, eller:
             artig HTTP-klient        →  PDF i en temporär fil utanför repot
             konvertering             →  .md + tabeller som .csv, PDF:en raderas
        │
        ▼
3. indexera                            →  index över alla dokument, luckor och versioner
```

Varje steg är ett eget kommando. Steg 1 och 3 läser bara föregående stegs
utdata; steg 2 läser kandidatlistan och dessutom poolens front matter, som
är tillståndet. Kandidatlistan skrivs till en arbetskatalog utanför repot
och tas fram på nytt vid varje körning.

### Inkrementell körning

Hur och varför står i
[ADR-0004](decisions/0004-inkrementell-korning-poolen-ar-tillstandet.md).

- **Poolen är tillståndet.** Det finns ingen separat tillståndsfil. Steg 2
  läser front matter i `data/<kommun>/` och slår upp varje kandidat på
  `kallnyckel` och `tidigare_kallnycklar`.
- **Adressen är signalen.** Vilka kandidater som hämtas står i K8. Adressen
  jämförs som sträng; adaptern ger alltid samma form av samma adress.
- **Upptäckten ger högst en kandidat per källnyckel.** Finns filen på flera
  adresser väljer adaptern den som gäller, annars skulle körningarna
  turas om att hämta varandras adresser. Valet är stabilt: en ny kopia av
  oförändrat innehåll, till exempel en ny ögonblicksbild i Internet
  Archive, ger inte en ny kandidat. Hur Wayback-adaptern väljer avgörs när
  den skrivs.
- **PDF:en finns bara medan dokumentet behandlas.** Den hämtas till en
  temporär fil utanför repot och raderas när dokumentet är konverterat,
  även om konverteringen misslyckas.
- **Tabellerna först, `.md` sist.** Tabellkatalogen ersätts som helhet, så
  att inga tabeller från en äldre version blir kvar. Sedan skrivs `.md`
  till en temporär fil i samma katalog, med ett namn som inte slutar på
  `.md`, som byter namn till den rätta. Avbryts körningen
  emellan står nya tabeller bredvid den gamla `.md`; dess `kalla_url` är
  då fortfarande den gamla, så nästa körning gör om dokumentet. En sådan
  körning checkas aldrig in (se nedan).
- **Det som en gång tagits in tas inte bort** (K12,
  [ADR-0007](decisions/0007-poolen-ar-en-ogonblicksbild.md)). Ett
  dokument står kvar när det försvinner ur källan, och historiken på
  `main` skrivs inte om.
- **Ett misslyckat hämtningsförsök** skriver aldrig över en fullständig
  `.md`. Har dokumentet ingen ger försöket en `.md` med kvalitet
  `ej-hamtad`, försökets tid i `hamtad` och orsaken i `fel` (K6); den bär
  också dokumentets plats. Den filen skrivs om bara när `fel` eller
  `kalla_url` ändras, så att en körning utan ändringar inte ger några
  diffar.

### Ordningen kandidaterna tas i

Hur och varför står i
[ADR-0010](decisions/0010-ordningen-organ-for-organ.md). Beteendet står i
K13.

- **Organ för organ, i `[[organ]]`-listans ordning** i
  `kommuner/<kommun>.toml`. Listans ordning är prioriteringen; det finns
  inget eget fält för den.
- **Inom ett organ:** protokoll, kallelser, övriga dokument, handlingar.
  Den ordningen står i koden och är densamma för alla kommuner.
- **Inom en typ:** det äldsta sammanträdet först.
- Ordningen beror bara på konfigurationen och kandidaternas egna
  uppgifter, så samma kandidatlista tas alltid i samma ordning.

### Körning och incheckning

Hur och varför står i
[ADR-0006](decisions/0006-schemalagd-korning-i-actions-och-data-direkt-till-main.md).
Vad en körning gör när budgeten tar slut, när kontrollerna faller och när
två startas står i K11.

- **Pipelinen är ett kommando** som inte vet var det körs. GitHub Actions
  startar det varje natt och för hand (`workflow_dispatch`), i en
  `concurrency`-grupp utan `cancel-in-progress`. Gruppen håller högst en
  körning i kö; en senare start ersätter den som väntar.
- **Varje körning börjar från en ren utcheckning av `main`.**
- **Tidsbudget, räknat från jobbets start.** Efter 5 timmar startas inget
  nytt dokument. Efter 5 timmar och 30 minuter läggs det pågående
  dokumentet åt sidan: dess tabellkatalog och temporära fil tas bort om
  de inte finns på `main`, och annars återställs de dit. Dokumentet nämns
  i jobbets sammanfattning, och körningen går vidare till kontrollerna.
  Resten av tiden fram till Actions gräns på 6 timmar per jobb är till
  för kontrollerna och pushen. Budgeten är vår egen och följer GitHubs
  gräns ([Actions limits](https://docs.github.com/en/actions/reference/limits),
  kontrollerat 2026-10-07); ändrar GitHub gränsen ändras budgeten.
- **Datakontrollerna körs innan något pushas.** Har `main` fått nya
  commits under körningen läggs körningens commit ovanpå och kontrollerna
  körs igen med koden från `main`. Blir det en konflikt eller faller
  kontrollerna pushas ingenting.
- **En push med Actions egen token startar inga workflows**
  ([GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token), kontrollerat 2026-10-07), så
  `kontroll.yml` körs inte på datacommiten. Kontrollerna i jobbet är de
  enda den får.

Datakontrollerna, i körningen och i CI:

- Inga binärer utom små testfixturer (ADR-0001).
- Varje `.md` under `data/` har front matter enligt
  [Front matter](#front-matter).
- Sökvägen stämmer med front matter: kommun, organ, år, datum, löpnummer,
  typ och namn enligt [Katalogstruktur](#katalogstruktur).
- Varje `.tabeller/`-katalog har sin `.md`, och varje CSV i den följer
  [Tabeller](#tabeller).
- Inga temporära filer finns under `data/`.

Bara i körningen, eftersom en vanlig PR ändrar kod och dokument: att
körningen bara har ändrat filer under `data/`.

## Datamodell

```
Kommun ── Organ (KF, KS, nämnd, utskott)    giltighetsperiod, föregångare
            └── Sammanträde (datum, löpnummer om flera samma dag)
                  └── Dokument (kallelse | handlingar | protokoll | bilaga)
                        │   namn, källnyckel, ärenden (diarienummer)
                        └── Version (sha256, hämtad, källa)
```

- Organ är data, inte kod: de byter namn och slås ihop.
- **Identitet** ([ADR-0003](decisions/0003-dokumentets-identitet-och-datamodell.md)).
  Ett dokument identifieras av sin plats i modellen – organ, datum,
  löpnummer, typ och namn – och känns igen på adapterns källnyckel
  (Sitevisions nod-id, Episervers adress) när adressen eller filnamnet
  ändras. En ny sha256 är en ny version och skriver över filen;
  git-historiken är versionshistoriken.
- Platsen bestäms första gången källnyckeln hittas och följer sedan
  källnyckeln. `<lopnr>` används när två sammanträden hålls samma dag.
  `<namn>` används alltid för bilagor och handlingar uppdelade per ärende,
  och annars bara när platsen redan är upptagen. Reglerna står i ADR-0003.
- `<namn>` bildas ur källans rubrik eller filnamn: små bokstäver, å och ä
  blir `a`, ö blir `o`, andra diakritiska tecken tas bort, allt som inte är
  bokstav eller siffra blir bindestreck, flera bindestreck i rad blir ett,
  och bindestreck först och sist tas bort. Namnet kortas till högst 80
  tecken, vid sista bindestrecket om det finns ett. Blir namnet tomt, eller
  ger två rubriker samma namn, får dokumentet ett löpnummer som namn: `2`,
  `3`, …
- Ärendet är ett attribut, `arenden` i [front matter](#front-matter).
  Diariet är en källa till mötesdokument, inte till egna dokument.

## Katalogstruktur

```
src/kommunhandlingar/
  adaptrar/        en modul per plattform (sitevision, wayback, ciceron, …)
  hamtning/        artig HTTP-klient
  konvertering/    pdf → md, tabeller, OCR-reserv, kvalitetsmått
  index/
kommuner/<kommun>.toml
hamtning.toml
data/<kommun>/<organ>/<år>/<datum>[-<lopnr>]/<typ>[-<namn>].md
data/<kommun>/<organ>/<år>/<datum>[-<lopnr>]/<typ>[-<namn>].tabeller/<sida>-<nr>.csv
scripts/          verktyg för utvecklingen, t.ex. storlekskontrollen
tests/fixtures/
```

## Kommunkonfigurationen

Hur och varför står i
[ADR-0008](decisions/0008-kommunkonfigurationen-i-toml.md). En kommun är en
fil, `kommuner/<kommun>.toml`, och filnamnet är `kommun` i front matter.
Filen läses med `tomllib`. Exemplet är påhittat:

```toml
namn = "Exempelby kommun"

[[organ]]
id = "bun"
namn = ["Barn- och ungdomsnämnden", "Förskole- och skolnämnden"]
fran = 2019-01-01
# foregangare = ["…"]       # id för organ i samma fil

[[kalla]]
adapter = "sitevision"
# … adapterns egna fält, till exempel startadresser

[[kalla.monster]]
typ = "protokoll"
regex = '^Protokoll för (?P<organ>.+?)\s+(?P<ar>\d{4})-(?P<manad>\d{2})-(?P<dag>\d{2})'
```

| Fält                   | Betyder                                                      |
| ---------------------- | ------------------------------------------------------------ |
| `namn`                 | Kommunens namn.                                              |
| `organ.id`             | Organets katalog i `data/` och `organ` i front matter.       |
| `organ.namn`           | Alla namn källorna använt för organet, minst ett.            |
| `organ.fran`, `till`   | Giltighetsperioden, som datum. Ett utelämnat värde är öppet åt det hållet. |
| `organ.foregangare`    | Id för organ som gick upp i det här (datamodellen). Varje id finns i filen. |
| `kalla.adapter`        | Adaptern som läser källan.                                   |
| `kalla.monster`        | Hur adaptern översätter en rubrik, ett filnamn eller en sökväg till organ, datum och typ. |
| `monster.regex`        | Ett reguljärt uttryck med de namngivna grupperna `organ`, `ar` (fyra siffror), `manad` och `dag`, och ibland `typ`. |
| `monster.typ`          | Dokumenttypen, när uttrycket inte har gruppen `typ`.         |

- **Id** för kommun och organ är katalognamn: små bokstäver a–z, siffror
  och bindestreck.
- **Källorna står i prioritetsordning.** Varje adapter anger vilka fält
  den har utöver `adapter` och `monster`; de beskrivs här när adaptern
  skrivs.
- **Datumet** byggs av grupperna `ar`, `manad` och `dag`, så att ordningen
  och skiljetecknen i källan står i mönstret och inte i koden.
- **Mönstren prövas i ordning** var som helst i texten, och det första
  som matchar gäller, också när det sedan inte ger någon kandidat.
- **Ett organnamn** jämförs med organens `namn` utan hänsyn till
  versaler och med flera blanksteg i rad som ett. Bara organ vars
  giltighetsperiod omfattar datumet räknas.
- **Ingen kandidat** blir det av en rubrik som inget mönster matchar, ett
  organnamn som inget organ har på datumet, ett datum som inte finns eller
  inte har fyrsiffrigt år, och en typ som inte är `kallelse`,
  `handlingar`, `protokoll` eller `bilaga` (utan hänsyn till versaler).
  Var och en nämns i körningens sammanfattning.
- **Körningen stoppas innan något hämtas** när filen inte följer
  schemat: ett fält som varken schemat eller adaptern har, ett id som
  inte är ett katalognamn eller som två organ delar, ett organ utan
  namn, en föregångare som inte finns, ett mönster vars grupper inte är
  `organ`, `ar`, `manad`, `dag` och högst `typ`, ett mönster med både
  eller ingen av gruppen och fältet `typ`, och två organ med samma namn
  och överlappande giltighetsperiod.
- **Ett organ som byter namn** får ett namn till. Ett organ som ersätts av
  ett nytt blir ett nytt organ, med det gamla som föregångare; de kan ha
  samma namn om perioderna inte överlappar.

`hamtning.toml` i roten gäller alla kommuner: User-Agent och det minsta
intervallet mellan anrop till samma värd (K10). Intervallet är ett och
detsamma, och HTTP-klienten håller det för varje värd för sig, över alla
kommuner i körningen; en ny kommun på en ny värd ändrar alltså inte
filen. Fälten bestäms när klienten skrivs.

`docs/kallor/<kommun>.md` beskriver hur kommunen publicerar, vad som är
belagt och hur, vad som är att verifiera och kända luckor. Organ,
adresser och mönster står i kommunfilen; källbeskrivningen länkar dit i
stället för att upprepa dem. Exempeladresser som belägg får stå kvar.

## Front matter

```yaml
---
kommun: kungsbacka
organ: ga
datum: 2025-10-16
lopnr: null
typ: protokoll
namn: null
kallnyckel: sitevision:18.4ac81f8819a0f459fef1dd70
tidigare_kallnycklar: []
arenden: [GA-2024-00194]
kalla_url: https://…/Protokoll….pdf
sha256: 3f9a…
bytes: 812345
sidor: 14
hamtad: 2026-10-06T15:40:12+02:00
konverterad: 2026-10-06T15:40:31+02:00
pipeline: kommunhandlingar <version> / <verktyg> <version> …
kvalitet: ocr
fel: null
kvalitet_per_sida: [ok, ok, ocr, tabell-osaker, …]
tal_obekraftade: [3]
---
```

Det här avsnittet äger schemat; värdena står i varje dokuments front
matter. Varje fält finns alltid, och ett fält som inte har något värde är
`null`.

| Fält                   | Betyder                                                      | `null` när |
| ---------------------- | ------------------------------------------------------------ | ---------- |
| `kommun`               | Kommunens id, kommunfilens namn utan `.toml`.                | aldrig |
| `organ`                | Organets id i kommunfilen.                                   | aldrig |
| `datum`                | Sammanträdets datum, `ÅÅÅÅ-MM-DD`.                           | aldrig |
| `lopnr`                | Sammanträdets löpnummer samma dag (ADR-0003).                | sökvägen saknar löpnummer |
| `typ`                  | `kallelse`, `handlingar`, `protokoll` eller `bilaga`.        | aldrig |
| `namn`                 | `<namn>` i sökvägen (ADR-0003).                              | sökvägen saknar namn |
| `kallnyckel`           | Adapterns källnyckel (ADR-0003).                             | aldrig |
| `tidigare_kallnycklar` | Källnycklar dokumentet haft tidigare (K9); `[]` när inga.     | aldrig |
| `arenden`              | Diarienummer; `[]` när dokumentet inte rör något ärende.      | det inte är känt |
| `kalla_url`            | Adressen originalet hämtades från, eller försöktes hämtas från. | aldrig |
| `sha256`               | Originalets sha256.                                          | `ej-hamtad` |
| `bytes`                | Originalets storlek i byte.                                  | `ej-hamtad` |
| `sidor`                | Originalets antal sidor.                                     | `ej-hamtad`, eller filen gick inte att öppna |
| `hamtad`               | Tiden för hämtningen; för `ej-hamtad` det första misslyckade försöket. | aldrig |
| `konverterad`          | Tiden för konverteringen.                                    | `ej-hamtad` |
| `pipeline`             | Poolens version och verktygen som läste dokumentet (nedan).  | aldrig |
| `kvalitet`             | Dokumentets kvalitet (nedan).                                | aldrig |
| `fel`                  | Kort orsakskod, till exempel `http-404`, `kapad` eller `krypterad`. | originalet hämtades och gick att öppna |
| `kvalitet_per_sida`    | Varje sidas kvalitet, i sidordning (nedan).                  | `ej-hamtad`, eller filen gick inte att öppna |
| `tal_obekraftade`      | Sidor vars tal inte är bekräftade (nedan); `[]` när alla är det. | `ej-hamtad`, eller filen gick inte att öppna |

`kvalitet` och `fel` är tillsammans dokumentets status (K6). När kvalitet
är `ej-hamtad` finns inget original, och härkomsten är källänken,
källnyckeln och försöket
([ADR-0004](decisions/0004-inkrementell-korning-poolen-ar-tillstandet.md)).

### Konvertering och kvalitet

Reglerna och trösklarna står här; varför de valdes, och mätningarna bakom
dem, står i [ADR-0005](decisions/0005-konvertering-verktyg-ocr-och-kvalitet.md).
Text och tabeller läses med pdfplumber. OCR görs med Tesseract och svensk
modell på sidor renderade med pypdfium2.

Text och tal märks var för sig. `kvalitet` och `kvalitet_per_sida` säger
hur texten lästes; `tal_obekraftade` säger på vilka sidor talen inte är
bekräftade och därför inte ska användas som data.

Varje sida får en kvalitet:

| Sida             | Betyder                                                          |
| ---------------- | ---------------------------------------------------------------- |
| `ej-konverterad` | Sidan skulle läsas med OCR, men Tesseract kände inte igen några ord eller medelsäkerheten nådde inte tröskeln. Ingen text från sidan skrivs. |
| `ocr`            | Sidan lästes med OCR. Den får inga CSV:er.                       |
| `tabell-osaker`  | Textlagret är läst, men sidan har en osäker tabell.              |
| `ok`             | Textlagret är läst, och sidans tabeller är säkra.                |
| `tom`            | Sidan har inga tecken och är, renderad, nästan helt vit.          |

Sidan prövas i den här ordningen, och den första regeln som stämmer gäller:

1. **Tom:** inga tecken, och sidan renderad i 72 dpi har högst 0,5 %
   pixlar som inte är vita → `tom`. Det gäller också en tom inskannad
   baksida och en sida med bara en ram eller ett streck.
2. **Skanning:** den yta som bilderna tillsammans täcker är minst 90 % av
   sidan, och sidan har färre än 50 synliga tecken. Osynlig text
   (renderingsläge 3, som ett tidigare OCR-lager har) räknas inte, och en
   stämpel eller ett diarienummer i synlig text hindrar inte → OCR.
3. **Oläsligt textlager:** mer än 1 % av textlagrets tecken är oläsliga
   (`(cid:…)`, styrtecken, ersättningstecken) → OCR.
4. **Inga tecken:** sidan har bilder eller ritad grafik men inga tecken →
   OCR, så att text som gjorts om till kurvor inte försvinner tyst.
5. **Annars** läses textlagret, hur kort det än är, och sidan blir `ok`
   eller `tabell-osaker`.

- **OCR:** sidan renderas och läses av Tesseract med svensk modell
  (`swe`). Upplösningen och förberedelsen av bilden bestäms när
  konverteringen skrivs, mot den inskannade blanketten som testfixtur. Säkerheten är medelvärdet av Tesseracts säkerhet för de
  ord den känt igen (poster med säkerhet −1 räknas inte). Är den minst 70
  blir sidan `ocr`. Annars, och när Tesseract inte känner igen några ord,
  blir den `ej-konverterad`: den har innehåll, en karta, ett foto eller
  handskrift, som inte blev text. På en OCR-sida letas inga tabeller;
  hela sidans text är OCR-text, och den läses för sammanhangets skull,
  inte som data. Talen i OCR-texten står omärkta i texten; att de inte är
  bekräftade syns bara i `tal_obekraftade`.
- **`tal_obekraftade`** listar, med sidnummer från 1, varje sida vars tal
  inte är bekräftade: varje sida som är `ocr`, varje sida som är
  `ej-konverterad`, eftersom talen på den inte är lästa, och varje sida
  med textlager där något tecken är oläsligt, eftersom tecknet kan ha
  varit en siffra. Övriga tal i ett läst textlager är bekräftade: de är
  de tal PDF:en innehåller. Det säger ingenting om vilken cell de hör
  till; det avgörs av reglerna för tabeller nedan. Talen på en sida som
  inte står i listan går att använda som data, och en tom lista betyder
  att det gäller varje tal i dokumentet.
- **En säker tabell** är avgränsad av ritade linjer: streck och fyllda
  rektanglar som är högst 2 punkter breda eller höga. Bredare fyllda ytor,
  som färgade rader och kolumner, är inga linjer. Tabellen har minst två
  rader och två kolumner, och varje ord inom dess yta har sin mittpunkt i
  en cell. En säker tabell skrivs som CSV enligt [Tabeller](#tabeller).
- **En osäker tabell** är minst tre talrader på sidan, var som helst
  utanför de säkra tabellerna. Raderna tas ur sidans text med bevarad
  uppställning, och fält skiljs åt av två eller fler mellanslag. En
  talrad har minst två fält som är tal. Ett tal är ett heltal, där
  tusentalen får skiljas med mellanslag eller hårt mellanslag, med
  eventuellt minustecken (`-`, `−` eller `–`), decimalkomma och
  procenttecken, med eller utan mellanslag före: `2027`, `-1 845`, `21,33`, `53%`,
  `53 %`, men inte `2026-08-11` eller `2023-00686`. En osäker tabell
  skrivs inte som CSV. Varje följd av talrader, där bara tomma rader får
  stå emellan, står i `.md` som ett eget kodblock märkt `osaker-tabell`,
  med uppställningen bevarad, och sidan blir `tabell-osaker`.

Dokumentets kvalitet följer av sidorna, och den första regeln som stämmer
gäller. Den sämsta sidan avgör:

| Dokument             | När                                                          |
| -------------------- | ------------------------------------------------------------ |
| `ej-hamtad`          | Filen gick inte att hämta (ADR-0004).                        |
| `ej-konverterad`     | Filen gick inte att öppna, eller ingen sida är `ok`, `tabell-osaker` eller `ocr`. |
| `delvis`             | Någon sida är `ej-konverterad`.                              |
| `ocr`                | Någon sida är `ocr`.                                         |
| `text-utan-tabeller` | Någon sida är `tabell-osaker`.                               |
| `full`               | Alla sidor är `ok` eller `tom`.                              |

När filen inte gick att öppna står orsaken i `fel`: `krypterad` (filen
kräver lösenord för att öppnas; ett lösenord som bara begränsar utskrift
eller ändring hindrar inte), `trasig-pdf` (också en fil utan sidor) eller
`inte-pdf`; vilka fält som då är `null` står i
[Front matter](#front-matter). Har filen sidor men ingen av dem gick att
läsa är `fel` `null`, och `sidor`, `kvalitet_per_sida` och
`tal_obekraftade` visar sidorna som de är.

`pipeline` är poolens version ur `pyproject.toml` följd av de verktyg som
läste dokumentet, med version: alltid pdfplumber och pdfminer.six, och
pypdfium2 samt Tesseract och språkmodellens version när någon sida
lästes med OCR, till exempel
`kommunhandlingar 0.1.0 / pdfplumber 0.11.10 / pdfminer.six 20260107 /
pypdfium2 5.14.0 / tesseract 5.3.4 swe 4.1.0`. För `ej-hamtad` har inget
verktyg läst dokumentet, och `pipeline` är bara poolens version. En fil
som inte gick att öppna har lästs av pdfplumber och pdfminer.six.
Versionen höjs när en ändring i konverteringen ändrar vad den skriver.

## Tabeller

Hur och varför står i
[ADR-0009](decisions/0009-tabellernas-harkomst-och-csv-format.md). Varje
säker tabell blir en CSV i dokumentets tabellkatalog, som heter som
`.md` men med `.tabeller` i stället för `.md`. Ett dokument utan säkra
tabeller har ingen tabellkatalog.

- **Filnamnet** är `<sida>-<nr>.csv`, utan inledande nollor: sidnumret
  från 1, och tabellens nummer på sidan från 1, uppifrån och ned och vid
  samma höjd från vänster till höger. `3-2.csv` är den andra tabellen på
  sidan 3.
- **Härkomsten** är front matter i tabellkatalogens `.md`. Tabellerna
  har ingen egen. Står sidan i `tal_obekraftade` är talen i dess CSV:er
  inte bekräftade; det syns bara i `.md`.
- **Formatet** är CSV som i [RFC 4180](https://www.rfc-editor.org/rfc/rfc4180),
  men med radslut LF i stället för CRLF: UTF-8 utan BOM och komma som
  skiljetecken. Varje rad har lika många fält. Cellerna står som de
  lästes: inget tal görs om, decimalkommat står kvar, och en radbrytning
  i en cell står kvar inom citattecken. En tom cell är tom, och en
  sammanslagen cells text står i dess första cell, uppe till vänster,
  medan cellerna den täcker är tomma. Den första raden är tabellens
  första rad och tolkas inte som rubrik.
- **Datakontrollen** prövar att varje CSV heter så, att numren på en
  sida följer på varandra utan lucka, och att sidan finns och är `ok`
  eller `tabell-osaker`.
