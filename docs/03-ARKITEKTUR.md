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
            └── Sammanträde (datum)
                  └── Dokument (kallelse | handlingar | protokoll | bilaga)
                        └── Version (sha256, hämtad, källa)
```

- Organ är data, inte kod: de byter namn och slås ihop.
- **Öppen fråga – identitet.** Vad som identifierar ett dokument och en
  version är inte bestämt. Organ, datum och typ räcker inte: ett möte kan ha
  flera bilagor, äldre handlingar och diariet är ordnade per ärende
  (diarienummer), och Sitevision ger en ny adress när en fil byts ut under
  samma nod-id. Det avgörs i en ADR innan den första koden skrivs, och
  sökvägarna nedan följer det beslutet.

## Katalogstruktur

```
src/kommunhandlingar/
  adaptrar/        en modul per plattform (sitevision, wayback, ciceron, …)
  hamtning/        artig HTTP-klient
  konvertering/    pdf → md, tabeller, OCR-reserv, kvalitetsmått
  index/
kommuner/<kommun>.yaml
data/<kommun>/<organ>/<år>/<datum>/<typ>.md
data/<kommun>/<organ>/<år>/<datum>/<typ>.tabeller/<n>.csv
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
