---
status: accepted
date: 2026-10-22
decision-makers: projektägaren
consulted: AI-agenten
---

# Ett dokument som granskats för hand märks med datumet i `granskad` och konverteras inte om, och två OCR-fel rättas i konverteringen

## Context and Problem Statement

Konverteringen har kvar brister som bara syns när sidan läggs bredvid
originalet: OCR-text med fel tecken, osäkra tabeller som inte blev CSV,
obekräftade tal i de skannade protokollen och figurer som inte är
tolkade. Projektägaren vill att dokumenten granskas för hand, med
Gymnasium & Arbetsmarknad först
([#193](https://github.com/moggleif/kommunhandlingar/issues/193)).

En ny konvertering skriver om `.md` och tabellkatalogen helt. Med
`omkonvertera = true` händer det vid varje versionshöjning (ADR-0019),
och figurtolkningarna försvinner redan i dag på det sättet (ADR-0017).
En rättning för hand skulle gå samma väg. Hur står en granskning kvar,
och vad gör den med märkningen av talen?

## Decision Drivers

* **Data ska vara rätt eller märkt.** En granskning som jämfört talen
  med originalet ska kunna säga att de stämmer.
* **Det som rättats för hand ska inte försvinna** med nästa version av
  konverteringen.
* **Ingen kod för säkerhets skull.** Mekanismen ska vara liten.
* **Fel som går igen rättas en gång.** Att rätta samma OCR-fel för hand
  i hundratals dokument är dyrt och fryser bort förbättringen för resten
  av poolen.

## Considered Options

* Ett fält `granskad` i front matter; omkonverteringen hoppar över ett
  granskat dokument så länge originalet är detsamma
* Rättelser i egna filer bredvid poolen, som läggs på efter varje
  konvertering
* Rätta bara i konverteringen, aldrig för hand

## Decision Outcome

Valt alternativ: "ett fält `granskad`", eftersom det är det minsta som
håller rättningen kvar. Rättningen görs där den syns, i dokumentet, och
PR:ens diff visar vad som ändrats. Rättelsefiler kräver ett format och
kod som lägger på dem, och en rättelse som inte längre passar efter en
ny konvertering måste ändå göras om för hand. Att bara rätta i
konverteringen räcker inte: en skannad sidas tal blir aldrig bekräftade
av OCR, och en tabell som läses fel på ett sätt som bara går igen en gång
är inte värd en regel.

* `granskad` är dagen för granskningen, annars `null`.
* Ett granskat dokument räknas som aktuellt oavsett vilken version av
  poolen som konverterade det, också under en ny adress eller en ny
  källnyckel med samma sha256. Ett nytt original (en annan sha256) blir
  en ny version (K9) utan granskning.
* En sida i `tal_obekraftade` vars tal jämförts med originalet får
  lämna listan; en `tabell-osaker`-sida där varje tabell
  skrivits som CSV blir `ok`. Det som fortfarande är osäkert skrivs ut
  på sidan, och dokumentet märks ändå granskat (projektägaren
  2026-10-22).
* De två OCR-fel som går igen i protokollen, `$` för `§` och
  innehållsförteckningens punktutfyllnad, rättas i konverteringen
  (version 0.9.0) innan granskningen börjar.
* En PR som bara har granskade dokument under `data/` mergas av den som
  granskat, när "Ren kod och tester" gått igenom, utan kontrollpunkten i
  fas 7 (projektägaren 2026-10-22). Den liknar nattkörningens PR
  (ADR-0052): den ändrar bara data, och diffen är granskningen.

### Consequences

* Bra, eftersom en granskning står kvar genom versionshöjningar, också
  figurtolkningarna i ett granskat dokument.
* Bra, eftersom de skannade protokollens tal kan bli bekräftade.
* Dåligt, eftersom ett granskat dokument inte får senare förbättringar
  av konverteringen. Projektägaren räknar med att granskade dokument kan
  konverteras om och granskas igen längre fram, när konverteringen är
  bättre; då tas `granskad` bort först.
* Dåligt, eftersom att talen stämmer bygger på den som granskat, inte på
  en mekanisk kontroll. Det syns i PR:ens diff och i `granskad`.
* Dåligt, eftersom version 0.9.0 gör att hela poolen konverteras om när
  `omkonvertera = true`, några nätter till.

### Confirmation

`tests/test_granskning.py` prövar omkonverteringen, datakontrollen och
OCR-rättningarna. Datakontrollen prövar `granskad` i CI.

## More Information

Arbetssättet står i `.claude/skills/granska-dokument/SKILL.md` och
reglerna i
[Granskade dokument](../03-ARKITEKTUR.md#granskade-dokument). Dokumenten
ur Internet Archive granskas senare; arkivet nås inte från den miljö där
granskningen görs.
