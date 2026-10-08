# Arkitektur

Det här beskriver hur poolen är tänkt att byggas. Upptäckten (steg 1)
och hämtningen och konverteringen (steg 2) finns som kod; indexet (steg 3)
gör det inte än. Där koden finns är det koden som gäller, och dokumentet
rättas efter den.
*Varför* står i [docs/decisions/](decisions/).

## Flödet

```
kommuner/<kommun>.toml
        │
        ▼
1. upptäck   adaptrar per plattform  →  kandidatlista: organ, datum, typ, URL,
                                         källa, källnyckel, filnamn
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
- **En äldre version av poolen konverteras om** (K8,
  [ADR-0019](decisions/0019-omkonvertering-efter-poolens-version.md)).
  Ett fullständigt dokument vars `pipeline` börjar med en annan version
  av poolen än den som körs hämtas igen från `kalla_url` och konverteras
  om, efter alla andra kandidater i samma lista. Det är versionen som avgör, och den
  höjs när konverteringen ändrar vad den skriver (se
  [Konvertering och kvalitet](#konvertering-och-kvalitet)), så en
  höjning konverterar om hela poolen under de närmaste nätterna. PDF:en
  sparas inte mellan körningarna; den hämtas igen.
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

Vilken ordning står i K13, och hur och varför i
[ADR-0010](decisions/0010-ordningen-organ-for-organ.md). Ordningen
mellan organ är `[[organ]]`-listans ordning i kommunfilen; det finns
inget eget fält för den. Ordningen inom ett organ står i koden och är
densamma för alla kommuner.

### Körning och incheckning

Hur och varför står i
[ADR-0006](decisions/0006-schemalagd-korning-i-actions-och-data-direkt-till-main.md)
och, för hur datat når `main`,
[ADR-0015](decisions/0015-nattkorningen-pa-egen-gren-och-pr.md).
Vad en körning gör när budgeten tar slut, när kontrollerna faller och när
två startas står i K11.

- **Pipelinen är ett kommando** som inte vet var det körs.
  `.github/workflows/nattkorning.yml` startar det varje natt och för hand
  (`workflow_dispatch`), i en `concurrency`-grupp utan
  `cancel-in-progress`. Gruppen håller högst en körning i kö; en senare
  start ersätter den som väntar. Jobbet kör upptäckten och steg 2 för
  varje kommunfil i `kommuner/`.
- **Varje körning börjar från en ren utcheckning av `main`.**
- **Tidsbudget, räknat från jobbets start** (`hamta --start`). Efter 5
  timmar startas inget nytt dokument. Efter 5 timmar och 30 minuter
  avbryts det pågående dokumentet (`SIGALRM`), utom medan det skrivs: då
  skrivs det klart. Ett avbrutet dokument har inte skrivit något, eftersom
  allt skrivs efter hämtning och konvertering och PDF:en ligger utanför
  repot. Det nämns i sammanfattningen, och körningen går vidare till
  kontrollerna. Resten av tiden fram till Actions gräns på 6 timmar per
  jobb är till för kontrollerna och pushen. Budgeten är vår egen och följer
  GitHubs gräns ([Actions limits](https://docs.github.com/en/actions/reference/limits),
  kontrollerat 2026-10-07); ändrar GitHub gränsen ändras budgeten.
- **Datakontrollerna körs innan något pushas**, och sedan att bara filer
  under `data/` har ändrats och att inget av dem är binärt. Faller något
  pushas ingenting.
- **Körningen pushar en egen gren**, `nattkorning/<datum>-<körningens id>`,
  och datat når `main` genom en PR, där "Ren kod och tester" kör samma
  kontroller. Har körningen inte ändrat något pushas ingen gren. Mergen
  till `main` bygger om webbplatsen.

Datakontrollerna, i körningen och i CI
(`python -m kommunhandlingar.datakontroll data`, utom binärerna):

- Inga binärer utom små testfixturer (ADR-0001).
- Varje `.md` under `data/` har front matter enligt
  [Front matter](#front-matter).
- Sökvägen stämmer med front matter: kommun, organ, år, datum, löpnummer,
  typ och namn enligt [Katalogstruktur](#katalogstruktur).
- Varje `.tabeller/`-katalog har sin `.md`, och varje CSV i den följer
  [Tabeller](#tabeller).
- Inga temporära filer finns under `data/`.
- Front matter hänger ihop: `ej-hamtad` har ett `fel` och inga
  originalfält, `sidor` stämmer med `kvalitet_per_sida`, och varje sida
  som är `ocr` eller `ej-konverterad` står i `tal_obekraftade`.
- Figurerna och tolkningarna hänger ihop, och varje tal i en tolkad CSV
  står i sidans text, enligt [Tolkade figurer](#tolkade-figurer).

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
  konfiguration.py kommunfilen läses och kontrolleras
  schema.py        kontrollerna av fält och värden i kommunfilen
  fel.py           konfigurationsfel och "ingen kandidat"
  monster.py       mönstren: typ och datum ur en text
  kandidat.py      kandidaten och ordningen (K13)
  adaptrar/        en modul per publiceringsplattform (sitevision, ciceron, …)
                   eller arkiv (wayback);
                   sitevision_html.py läser mötessidan, sitevision.py tolkar den
  upptack.py       steg 1: hämtar källsidorna och skriver kandidatlistan
  hamtning/        artig HTTP-klient: robots.txt, intervall och nya försök
  hamta.py         steg 2: tar kandidatlistan in i poolen, ett dokument i taget
  behandla.py      steg 2 för en kandidat: hoppa över, hämta, konvertera, skriva
  pool.py          poolens front matter, uppslagen på källnyckel och sökväg
  plats.py         sökvägen och namnet för ett nytt dokument (ADR-0003)
  skrivning.py     `.md` och tabellkatalog, tabellerna först och `.md` sist
  frontmatter.py   front matter läses och skrivs
  tidsbudget.py    budgetens hårda gräns, som inte avbryter en skrivning
  datakontroll*.py datakontrollerna av allt under data/ (K11)
  tolkning.py      arbetslistan och renderingen av figurerna (K15)
  konvertering/    pdf → md: sidans väg, text, tabeller och kvalitet
  webbplats/       statussidorna och startsidan för GitHub Pages
kommuner/<kommun>.toml
hamtning.toml
data/<kommun>/<organ>/<år>/<datum>[-<lopnr>]/<typ>[-<namn>].md
data/<kommun>/<organ>/<år>/<datum>[-<lopnr>]/<typ>[-<namn>].tabeller/<sida>-<nr>.csv
data/<kommun>/<organ>/<år>/<datum>[-<lopnr>]/<typ>[-<namn>].tabeller/<sida>-<nr>.tolkad.csv
scripts/          verktyg för utvecklingen, t.ex. storlekskontrollen
tests/fixtures/
```

