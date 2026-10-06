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

Varje steg är ett eget kommando och läser bara föregående stegs utdata.
Kandidatlistan är en arbetsfil som inte checkas in; den går att ta fram
igen genom att köra upptäckten.

### Inkrementell körning

Hur och varför står i
[ADR-0004](decisions/0004-inkrementell-korning-poolen-ar-tillstandet.md).

- **Poolen är tillståndet.** Det finns ingen separat tillståndsfil. Steg 2
  läser front matter i `data/<kommun>/` och slår upp varje kandidat på
  `kallnyckel`.
- **Adressen är signalen.** Samma källnyckel med samma `kalla_url` hämtas
  inte. En ny källnyckel, en ny adress eller kvalitet `ej-hamtad` hämtas,
  och sha256 avgör sedan enligt ADR-0003 om det är en ny version eller bara
  en ny adress.
- **Upptäckten ger högst en kandidat per källnyckel.** Finns filen på flera
  adresser väljer adaptern den som gäller, annars skulle körningarna
  turas om att hämta varandras adresser.
- **PDF:en finns bara under ett dokument.** Den hämtas till en temporär fil
  utanför repot och raderas när dokumentet är konverterat, även om
  konverteringen misslyckas.
- **`.md` skrivs sist,** till en temporär fil som sedan byter namn till den
  rätta, så att en avbruten körning aldrig lämnar en halvskriven `.md`.
  Tabellerna skrivs före. Den som avbryts kör om; det som redan är skrivet
  hoppas över.
- **Ett misslyckat hämtningsförsök** för ett dokument som inte finns i
  poolen ger en `.md` med kvalitet `ej-hamtad`, försökets tid i `hamtad`
  och orsaken i `fel` (K6); den bär också dokumentets plats. Gäller
  försöket en ny adress för ett dokument som redan finns, lämnas dess `.md`
  orörd. I båda fallen försöker nästa körning igen.

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
fel: null             # orsaken när kvalitet är ej-hamtad eller ej-konverterad
kvalitet_per_sida: [ok, ok, ocr, tabell-osaker, …]
---
```

När kvalitet är `ej-hamtad` finns inget original: `sha256`, `bytes`,
`sidor`, `konverterad` och `kvalitet_per_sida` är `null`, och `hamtad` är
tiden för försöket.
