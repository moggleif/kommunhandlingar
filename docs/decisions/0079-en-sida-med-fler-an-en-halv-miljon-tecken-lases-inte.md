---
status: accepted
date: 2026-11-15
decision-makers: projektägaren
consulted: AI-agenten
---

# En sida med fler än 500 000 tecken läses inte, utan blir `ej-konverterad` och märks som figur

## Context and Problem Statement

Geoteknikrapporten som fick nattkörningen att fastna
([#274](https://github.com/moggleif/kommunhandlingar/issues/274)) står i
poolen som `ej-konverterad` med `fel: tidsgrans`
([ADR-0075](0075-ett-dokument-far-en-egen-tidsgrans.md)), fast de flesta
av dess 121 sidor går att läsa. Orsaken är ett fåtal borrdiagram med
miljontals tecken
([#275](https://github.com/moggleif/kommunhandlingar/issues/275)). Hur
ska en sida som är för tung att läsa hindras från att ta resten av
dokumentet med sig, med en gräns som inte beror på hur snabb maskinen är?

Mätt 2026-11-15, tecken per sida enligt pypdfium2 och tid i sidläsningen:

| Sida | Tecken    | Tid                         |
| ---- | --------- | --------------------------- |
| 94   | 6 046 184 | inte klar på 20 minuter     |
| 103  | 1 076 515 | inte mätt                   |
| 100  |   351 634 | 3 min 15 s                  |
| 77   |    94 915 | 17 s                        |
| 96   |    63 427 | 9 s                         |

Tiden växer snabbare än antalet tecken. De tyngsta sidorna i fyra stora
handlingar har 3 000–4 500 tecken. Textens längd per sida i hela poolen
(5 148 dokument), som en övre gräns: 99,99 procent av sidorna har under
42 000 tecken, och den tyngsta omkring 110 000.

## Decision Drivers

* **Tomt är inte noll.** En sida som inte läses registreras som det.
* **Förutsägbart.** Gränsen ska bli densamma på varje maskin.
* **Vanliga sidor ska inte drabbas.**
* **Enkelt först.** pypdfium2 öppnar redan varje sida för renderingen, och
  räknar en sidas tecken snabbt: hela rapporten på 10 sekunder.

## Considered Options

* A – Ett tak för antalet tecken per sida, räknat med pypdfium2 innan
  pdfplumber läser sidan
* B – En tidsgräns per sida
* C – Ett tak för antalet ritade objekt (linjer, rektanglar, kurvor)

## Decision Outcome

Valt: A, eftersom antalet tecken går att räkna innan den dyra läsningen
börjar och blir detsamma på varje maskin.

* **Taket** är 500 000 tecken, fyra gånger poolens tyngsta vanliga sida.
  I geoteknikrapporten faller sida 94 och 103; sida 100 läses.
  Projektägaren valde 500 000 framför 200 000, som också hade fällt sida
  100.
* **En sida över taket** blir `ej-konverterad` utan text och står i
  `tal_obekraftade`, som varje sådan sida. Den står också i `figurer`, så
  att den hamnar i arbetslistan för figurer (K15,
  [ADR-0017](0017-figurer-marks-och-tolkas-i-efterhand.md)); ett
  borrdiagram är en figur. Dokumentet blir `delvis`.
* **Dokumentets tidsgräns** (ADR-0075) står kvar för allt annat som tar
  för lång tid.
* **Ingen versionshöjning.** Versionen jämförs exakt (ADR-0019), och
  omkonverteringen är påslagen, så en höjning skulle köa om varje dokument
  som redan har den nya versionen. Ingen sida i poolen är i närheten av
  taket, så de skulle bli likadana. Geoteknikrapportens tomma dokument
  togs i stället bort för hand, så att nattkörningen hämtar den som ett
  nytt dokument.

### Consequences

* Bra, eftersom rapportens läsbara sidor blir text, och de tunga sidorna
  kan tolkas som figurer.
* Bra, eftersom gränsen är ett antal och inte en tid.
* Dåligt, eftersom en sida strax under taket ändå kan ta flera minuter;
  sida 100 med 350 000 tecken tar drygt tre. Dokumentets tidsgräns fångar
  ett dokument med många sådana.
* Dåligt, eftersom text på en sida över taket inte blir sökbar. Ingen
  sådan sida har hittats i en vanlig handling.
* Neutralt, eftersom tecknen räknas en gång till för varje sida; det
  kostar en bråkdel av sidläsningen.

### Confirmation

Tester i `tests/test_konvertering.py`: taket är 500 000; en sida över
taket blir `ej-konverterad`, står i `figurer` och `tal_obekraftade`; en
sida med exakt så många tecken som taket läses; övriga sidor läses som
vanligt. Geoteknikrapporten konverterad lokalt med taket: se PR:en.

## Pros and Cons of the Options

### A – Tak för antalet tecken

* Bra, eftersom det räknas snabbt och lika överallt.
* Dåligt, eftersom en sida med få tecken men väldigt mycket grafik inte
  fångas.

### B – Tidsgräns per sida

* Bra, eftersom den fångar varje orsak.
* Dåligt, eftersom resultatet beror på maskinens fart, och issuet ber om
  en förutsägbar gräns.

### C – Tak för antalet ritade objekt

* Bra, eftersom linjerna och rektanglarna också kostar i tabellsökningen.
* Dåligt, eftersom vanliga ritningar och kartor har många objekt men går
  fort att läsa, så gränsen blir svår att sätta utan fler mätningar.