## Kommunkonfigurationen

Hur och varför står i
[ADR-0008](decisions/0008-kommunkonfigurationen-i-toml.md). En kommun är en
fil, `kommuner/<kommun>.toml`, och filnamnet är `kommun` i front matter.
Filen läses med `tomllib`. Ordningen på `[[organ]]` är den ordning
organen hämtas i (K13). Exemplet är påhittat:

```toml
namn = "Exempelby kommun"

[[organ]]
id = "bun"
namn = ["Barn- och ungdomsnämnden", "Förskole- och skolnämnden"]
fran = 2019-01-01
# foregangare = ["…"]       # id för organ i samma fil

[[kalla]]
adapter = "…"
# … adapterns egna fält, till exempel startadresser (Sitevision nedan)

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
| `kalla.manader`        | Månadernas namn i källan, januari först. Utelämnas när källan skriver månaden med siffror. |
| `monster.regex`        | Ett reguljärt uttryck med de namngivna grupperna `organ`, `ar` (fyra siffror), `manad` och `dag`, och `typ`, var och en när källan har den. |
| `monster.typ`          | Dokumenttypen, när uttrycket inte har gruppen `typ`.         |

- **Id** för kommun och organ är katalognamn: små bokstäver a–z, siffror
  och bindestreck.
- **Källorna står i prioritetsordning.** Varje adapter anger vilka fält
  den har utöver `adapter` och `monster`; de beskrivs här när adaptern
  skrivs. Med en enda adapter väljer konfigurationen den direkt; ett
  sätt att slå upp adaptrar kommer med den andra.
- **Datumet** byggs av grupperna `ar`, `manad` och `dag`, så att ordningen
  och skiljetecknen i källan står i mönstret och inte i koden. `manad` är
  siffror eller ett av namnen i `manader`, utan hänsyn till versaler.
- **Det ett mönster inte ger, ger adaptern ur källan.** Ett mönster har
  `ar`, `manad` och `dag` tillsammans eller inte alls, och gruppen `organ`
  bara när adaptern inte vet organet. Varifrån adaptern tar resten står
  under adaptern nedan.
- **Mönstren prövas i ordning** var som helst i texten, och det första
  som matchar gäller, också när det sedan inte ger någon kandidat.
- **Ett organnamn** jämförs med organens `namn` utan hänsyn till
  versaler och med flera blanksteg i rad som ett. Bara organ vars
  giltighetsperiod omfattar datumet räknas.
- **Ingen kandidat** blir det av en rubrik som inget mönster matchar, ett
  organnamn som inget organ har på datumet, ett datum som är ofullständigt,
  inte finns, inte har fyrsiffrigt år eller har ett okänt månadsnamn, och
  en typ som inte är `kallelse`, `handlingar`, `protokoll` eller `bilaga` (utan
  hänsyn till versaler). Var och en nämns i körningens sammanfattning.
- **Körningen stoppas innan något hämtas** när filen inte följer
  schemat: ett fält som varken schemat eller adaptern har, ett id som
  inte är ett katalognamn eller som två organ delar, ett organ utan
  namn, en föregångare som inte finns, ett mönster med en annan grupp än
  `organ`, `ar`, `manad`, `dag` och `typ`, med bara några av `ar`,
  `manad` och `dag` eller med en grupp adaptern inte tar, ett mönster med
  både eller ingen av gruppen och fältet `typ`, en månadslista som inte
  har tolv olika namn, ett värde av fel slag (text, lista, datum), och
  två organ med samma namn och överlappande giltighetsperiod.
- **Ett organ som byter namn** får ett namn till. Ett organ som ersätts av
  ett nytt blir ett nytt organ, med det gamla som föregångare; de kan ha
  samma namn om perioderna inte överlappar.

### Sitevision

Hur och varför står i
[ADR-0011](decisions/0011-sitevision-organ-fran-sidan-datum-och-rattelser.md).
Adaptern läser mötessidornas HTML, som den får som text. Varje möte är
en rubrik `<h3>` och varje år en `<h2>`, som i Kungsbackas mall. En
annan kommuns mall kan ha andra nivåer; då blir rubriknivån ett fält.
Mötets filer står antingen som länkar i filportleten
(`/download/18.<nod-id>/…`) eller som JSON i
`AppRegistry.registerInitialState`. Båda läses.

```toml
[[kalla]]
adapter = "sitevision"
manader = ["januari", "februari", …, "december"]
rubrik = '^(?P<dag>\d{1,2}) (?P<manad>[a-zåäö]+) (?P<ar>\d{4})'

