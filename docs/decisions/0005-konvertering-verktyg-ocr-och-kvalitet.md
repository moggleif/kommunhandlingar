---
status: proposed
date: 2026-10-06
decision-makers: Morgan
consulted: Claude
---

# Konvertering: verktyg, OCR och kvalitet som den sämsta sidan avgör

## Context and Problem Statement

Varje hämtad PDF blir en `.md` med tabeller som CSV, och PDF:en raderas
(ADR-0001). Konverteringen kan inte göras om utan att filen letas upp igen,
så den måste vara så bra som möjligt första gången – och säga ärligt hur bra
den blev ([#4](https://github.com/moggleif/kommunhandlingar/issues/4)).

Handlingarna är blandat material: protokoll och tjänsteskrivelser i löptext,
budget- och uppföljningstabeller, inskannade yttranden och underskrivna
sidor, och sammanslagna handlingar-PDF:er på 3–33 MB per möte
([källor](../kallor/kungsbacka.md)).

Vilket verktyg läser text och tabeller, vad läser sidor utan textlager, vad
betyder kvalitetsnivåerna och hur avgörs de, och vad står i `pipeline`?

## Decision Drivers

* **Licensen.** Repot är MIT. Ett beroende med AGPL drar in villkor som
  inte passar en publik datapool som andra ska kunna bygga vidare på.
* **Tabellerna.** Siffrorna i budgetar och uppföljningar är det analyserna
  behöver mest. Ett fel tal som ser riktigt ut är värre än ett som saknas.
* **Hellre märka än gissa.** Kvaliteten ska gå att avgöra mekaniskt och
  stämma med hur användbar texten faktiskt är (K5, K6).
* **Svenska.** Å, ä och ö i textlager och OCR.
* **Enkelhet och drift.** Få och små beroenden; körningen ska fungera i
  CI eller en molnmiljö utan GPU (#5).

## Considered Options

* A – pdfplumber för text och tabeller, Tesseract för OCR
* B – Docling för text, tabeller och OCR
* C – PyMuPDF (pymupdf4llm) med Tesseract
* D – Poppler (`pdftotext -layout`) med OCRmyPDF

## Decision Outcome

*Väntar på jämförelsen på riktiga handlingar (se More Information).*
Claude rekommenderar preliminärt A.

Det som redan är avgjort, oberoende av verktyget (Morgan 2026-10-06):

* **AGPL utesluts.** C faller på licensen, och OCRmyPDF i D kräver
  Ghostscript, som också är AGPL. De är med i jämförelsen bara som mått på
  vad som går förlorat.
* **Kvalitet per sida, och den sämsta sidan avgör dokumentet.** Nivåerna
  och hur de avgörs står i
  [ARKITEKTUR](../03-ARKITEKTUR.md#konvertering-och-kvalitet). Sidans nivå
  följer av vad konverteringen själv mäter – textlagrets längd och andel
  oläsliga tecken, OCR:ns säkerhet och om tabellen är avgränsad av linjer –
  inte av någon bedömning i efterhand.
* **Text från OCR under säkerhetströskeln skrivs inte.** Sidan blir
  `ej-konverterad`, så att ingen bygger analyser på gissad text.
* **En fil som inte går att öppna** ger `ej-konverterad` med orsaken i `fel`
  (`krypterad`, `trasig-pdf`, `inte-pdf`), på samma sätt som ett misslyckat
  hämtningsförsök i ADR-0004.
* **`pipeline`** är `kommunhandlingar <version>` ur `pyproject.toml` följt
  av varje verktyg som användes på dokumentet, med version. Versionen höjs
  när konverteringens utdata ändras. `pyproject.toml` och ARKITEKTUR
  stämdes av till `0.1.0`.

Trösklarna – tecken per sida, andel oläsliga tecken och OCR-säkerhet –
sätts ur jämförelsen.

### Consequences

* Bra, eftersom kvaliteten i varje fil går att lita på: den mäts, den
  gissas inte.
* Bra, eftersom ett dokument med en enda dålig sida syns som `delvis`
  och inte som `full`.
* Dåligt, eftersom en enda inskannad underskriftssida gör ett annars rent
  protokoll till `ocr`. `kvalitet_per_sida` visar då att resten är `ok`.
* Dåligt, eftersom tabeller utan linjer alltid blir osäkra, även när de
  råkar vara rätt lästa.

### Confirmation

* Testfixturer under `tests/fixtures/` med facit som går att kontrollera
  för hand: en sida med textlager, en inskannad sida, en tabell med linjer,
  en tabell utan linjer, en krypterad och en trasig fil. Testerna kontrollerar
  både texten och den kvalitet varje sida får.
* CI kontrollerar att `kvalitet` stämmer med `kvalitet_per_sida` enligt
  tabellen i ARKITEKTUR, i varje `.md` under `data/`.

## Pros and Cons of the Options

### A – pdfplumber för text och tabeller, Tesseract för OCR

pdfplumber (MIT, på pdfminer.six) ger varje ord med koordinater och varje
ritad linje. Tabellerna läses med koordinatmetoden från
`moggleif/politik` (`scripts/pdftabell.py`): linjerna avgränsar cellerna.
Sidor utan textlager renderas med pypdfium2 (Apache-2.0/BSD) och läses av
Tesseract (Apache-2.0) med svensk modell.

* Bra, eftersom alla licenser är tillåtande.
* Bra, eftersom metoden redan läser Kungsbackas och GR:s rapporter rätt i
  politik-repot.
* Bra, eftersom "säker tabell" får en mekanisk definition: avgränsad av
  linjer.
* Neutralt, eftersom Tesseract är ett systempaket, inte ett Python-paket.
* Dåligt, eftersom läsordningen i flerspaltiga sidor måste ordnas själv.

### B – Docling för text, tabeller och OCR

Docling (MIT) analyserar sidans layout med maskininlärda modeller, ger
läsordning och tabellstruktur, och kan köra OCR.

* Bra, eftersom läsordning och tabeller utan linjer hanteras.
* Dåligt, eftersom det kräver PyTorch och modeller på flera GB, hämtade
  från Hugging Face.
* Dåligt, eftersom en modells tabell inte går att kalla säker eller
  osäker mekaniskt: den ser lika säker ut när den har fel.
* Dåligt, eftersom det är långsamt utan GPU.

### C – PyMuPDF (pymupdf4llm) med Tesseract

* Bra, eftersom det är snabbt och ger bra Markdown direkt.
* Dåligt, eftersom licensen är AGPL-3.0 (eller kommersiell).

### D – Poppler (`pdftotext -layout`) med OCRmyPDF

* Bra, eftersom `pdftotext` är snabbt och finns överallt.
* Dåligt, eftersom tabeller bara blir text i spalter, utan celler.
* Dåligt, eftersom OCRmyPDF kräver Ghostscript (AGPL), och Poppler är
  GPL – ett externt program, men ett beroende att hålla reda på.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Fas 0 (Claude).** Fyra saker att bestämma: verktyg, OCR, `pipeline`
   och kvalitetsnivåerna. `status` var redan löst av ADR-0004: `kvalitet`
   och `fel` tillsammans.
2. **Fem frågor till Morgan, med Claudes rekommendation:** utesluta AGPL
   på förhand (ja), låta den sämsta sidan avgöra (ja), `pipeline` med
   versionen ur `pyproject.toml` (ja), hålla jämförelseskriptet utanför
   repot och bara redovisa resultatet här (ja), och var provfilerna skulle
   komma ifrån. **Morgan sa ja** till alla 2026-10-06.
3. **Provfilerna.** Molnmiljön nådde varken kungsbacka.se, Internet Archive
   eller Hugging Face. Morgan öppnade nätet i en ny miljö i stället för att
   ladda upp exempel, så att jämförelsen görs på handlingar hämtade direkt
   från källan.
4. **Under skrivandet (Claude)** lades till att text från OCR under
   tröskeln inte skrivs alls, att tabeller på en OCR-sida alltid är osäkra,
   och att en fil som inte går att öppna får en orsak i `fel`.

### Jämförelsen

*Görs i en session med öppet nät, på ett protokoll, en tjänsteskrivelse,
en budgettabell, ett inskannat yttrande och en sammanslagen
handlingar-PDF.* Resultatet redovisas här: tid per sida, läsordning,
tabeller rätt lästa, OCR-fel på å, ä och ö, och vilken kvalitet sidorna
fick.

### Vad som inte avgörs här

* Hur sammanslagna handlingar delas upp per ärende.
* CSV-schemat och härkomsten för tabellfilerna
  ([#9](https://github.com/moggleif/kommunhandlingar/issues/9)).

### När beslutet bör omprövas

Om en stor del av sidorna blir `tabell-osaker` för tabeller som i själva
verket är rätt lästa, eller om OCR-säkerheten ofta hamnar under tröskeln
på sidor som går att läsa för ögat.
