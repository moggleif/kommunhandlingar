# Arkitektur

Det här beskriver hur poolen är tänkt att byggas. Inget av det är kod än;
när koden kommer är det koden som gäller och dokumentet rättas efter den.
*Varför* står i [docs/decisions/](decisions/).

## Flödet

```
kommuner/<kommun>.yaml
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
  turas om att hämta varandras adresser.
- **PDF:en finns bara medan dokumentet behandlas.** Den hämtas till en
  temporär fil utanför repot och raderas när dokumentet är konverterat,
  även om konverteringen misslyckas.
- **Tabellerna först, `.md` sist.** Tabellkatalogen ersätts som helhet, så
  att inga tabeller från en äldre version blir kvar. Sedan skrivs `.md`
  till en temporär fil som byter namn till den rätta. Avbryts körningen
  emellan står nya tabeller bredvid den gamla `.md`; dess `kalla_url` är
  då fortfarande den gamla, så nästa körning gör om dokumentet. Att bara
  checka in färdiga körningar hör till issue #5.
- **Ett misslyckat hämtningsförsök** skriver aldrig över en befintlig
  `.md`. Har dokumentet ingen ger försöket en `.md` med kvalitet
  `ej-hamtad`, försökets tid i `hamtad` och orsaken i `fel` (K6); den bär
  också dokumentets plats. Misslyckas nästa försök av samma orsak skrivs
  ingenting, så att en körning utan ändringar inte ger några diffar.

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
- Ärendet är ett attribut: `arenden` listar diarienummer, är tom när
  dokumentet inte rör något ärende och `null` när det inte är känt.
  Diariet är en källa till mötesdokument, inte till egna dokument.

## Katalogstruktur

```
src/kommunhandlingar/
  adaptrar/        en modul per plattform (sitevision, wayback, ciceron, …)
  hamtning/        artig HTTP-klient
  konvertering/    pdf → md, tabeller, OCR-reserv, kvalitetsmått
  index/
kommuner/<kommun>.yaml
data/<kommun>/<organ>/<år>/<datum>[-<lopnr>]/<typ>[-<namn>].md
data/<kommun>/<organ>/<år>/<datum>[-<lopnr>]/<typ>[-<namn>].tabeller/<nr>.csv
scripts/          verktyg för utvecklingen, t.ex. storlekskontrollen
tests/fixtures/
```

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
pipeline: kommunhandlingar 0.1 / <verktyg> <version>
kvalitet: full        # full | text-utan-tabeller | ocr | delvis | ej-konverterad | ej-hamtad
fel: null             # orsaken när något inte gick: ej-hamtad, ej-konverterad, delvis
kvalitet_per_sida: [ok, ok, ocr, tabell-osaker, …]
---
```

`kvalitet` och `fel` är tillsammans dokumentets status (K6). När kvalitet
är `ej-hamtad` finns inget original: `sha256`, `bytes`, `sidor`,
`konverterad` och `kvalitet_per_sida` är `null`, och `hamtad` är tiden för
det första försöket som misslyckades av orsaken i `fel`. Härkomsten är då
källänken, källnyckeln och försöket
([ADR-0004](decisions/0004-inkrementell-korning-poolen-ar-tillstandet.md)).