[kalla.sidor]
bun = "https://exempelby.se/…/barn-och-ungdomsnamndens-sammantraden"

[kalla.rattelser]
"sitevision:18.1a2b3c" = 2025-04-24   # belägg: kallelsens datum
```

| Fält              | Betyder                                                         |
| ----------------- | --------------------------------------------------------------- |
| `kalla.sidor`     | Organets id och adressen till dess mötessida. Organet är sidans. |
| `kalla.rubrik`    | Ett reguljärt uttryck med grupperna `ar`, `manad` och `dag`, som läser mötesrubriken. |
| `kalla.rattelser` | Källnyckel och det rätta datumet, för filer vars filnamn och rubrik anger olika datum. |

- **Källnyckeln** är `sitevision:` och nod-id:t. Adressen är länkens
  eller JSON-postens `uri` som sidan skriver den, gjord absolut; båda
  formerna kodar sökvägen på samma sätt. Filnamnet är adressens sista del,
  avkodad.
- **Mönstren** prövas mot filnamnet och har ingen grupp `organ`.
- **Datumet** är rättelsens, om filen har en. Annars filnamnets, om
  mönstret har ett, och rubrikens annars. Anger filnamnet och rubriken
  olika datum blir filen ingen kandidat (K2). En rubrik som rubrikmönstret
  inte läser ("17 och 18 augusti 2026") ger inget datum, och filnamnets
  gäller ensamt. En rubrik som mönstret läser men vars datum inte finns
  eller vars månad är okänd ger ingen kandidat, som ett filnamn gör (K2).
- **En fil som står under flera möten** blir en kandidat: det första
  stället i sidans ordning som ger en kandidat gäller.

`docs/kallor/<kommun>.md` beskriver hur kommunen publicerar, vad som är
belagt och hur, vad som är att verifiera och kända luckor. Organ,
adresser och mönster står i kommunfilen; källbeskrivningen länkar dit i
stället för att upprepa dem. Exempeladresser som belägg får stå kvar.

## Hämtningen

Hur och varför står i
[ADR-0013](decisions/0013-artig-hamtning-och-kandidatlistan.md). Allt
som hämtas går genom HTTP-klienten i `hamtning/`, med bara
standardbiblioteket.

`hamtning.toml` i roten gäller alla kommuner:

| Fält         | Betyder                                                         |
| ------------ | --------------------------------------------------------------- |
| `user_agent` | User-Agent i varje anrop: vem vi är och hur vi nås.             |
| `intervall`  | Minsta antalet sekunder mellan anrop till samma värd, räknat från slutet av det förra. |

- **Intervallet** hålls för varje värd för sig, över alla kommuner i
  körningen; en ny kommun på en ny värd ändrar alltså inte filen.
- **`robots.txt`** hämtas en gång per värd och körning och läses enligt
  RFC 9309: gruppen för vår produkt (User-Agent fram till första `/` eller
  mellanslag) gäller, annars gruppen `*`; den längsta regel som träffar
  sökvägen med frågesträng avgör, och `Allow` vinner vid lika längd. `*`
  och `$` stöds, och reglerna procentkodas innan de jämförs. Svarar
  `robots.txt` 4xx, utom 429, gäller inga regler. Går den inte att hämta
  hämtas ingenting från värden. En stängd adress ger orsaken `robots`.
- **Nya försök** görs vid 429, 5xx, tidsgräns (60 sekunder), när servern
  stänger anslutningen utan svar och när svaret bryts av: efter 5, 10 och
  20 sekunder, eller den tid `Retry-After` anger, högst 300 sekunder.
  Efter det fjärde försöket är orsaken `http-<kod>`, `tidsgrans`,
  `tomt-svar` eller `avbrutet-svar`.
- **Inget nytt försök** görs vid andra 4xx och vid omdirigeringar, som
  inte följs, så att målet aldrig hämtas utan att prövas mot `robots.txt`
  och intervallet. Orsaken är `http-<kod>`. En server som inte går att nå
  ger `anslutning`, och en sida som inte går att avkoda `teckenkodning`.

### Kandidatlistan

`python -m kommunhandlingar.upptack kommuner/<kommun>.toml <arbetskatalog>`
läser `hamtning.toml` i samma repo som kommunfilen och stoppas om
arbetskatalogen ligger i repot. Det hämtar varje källsida, kör adaptern och skriver
`<arbetskatalog>/<kommun>.kandidater.json`: en lista i ordningen från
K13, en post per kandidat med fälten `organ`, `datum` (`ÅÅÅÅ-MM-DD`),
`typ`, `url`, `kalla`, `kallnyckel` och `filnamn`. Sammanfattningen
skrivs ut: antal kandidater per organ och varje fil som inte blev
kandidat, med orsak och källsida. En källsida som inte går att hämta
stoppar körningen innan listan skrivs.

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
hamtad: 2026-10-06T13:40:12+00:00
konverterad: 2026-10-06T13:40:31+00:00
pipeline: kommunhandlingar <version> / <verktyg> <version> …
kvalitet: ocr
fel: null
kvalitet_per_sida: [ok, ok, ocr, tabell-osaker, …]
tal_obekraftade: [3]
figurer: [5, 9]
tolkade: [5]
---
```

