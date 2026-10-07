---
status: proposed
date: 2026-10-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Markdown-texten har en kommentar per sida, uppställningen kvar och de säkra tabellerna efter sidans text

## Context and Problem Statement

Steg 2 hämtar och konverterar
([#35](https://github.com/moggleif/kommunhandlingar/issues/35)). Reglerna
för sidornas kvalitet och tabellerna står i
[ADR-0005](0005-konvertering-verktyg-ocr-och-kvalitet.md) och
[ADR-0009](0009-tabellernas-harkomst-och-csv-format.md), men inte hur
texten under front matter ser ut: hur sidorna skiljs åt, hur raderna
skrivs och var en säker tabell står.

## Decision Drivers

* **Tal får inte flyta ihop.** "4 078  4 054" och "4 078 4 054" är olika
  saker, och texten är det enda som bär talen på en sida utan säker
  tabell.
* **En sida i `kvalitet_per_sida` ska gå att hitta i texten.**
* **Ett tal ska stå en gång.** En säker tabell ska inte stå både som
  löptext och som tabell.
* **Enkelt att läsa för både människor och program.**

## Considered Options

* A – Textlagret med bevarad uppställning, en kommentar per sida, säkra
  tabeller efter sidans text
* B – Textlagret utan uppställning (pdfplumbers vanliga text), rubriker
  per sida, säkra tabeller där de står
* C – En fil per sida

## Decision Outcome

Valt: A. Den exakta formen står i
[ARKITEKTUR](../03-ARKITEKTUR.md#markdown-texten).

* `<!-- sida N -->` först på varje sida. Det syns inte när Markdown
  visas, och det krockar inte med dokumentets egna rubriker.
* Raderna ur `extract_text(layout=True)` skrivs utan indrag, med
  mellanrummen inne i raden kvar.
* En säker tabell tas bort ur sidans text och står efter den, som länk
  till CSV:n och som Markdown-tabell.
* Steg 2 får ett eget kommando, `python -m kommunhandlingar.hamta`.
  Namnet på ett nytt dokument tas ur filnamnet, eftersom Sitevision-
  adaptern inte ger någon rubrik per fil, och tiderna skrivs i UTC.
* pdfplumber och pypdfium2 blir projektets första beroenden, låsta på de
  versioner som ADR-0005 provade (0.11.10 och 5.14.0). pypdfium2 behövs
  redan här, för att avgöra om en sida utan tecken är tom.

### Consequences

* Bra, eftersom tal som står i följd i PDF:en också står isär i texten.
* Bra, eftersom varje tal i en säker tabell står en gång, i CSV:n, och
  tabellen ändå syns i texten.
* Dåligt, eftersom uppställningen ger glesa rader i löptext, till exempel
  "Årets  arbete  med".
* Dåligt, eftersom en säker tabell som stod mitt i sidan hamnar efter
  sidans text. Länken och sidkommentaren visar var den hör hemma.

### Confirmation

`tests/test_konvertering.py` och `tests/test_hamta.py` prövar sidornas
text, den osäkra tabellens kodblock, tabellänken och sidkommentarerna mot
fixturerna i `tests/fixtures/pdf/`, som `skapa.py` där bredvid skapar.

## Pros and Cons of the Options

### A – Uppställningen kvar, kommentar per sida, tabeller efter texten

* Bra, eftersom inga tal flyter ihop och sidorna går att hitta.
* Dåligt, eftersom löptexten blir gles.

### B – Vanlig text, rubrik per sida, tabeller på plats

* Bra, eftersom löptexten blir tät och tabellerna står där de stod.
* Dåligt, eftersom pdfplumbers vanliga text sätter ett mellanslag mellan
  ord oavsett avstånd, så två tal i följd inte går att skilja från ett
  tal med tusentalsavgränsare. Provat på valnämndens årsredovisning 2023:
  "330 585 340 835" är två belopp.
* Dåligt, eftersom rubriker per sida krockar med dokumentets egna.

### C – En fil per sida

* Bra, eftersom sidan och dess kvalitet hör ihop i filsystemet.
* Dåligt, eftersom ett dokument på 228 sidor blir 228 filer, och
  datamodellen säger en `.md` per dokument (ADR-0003).

## More Information

Projektägaren gav klartecken 2026-10-07 att arbetet fram till den första
nattkörningen görs under natten, med agentens rekommendationer. Formen
här valde agenten utan att projektägaren sett den, så ADR:n står som
`proposed` tills projektägaren tagit ställning. Att ändra formen senare
betyder att poolen konverteras om, vilket kräver att PDF:erna hämtas
igen så länge de finns kvar hos kommunen.

Sidor som behöver OCR blir `ej-konverterad` tills OCR finns
([#36](https://github.com/moggleif/kommunhandlingar/issues/36)). Den
schemalagda körningen startar inte före det, så ingen sådan sida når
poolen.
