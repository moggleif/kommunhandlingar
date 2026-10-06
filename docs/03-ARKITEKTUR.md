# Arkitektur

Det här beskriver hur poolen är tänkt att byggas. Inget av det är kod än;
när koden kommer är det koden som gäller och dokumentet rättas efter den.
*Varför* står i [docs/decisions/](decisions/).

## Flödet

```
kommuner/<kommun>.yaml
        │
        ▼
1. upptäck   adaptrar per plattform  →  kandidater: organ, datum, typ, URL, källa
        │
        ▼
2. hämta     artig HTTP-klient        →  PDF i en temporär katalog
        │
        ▼
3. konvertera                          →  .md + tabeller som .csv, PDF:en raderas
        │
        ▼
4. indexera                            →  index över alla dokument, luckor och versioner
```

Varje steg är ett eget kommando, läser bara föregående stegs utdata och gör
bara det som är nytt eller ändrat.

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
- Ärendet är ett attribut: diarienummer listas i front matter när de är
  kända. Diariet är en källa till mötesdokument, inte till egna dokument.

## Katalogstruktur

```
src/kommunhandlingar/
  adaptrar/        en modul per plattform (sitevision, wayback, ciceron, …)
  hamtning/        artig HTTP-klient
  konvertering/    pdf → md, tabeller, OCR-reserv, kvalitetsmått
  index/
kommuner/<kommun>.yaml
data/<kommun>/<organ>/<år>/<datum>[-<n>]/<typ>[-<namn>].md
data/<kommun>/<organ>/<år>/<datum>[-<n>]/<typ>[-<namn>].tabeller/<n>.csv
scripts/          verktyg för utvecklingen, t.ex. storlekskontrollen
tests/fixtures/
```

## Front matter

```yaml
---
kommun: kungsbacka
organ: ga
datum: 2025-10-16
typ: protokoll
kallnyckel: sitevision:18.4ac81f8819a0f459fef1dd70
arenden: [GA-2024-00194]
kalla_url: https://…/Protokoll….pdf
sha256: 3f9a…
bytes: 812345
sidor: 14
hamtad: 2026-10-06T15:40:12+02:00
konverterad: 2026-10-06T15:40:31+02:00
pipeline: kommunhandlingar 0.1 / <verktyg> <version>
kvalitet: full        # full | text-utan-tabeller | ocr | delvis | ej-konverterad
kvalitet_per_sida: [ok, ok, ocr, tabell-osaker, …]
---
```