Det här avsnittet äger schemat; värdena står i varje dokuments front
matter. Varje fält finns alltid, och ett fält som inte har något värde är
`null`. Varje fält står på en egen rad, och en lista skrivs
inom hakparenteser på samma rad, som i exemplet.

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
| `figurer`              | Sidor som kan ha en figur ([Figurer](#figurer)); `[]` när inga. | `ej-hamtad`, filen gick inte att öppna, eller dokumentet konverterades före version 0.3.0 |
| `tolkade`              | Sidor som har tolkats ([Tolkade figurer](#tolkade-figurer)); `[]` när inga. | när `figurer` är `null` |

`kvalitet` och `fel` är tillsammans dokumentets status (K6). När kvalitet
är `ej-hamtad` finns inget original, och härkomsten är källänken,
källnyckeln och försöket
([ADR-0004](decisions/0004-inkrementell-korning-poolen-ar-tillstandet.md)).

### Konvertering och kvalitet

Reglerna och trösklarna står här; varför de valdes, och mätningarna bakom
dem, står i [ADR-0005](decisions/0005-konvertering-verktyg-ocr-och-kvalitet.md),
för tabellerna i [ADR-0016](decisions/0016-tabeller-utan-lodrata-linjer.md)
och för figurerna i [ADR-0017](decisions/0017-figurer-marks-och-tolkas-i-efterhand.md).
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
| `tabell-osaker`  | Textlagret är läst, men sidan har en osäker tabell, eller siffror ur en tabell med linjer som inte gick att läsa säkert. |
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

- **OCR:** sidan renderas med pypdfium2 i 300 dpi och gråskala, utan
  annan förberedelse, och läses av Tesseract med svensk modell (`swe`).
  Det läser den inskannade sidan i `tests/fixtures/pdf/` rätt; den är
  ren och rak, och upplösningen är ännu inte prövad mot riktiga
  skanningar. Säkerheten är medelvärdet av Tesseracts säkerhet för de
  ord den känt igen (poster med säkerhet −1 räknas inte). Är den minst 70
  blir sidan `ocr`. Annars, och när Tesseract inte känner igen några ord,
  blir den `ej-konverterad`: den har innehåll, en karta, ett foto eller
  handskrift, som inte blev text. Tesseract körs utan
  orienteringsdetektering, så en liggande skanning blir också
  `ej-konverterad`. Fallerar Tesseract på en sida, eller blir den inte
  klar på fem minuter, blir sidan `ej-konverterad` och felet skrivs ut;
  dokumentets övriga sidor behålls. Saknas Tesseract eller `swe` stoppas
  steg 2 innan något dokument läses, så att ingen sida märks
  `ej-konverterad` för att miljön saknar något. På en OCR-sida letas
  inga tabeller;
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
  rader och två kolumner, varje ord inom dess yta har sin mittpunkt i
  en cell, och ingen cell rymmer mer än ett tal. En cell rymmer mer än
  ett tal när
  - två rader i den var för sig är ett tal (med eller utan förtecken,
    decimalpunkt, parentes eller någon av enheterna nedan), ett ensamt streck, eller
    en etikett på ett eller två ord utan siffror följd av ett tal, som
    `4 078⏎4 054`, `(2 100)⏎1 978`, `4 078⏎varav bidrag⏎4 054` eller
    `Utfall 2022⏎50,1`;
  - en rad bara består av tal och streck, med enheterna `%`, `kr`, `tkr`,
    `mkr`, `mnkr`, `mdkr` och `st`, oavsett skiftläge, borträknade,
    mellanslag, parenteser och snedstreck med mellanslag omkring som
    skiljetecken, och de tillsammans inte är ett tal (en decimalpunkt
    räknas som decimalkomma), som `65,0 70,0`, `1 234 (1 150)`,
    `74 984 kr 80%` eller `4 078 -`; eller
  - två fält på samma rad i cellen var för sig är ett tal eller ett
    streck, med fälten avgränsade som i tabellerna utan lodräta linjer
    och ett tvetydigt mellanrum räknat som en gräns, som `120   135`.

  Två rader eller kolumner som linjerna inte skiljer åt hamnar annars i
  samma cell. En sådan tabell blir ingen CSV. Står en siffra ur den
  utanför de tabeller som lästs säkert, också när en del av den lästs
  som en tabell utan lodräta linjer, blir sidan `tabell-osaker`, och
  texten står kvar i sidans text.
- **En säker tabell utan lodräta linjer** läses ur de ord som står
  utanför tabellerna med linjer, enligt
  [Tabeller utan lodräta linjer](#tabeller-utan-lodrata-linjer).
- Båda sorterna skrivs som CSV enligt [Tabeller](#tabeller), numrerade
  tillsammans efter läget på sidan.
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
`kommunhandlingar 0.3.0 / pdfplumber 0.11.10 / pdfminer.six 20260107 /
pypdfium2 5.14.0 / tesseract 5.3.4 swe 4.1.0`. För `ej-hamtad` har inget
verktyg läst dokumentet, och `pipeline` är bara poolens version.
Språkmodellens version är paketet `tesseract-ocr-swe`:s version utan epok
och revision; går den inte att läsa ur paketsystemet står `okänd`. En fil
som inte gick att öppna har lästs av pdfplumber och pdfminer.six.
Versionen höjs när en ändring i konverteringen ändrar vad den skriver,
och bara då: varje höjning gör att hela poolen hämtas och konverteras om
([ADR-0019](decisions/0019-omkonvertering-efter-poolens-version.md)).
Verktygens versioner i `pipeline` ger ingen omkonvertering.

### Figurer

Varje sida som inte är `tom` prövas för figurer: diagram, kartor, scheman
och bilder. En sida som kan ha en figur står i `figurer`. Regeln får
hellre ta med en sida för mycket än missa en; den som tolkar sidan avgör
om det är en figur. Sidan står i `figurer` när något av det här gäller:

1. **En bild** täcker minst 2 % av sidan men mindre än 90 %. En mindre
   bild är oftast en logotyp, och en större är en skanning.
2. **Minst 8 ritade objekt** – kurvor, och rektanglar som är bredare
   och högre än 2 punkter, syns och inte har något tecken inom sig –
   ligger inom en rektangel som täcker minst 2 % av sidan. Ett vapen
   eller en ikon har många kurvor på en liten yta, och en tabell har
   linjer och rutor med text i.

Bilder och objekt med mittpunkten i en säker tabell räknas inte. En
rektangel syns när den har en kantlinje eller en fyllning som inte är
vit. En stapel med talet inuti räknas inte, så ett diagram med talen i
staplarna kan missas; ett diagram i en skanning hittas inte alls.

### Tabeller utan lodräta linjer

Hur och varför står i
[ADR-0016](decisions/0016-tabeller-utan-lodrata-linjer.md). Reglerna
gäller sidans ord utanför tabellerna med linjer, med koordinater i
punkter. Ett ord delas där teckenstorleken ändras, så att en upphöjd
fotnotssiffra inte blir en del av talet framför. En tabell som inte
uppfyller alla regler blir ingen CSV; dess talrader står kvar i texten
och blir en osäker tabell som förut.

1. **Rader:** orden grupperas efter överkanten, med 3 punkters tolerans
   som i pdfplumbers text med uppställning, och sorteras från vänster.
2. **Fält:** två ord i följd hör till samma fält när mellanrummet är
   högst en halv teckenhöjd (den högre av ordens höjd), och till olika
   fält när det är minst en teckenhöjd. Ett mellanrum däremellan är
   tvetydigt. Så skiljs tusentalsmellanrummet i `4 078` från mellanrummet
   mellan två kolumner.
3. **Tabellrad:** första fältet är en etikett med minst en bokstav, minst
   ett fält följer, och varje följande fält är ett tal (enligt
   definitionen ovan) eller ett ensamt streck (`-`, `−` eller `–`).
4. **Följd:** rader i följd som är tabellrader eller talrader, där en
   talrad har minst två fält som är tal, eller minst två ord som är tal
   när ett mellanrum är tvetydigt. Avståndet mellan två rader i följden
   är högst tre teckenhöjder. En tabell blir det bara om varje rad i
   följden är en tabellrad och minst tre av dem har två tal eller fler.
5. **Kolumner:** talen grupperas efter sin högerkant; de som ligger högst
   2 punkter från gruppens första hör till samma kolumn. Varje kolumn har
   minst två tal, varje streck står med högerkanten i linje med en
   kolumn, och kolumnerna överlappar inte varandra eller etiketterna:
   varje kolumns vänstra kant ligger till höger om föregående kolumns
   högra kant, och den första till höger om den etikett som slutar
   längst till höger. Består den första kolumnen bara av fyrsiffriga
   heltal, år eller koder, är den en kolumn med etiketter, och det som
   står till vänster är något annat, till exempel text i en spalt
   bredvid; då blir det ingen tabell.
6. **Rubrikrader:** raderna närmast ovanför, högst tre teckenhöjder
   ifrån raden under, tas med från tabellen och uppåt så länge raden inte
   är en tabellrad eller talrad, har minst ett fält i en kolumn, och
   varje fält utom ett första står med högerkanten i linje med en kolumn
   (högst 2 punkter ifrån) och börjar till höger om föregående kolumns
   högra kant, eller om den etikett som slutar längst till höger för den
   första kolumnen. Ett första fält som börjar till vänster om där den
   etiketten slutar, och slutar före den första kolumnen, är rubrikens
   etikett. Rubriken tas med bara om den översta
   rubrikraden har en rubrik i varje kolumn, och om raden ovanför den är
   en ensam etikett till vänster om kolumnerna, ligger längre bort, eller
   inte finns; annars tas ingen rubrikrad med, så att en rubrik aldrig
   blir halv.
7. **Ensam:** inget annat ord på sidan, inte heller i en tabell med
   linjer, får ha sin mittpunkt inom den rektangel som omsluter tabellens
   ord.

Varje rad i CSV:n är etiketten följd av en cell per kolumn, tom där
raden saknar värde. En rubrikrad har sin etikett i första cellen.
Cellerna är fältens ord med ett mellanslag emellan, som de står i
textlagret; inget tal görs om.

### Markdown-texten

Hur och varför står i
[ADR-0014](decisions/0014-markdown-texten-och-steg-2.md). Efter front
matter följer sidorna i ordning. Varje sida börjar med kommentaren
`<!-- sida N -->`, så att en sida i `kvalitet_per_sida` eller
`tal_obekraftade` går att hitta i texten.

- **Texten** är textlagret med bevarad uppställning (pdfplumber,
  `layout=True`). Raderna skrivs utan indrag, men mellanrummen inne i
  raden står kvar, så att två tal i följd inte flyter ihop. Flera tomma
  rader blir en.
- **En osäker tabell** står där den står på sidan, som ett kodblock märkt
  `osaker-tabell` med uppställningen kvar.
- **En säker tabell**, med eller utan lodräta linjer, står inte i sidans
  text. Den står efter texten, i
  sidans ordning, som en länk till sin CSV (`[Tabell 3-1](<namn>.tabeller/3-1.csv)`)
  följd av tabellen i Markdown. Där är första raden tabellhuvud, eftersom
  Markdown kräver ett; `|` skrivs `\|` och en radbrytning `<br>`.
- **En sida utan text** (`tom`, `ej-konverterad`) har bara sin kommentar.
  En `.md` för ett dokument som inte gick att hämta eller öppna har ingen
  text alls.

## Steg 2: hämta och konvertera

`python -m kommunhandlingar.hamta kommuner/<kommun>.toml <arbetskatalog>`
läser `<arbetskatalog>/<kommun>.kandidater.json` och skriver i `data/` i
samma repo som kommunfilen. Kandidaterna tas i listans ordning, utom de
som bara ska konverteras om, som tas sist (K13), och för var och en avgör
K8 och K9 vad som händer. Sammanfattningen räknar
utfallen och nämner varje dokument som inte gick att hämta, med orsak.

- **Platsen** för en ny källnyckel är organ, datum och typ. En bilaga får
  alltid ett namn, ur filnamnet utan `.pdf`. Är platsen upptagen av ett
  dokument vars källnyckel inte längre finns bland kandidaterna blir den
  nya filen en ny version av det, och den gamla källnyckeln flyttas till
  `tidigare_kallnycklar`. Finns den kvar får det nya dokumentet ett namn
  ur filnamnet, eller ett löpnummer om namnet är upptaget eller tomt.
- **PDF:en** strömmas till en temporär katalog utanför repot, och
  katalogen tas bort när dokumentet är klart, också om något gick fel.
- **Tiderna** `hamtad` och `konverterad` skrivs i UTC, på sekunden.
- **En fil som pdfplumber eller pdfminer inte kan läsa**, hur felet än
  ser ut, blir `ej-konverterad` med `trasig-pdf`, och felet skrivs ut, så
  att en enda fil inte stoppar körningen.
- **Ett dokument med samma källnyckel och sha256** under en ny adress får
  bara ny `kalla_url`; texten och tabellerna rörs inte. Har det en äldre
  version av poolen konverteras det om i stället.

## Tabeller

Hur och varför står i
[ADR-0009](decisions/0009-tabellernas-harkomst-och-csv-format.md). Varje
säker tabell blir en CSV i dokumentets tabellkatalog, som heter som
`.md` men med `.tabeller` i stället för `.md`. Ett dokument utan säkra
tabeller har ingen tabellkatalog.

- **Filnamnet** är `<sida>-<nr>.csv`, utan inledande nollor: sidnumret
  från 1, och tabellens nummer på sidan från 1, uppifrån och ned och vid
  samma höjd från vänster till höger. `3-2.csv` är den andra tabellen på
  sidan 3. En tabell som tolkats ur ett diagram heter
  `<sida>-<nr>.tolkad.csv` och numreras för sig
  ([Tolkade figurer](#tolkade-figurer)).
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
  eller `tabell-osaker`. För en tolkad CSV prövar den i stället att
  sidan står i `tolkade` och att talen står i sidans text
  ([Tolkade figurer](#tolkade-figurer)).

## Tolkade figurer

Hur och varför står i
[ADR-0017](decisions/0017-figurer-marks-och-tolkas-i-efterhand.md). En
figur tolkas i efterhand, för hand, av en Claude-session, enligt
`.claude/skills/tolka-figurer/SKILL.md`. Konverteringen tolkar ingenting.

- **Arbetslistan** är varje dokument med sidor i `figurer` som inte står
  i `tolkade`:
  `python -m kommunhandlingar.tolkning lista data`.
- **Sidorna** renderas med
  `python -m kommunhandlingar.tolkning rendera <md> <katalog>`, som hämtar
  originalet från `kalla_url` med samma artighet som steg 2, prövar att
  sha256 stämmer med front matter och sparar varje otolkad sida i
  `figurer` som `<sida>.png` i 144 dpi. PDF:en raderas. Har originalet
  ändrats renderas ingenting, och dokumentet står kvar i arbetslistan
  tills det konverteras om.
- **Tolkningen** står sist på sidan i `.md`, efter sidans text och
  tabeller, och börjar med kommentaren
  `<!-- tolkning: <modell>, <ÅÅÅÅ-MM-DD> -->`. Därefter, för varje figur
  på sidan, i sidans ordning:
  - **ett diagram med utskrivna tal** blir en tolkad CSV,
    `<sida>-<nr>.tolkad.csv` i tabellkatalogen, och en länk till den
    (`[Tolkad tabell 5-1](<namn>.tabeller/5-1.tolkad.csv)`) följd av en
    mening om vad diagrammet visar. Bara tal som står utskrivna i
    diagrammet tas med, aldrig en stapels höjd avläst mot axeln;
  - **ett schema eller ett flöde** blir ett kodblock märkt `mermaid`;
  - **en karta, ett foto eller ett diagram utan utskrivna tal** blir en
    kort beskrivning.

  En sida som inte hade någon figur får bara kommentaren och meningen
  `Ingen figur.`
- **`tolkade`** får sidans nummer när tolkningen är skriven, så att
  `tolkade` alltid är sidor ur `figurer`, i samma ordning.
- **Datakontrollen** prövar att `figurer` och `tolkade` är `null`
  samtidigt, att `figurer` bara har sidor som finns i dokumentet, att
  `tolkade` är sidor ur `figurer` i ordning, och att varje sida i
  `tolkade`, och ingen annan, har precis en tolkning, med modell och
  datum. Har dokumentet en tolkning ska sidkommentarerna stå en gång
  var, från 1 till sista sidan. I en tolkad CSV ska varje tal i varje
  cell stå i sidans text före tolkningen, och en cell med siffror som
  inte är ett helt tal, som `65–79 år` eller `2022-23`, ska stå
  ordagrant där. Sidans text är då utan länkarna till tabellerna, och
  ett tal är ett helt tal med tusentalsmellanrum: `120` står inte i
  `1 120` eller `1 250–1 120`, och inget tal står i `13.30`,
  `2025-10-08`, `2022/23`, `K15` eller `3a`. En cell som står ordagrant
  är heller ingen del av ett tal: `5–3` står inte i `2,5–3,5`, och
  `250–300` inte i `1 250–300`. Eftersom tusentalen skiljs med
  mellanslag läses tal med ett enda mellanslag emellan ihop, som axeln
  `0 100 200` eller värdena `90 130`, och ett sådant tal går inte att
  ta med för sig. Två siffergrupper som kan vara ett tal delat över en
  radbrytning eller ett smalt mellanslag, en till tre siffror följda av
  exakt tre, räknas inte som tal, så att `5⏎053 kronor` inte ger talen
  `5` och `053`. Står båda delarna ensamma på var sin rad, eller med
  minst två mellanslag till resten av raden, som talen i ett diagram,
  räknas de. På en sida som lästs med OCR stäms talen
  av mot OCR-texten och är lika obekräftade som den. Att texten före
  tolkningen är orörd prövas inte mekaniskt; det syns i PR:ens diff.
- **En ny konvertering** av dokumentet skriver om `.md` och
  tabellkatalogen som vanligt, också när bara källnyckeln har bytts
  (K9); tolkningarna försvinner då, och sidorna hamnar i arbetslistan
  igen.

## Webbplatsen

Hur och varför står i
[ADR-0012](decisions/0012-webbplatsen-byggs-i-actions-och-publiceras-pa-pages.md).
Webbplatsen är statisk HTML som byggs av
`python -m kommunhandlingar.webbplats <utkatalog> <repoadress>` och
publiceras på GitHub Pages av `.github/workflows/webbplats.yml` vid varje
push till `main` och för hand. Inget av det som byggs checkas in.

- **Sidorna:** en startsida och en statussida per kommunfil i `kommuner/`,
  `<kommun>.html`. Varje sida har samma meny – startsidan och kommunerna
  i bokstavsordning efter id – och en sidfot som länkar till repot och
  säger när sidan byggdes.
- **Statussidan** räknar ur front matter i varje `.md` under
  `data/<kommun>/`, utan något index. Den har en rad per organ i
  kommunfilens ordning: antal sammanträden (olika `datum` och `lopnr`),
  antal dokument per `typ`, antal dokument per `kvalitet` och antal sidor
  i `tal_obekraftade`. Ett organ utan dokument står med som "inget hämtat
  än". Sidan räknar men visar inga andelar, eftersom det ännu inte finns
  något att räkna andelen av.
- **Statisk och utan beroenden:** bara standardbiblioteket, ingen
  JavaScript och inga externa resurser. All text går genom
  `html.escape`. Ingen information bärs av färg.
- **Efter nattkörningen** byggs webbplatsen om när körningens PR mergas
  (se [Körning och incheckning](#körning-och-incheckning)).
- **Dokumenten** måste ha ett `organ` ur kommunfilen, en `typ` och en
  `kvalitet` ur tabellerna ovan. Annars stoppas bygget med filens namn,
  så att inget dokument utelämnas tyst ur tabellerna.
