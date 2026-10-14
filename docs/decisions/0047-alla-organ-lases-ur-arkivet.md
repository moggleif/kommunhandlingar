---
status: accepted
date: 2026-10-13
decision-makers: projektägaren
consulted: AI-agenten
---

# Alla organ läses ur arkivets Sitevision-kopior, utan att vänta på att konverteringen blir färdig

## Context and Problem Statement

[ADR-0027](0027-arkivet-slas-pa-per-organ.md) slog på arkivet bara för
Gymnasium & Arbetsmarknad (`ga`), med drivkraften att resten av arkivet
inte skulle hämtas förrän konverteringen var färdig. `ga` är nu hämtat ur
alla arkiv. För de andra 16 organen saknar poolen allt före 2024, ungefär
1 300 filer i arkivets Sitevision-kopior 2021–2023
([täckningen](../kallor/kungsbacka.md#täckning)). Ägaren vill att
nattkörningen hämtar resten av dokumenten.

Ska resten av arkivet hämtas nu, eller vänta på att konverteringen blir
färdig?

## Decision Drivers

* **Poolen ska bli hel.** Ägaren vill ha resten av dokumenten.
* **Omkonverteringen finns.** Det som hämtas nu görs om när
  konverteringen ändras ([ADR-0019](0019-omkonvertering-efter-poolens-version.md)),
  så att vänta sparar inget arbete i längden.
* **Enkelt först.** Fältet från ADR-0027 räcker.

## Considered Options

* A – Alla organ i `wayback` nu
* B – Vänta tills konverteringen är färdig, som ADR-0027 sa
* C – Ett organ i taget

## Decision Outcome

Valt: A, eftersom det ger ägaren det den ber om med en ändring i
kommunfilen och ingen kod.

* **Kungsbacka** får alla organ i `wayback`.
* **Allt annat är som i ADR-0018 och ADR-0027:** arkivet körs sist, nyast
  först, och fyller bara luckor. Omkonverteringen
  ([#84](https://github.com/moggleif/kommunhandlingar/issues/84)) går före
  arkivet.

Det ersätter drivkraften "konverteringen först" i ADR-0027.

### Consequences

* Bra, eftersom nattkörningen hämtar resten av 2021–2023 utan ny kod.
* Dåligt, eftersom arkivet får det som blir över av tidsbudgeten. Så länge
  omkonverteringen pågår hämtas inget ur arkivet, och sedan tar de 1 300
  filerna flera nätter.
* Dåligt, eftersom en fil vars datum i filnamnet och på mötessidan inte
  stämmer blir utan kandidat (K2) tills en rättelse läggs i kommunfilen
  för hand. Sammanfattningen listar dem.
* Dåligt, eftersom de år då både Sitevision och Episerver fanns,
  2021–2022, får Sitevisions dokument först. Episervers dokument av samma
  typ för samma möte hämtas inte
  ([ADR-0039](0039-episerver-ur-arkivet-med-mappar-och-monster.md)). Det
  prövas i ett eget beslut innan fler organ får Episerver-mappar.

### Confirmation

`tests/test_konfiguration.py` prövar att Kungsbackas `wayback` har alla
organ.

## Pros and Cons of the Options

### A – Alla organ nu

* Bra, eftersom det är en ändring i kommunfilen.
* Dåligt, eftersom det som hämtas före en ny version av konverteringen
  måste göras om.

### B – Vänta

* Bra, eftersom inget görs två gånger.
* Dåligt, eftersom ingen vet när konverteringen är färdig, och poolen
  saknar tre år under tiden.

### C – Ett organ i taget

* Bra, eftersom varje natt rör ett organ.
* Dåligt, eftersom någon måste ändra kommunfilen för varje organ, och
  ADR-0018 valde nyast först för alla organ.

## More Information

Ägaren bad 2026-10-13 att nattkörningen ska hämta resten av dokumenten.
Agenten föreslog att dela upp arbetet: först det här, sedan regeln för
samma möte från två plattformar, sist Episerver-mapparna för alla organ.
Ägaren valde det.
