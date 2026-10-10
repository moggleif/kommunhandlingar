---
status: proposed
date: 2026-10-10
decision-makers: projektägaren
consulted: AI-agenten
---

# Webbplatsen renderar poolens dokument med markdown-it-py, en sida per dokument och en per organ

## Context and Problem Statement

Webbplatsen visar en statussida per kommun som räknar dokumenten
([ADR-0012](0012-webbplatsen-byggs-i-actions-och-publiceras-pa-pages.md)),
men inget dokument går att läsa där
([#55](https://github.com/moggleif/kommunhandlingar/issues/55)). Poolens
text är riktig Markdown sedan
[ADR-0021](0021-texten-ar-riktig-markdown.md). Hur blir omkring 1 600
dokument och 17 000 tabeller läsbara på webbplatsen, och vad renderar
Markdown-texten till HTML? ADR-0012 sa att webbplatsen byggs med bara
standardbiblioteket.

## Decision Drivers

* **Texten visas som den stod**, med uppställningen kvar och utan att
  något ur poolen blir markup.
* **Härkomsten och osäkerheten syns** vid texten: källa, kvalitet per
  sida och obekräftade tal (K6).
* **Minst egen kod.** Formatet ägs av konverteringen (ADR-0021), inte av
  webbplatsen.
* **Statisk webbplats** utan JavaScript och utan externa resurser
  (ADR-0012).

## Considered Options

* A – markdown-it-py renderar texten i bygget
* B – Python-Markdown renderar texten i bygget
* C – En egen rendering med bara standardbiblioteket
* D – Webbplatsen länkar till filerna på GitHub

## Decision Outcome

Valt: A, eftersom poolen redan prövas mot markdown-it-py i testerna
(ADR-0021): webbplatsen visar texten med samma läsare som garanterar att
den är riktig.

* **Läsaren** är markdown-it-py med CommonMark, GFM:s tabeller och
  genomstrykning, och HTML i källan avslaget, så att `<…>` ur poolen
  alltid blir text. markdown-it-py flyttas från testberoende till
  projektets beroenden.
* **Sidorna** delas vid `<!-- sida N -->` och renderas var för sig, under
  en egen rubrik med ankare och sidans kvalitet ur front matter.
  Styckena visas med `white-space: pre-wrap`, som ADR-0021 förutsåg.
* **Strukturen:** en sida per organ med sammanträdena per år, nyast
  först, och en sida per dokument på samma sökväg som i `data/`, med
  `.html` i stället för `.md`. Tabellkatalogerna kopieras som de är, så
  att länkarna i texten till CSV:erna fungerar.
* **Resten av webbplatsen** är som förut: standardbiblioteket, `html.escape`
  på all text som inte går genom läsaren, ingen JavaScript.

### Consequences

* Bra, eftersom webbplatsen inte har någon egen tolkning av Markdown att
  hålla i takt med konverteringen.
* Bra, eftersom varje dokument har en egen adress att länka till.
* Dåligt, eftersom webbplatsen får ett beroende, och bygget installerar
  det. Det är litet, rent Python och MIT-licensierat.
* Dåligt, eftersom bygget renderar omkring 160 MB text, ett par minuter
  i Actions, och webbplatsen blir omkring 250 MB. Gränsen på GitHub
  Pages är 1 GB.
* Neutralt, eftersom sök inte ingår
  ([#67](https://github.com/moggleif/kommunhandlingar/issues/67)).

### Confirmation

`tests/test_webbplats_dokument.py` bygger organsidor och dokumentsidor ur
påhittade dokument och kontrollerar ordningen, märkningarna, tabellerna,
kopieringen av CSV:erna och att HTML i texten blir text.

## Pros and Cons of the Options

### A – markdown-it-py

* Bra, eftersom det är samma läsare som testerna prövar poolen med.
* Bra, eftersom CommonMark och GFM-tabeller är det format ADR-0021 lovar.
* Dåligt, eftersom det är ett beroende.

### B – Python-Markdown

* Bra, eftersom det är vanligt och moget.
* Dåligt, eftersom det inte följer CommonMark, så texten kan visas
  annorlunda än testerna och GitHub visar den.
* Dåligt, eftersom tabeller kräver ett tillägg.

### C – Egen rendering

* Bra, eftersom inget beroende tillkommer.
* Dåligt, eftersom webbplatsen då äger en tolkning av formatet som måste
  hållas i takt med konverteringen och med CommonMark.

### D – Länkar till GitHub

* Bra, eftersom ingen rendering behövs och GitHub visar filerna rätt.
* Dåligt, eftersom radbrytningarna flyter ihop på GitHub, härkomsten
  visas som en tabell utan märkning per sida, och tabellerna inte märks
  som obekräftade.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet (projektägaren).** Det ska gå att läsa varje dokument på
   webbplatsen, i strukturen kommun, organ, år, sammanträde, dokument,
   med härkomsten synlig och det som saknas eller är osäkert inte dolt.
2. **Första förslaget (agenten).** Poolens text var då inte riktig
   Markdown: rader ur PDF:en blev listor, rubriker och HTML. Agenten
   föreslog en egen rendering av poolens format (alternativ C).
3. **Projektägarens invändning.** Filerna borde städas till riktig
   Markdown, så att de också går att läsa på GitHub. Det blev ett eget
   issue, [#65](https://github.com/moggleif/kommunhandlingar/issues/65),
   och ADR-0021, som gjordes först.
4. **Andra förslaget (agenten).** När texten är riktig Markdown behövs
   ingen egen rendering. markdown-it-py renderade 11 MB ur poolen på sju
   sekunder. År och sammanträde blir rubriker på organets sida i stället
   för egna sidor, eftersom ett sammanträde har högst några dokument.
   Sök blir ett eget issue (#67). Projektägaren sa ja.
5. **Omprövas** om webbplatsen behöver sök, eller om storleken närmar sig
   gränsen på GitHub Pages.
