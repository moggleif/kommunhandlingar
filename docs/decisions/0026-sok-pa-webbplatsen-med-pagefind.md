---
status: proposed
date: 2026-10-11
decision-makers: projektägaren
consulted: AI-agenten
---

# Webbplatsen får sök med Pagefind: ett delat index som byggs i Actions och JavaScript bara på söksidan

## Context and Problem Statement

Poolens dokument går att läsa på webbplatsen
([ADR-0023](0023-dokumenten-pa-webbplatsen-med-markdown-it-py.md)), men
inte att söka i
([#67](https://github.com/moggleif/kommunhandlingar/issues/67)).
Webbplatsen är statisk, utan server och utan JavaScript
([ADR-0012](0012-webbplatsen-byggs-i-actions-och-publiceras-pa-pages.md)),
och poolen är omkring 160 MB text i 1 600 dokument. Hur går det att söka
efter ord i dokumenten och komma till träffen, med kvaliteten synlig?

## Decision Drivers

* **Träffen leder till rätt sida** i dokumentet, och märkningen av
  kvalitet och obekräftade tal syns i träfflistan (K6, K18).
* **Ingen server och inga externa resurser.** Webbplatsen ligger kvar på
  GitHub Pages.
* **Litet att hämta per sökning**, också när poolen växer.
* **Minst egen kod**, och bara text i repot (ADR-0001).

## Considered Options

* A – Pagefind bygger ett delat index i Actions, och söksidan söker i
  webbläsaren
* B – Ett eget index i Python och en egen sökning i JavaScript
* C – Söksidan länkar till GitHubs kodsök i repot
* D – Ett färdigt sökbibliotek (som Lunr) med ett index i en fil

## Decision Outcome

Valt: A, eftersom det är det enda alternativet som både når rätt sida i
dokumentet och håller varje sökning liten, utan egen sökkod.

* **Indexet** byggs av Pagefind ur den färdiga webbplatsen, efter
  `python -m kommunhandlingar.webbplats`, och publiceras med den. Det
  checkas inte in. Pagefind delar indexet i bitar, och webbläsaren hämtar
  bara de bitar en sökning behöver.
* **Bara dokumentens text indexeras.** Dokumentsidans text ligger i ett
  element med `data-pagefind-body`; härkomsten, menyn och status- och
  organsidorna ligger utanför och indexeras inte. Webbplatsens egna
  markeringar i texten har `data-pagefind-ignore`. Rubrikerna "Sida N"
  indexeras, eftersom träffen per sida tar sin titel och sitt ankare ur
  dem; ordet "sida" ger därför träff i alla dokument.
* **Märkningen:** träffens titel är dokumentets rubrik och, när
  kvaliteten inte är `full`, kvaliteten. En sida i `tal_obekraftade` har
  "obekräftade tal" i sin rubrik, så att det står vid träffen på den
  sidan. En osäker tabell märks inte per sida i träfflistan: ett dokument
  med en osäker tabell har aldrig kvaliteten `full`, så kvaliteten står i
  titeln, och på sidan står tabellen märkt som förut (K18).
* **Filter** för organ, år, typ och kvalitet sätts i dokumentsidan med
  Pagefinds attribut.
* **JavaScript bara på söksidan** (`sok.html`), med Pagefinds färdiga
  sökruta (Default UI) och filerna från webbplatsen själv. Pagefind
  rekommenderar sedan version 1.5 sina webbkomponenter för nya
  webbplatser, med bättre tillgänglighet; Default UI valdes för att det
  är en rad att sätta upp, och bytet prövas om tillgängligheten brister.
  Alla andra sidor är som förut utan JavaScript, och söksidan säger vad som krävs när JavaScript
  saknas. Det ändrar ADR-0012 på den punkten.
* **Pagefind** (MIT) installeras i bygget som Python-paket med det
  förbyggda programmet, i en egen grupp av beroenden (`webbplats`).

### Consequences

* Bra, eftersom ett prov på hela poolen gav ett index på omkring 100 MB
  som byggdes på en minut, och en sökning hämtade 0,5–0,9 MB.
* Bra, eftersom Pagefind hanterar svenska böjningar och länkar till
  rubrikerna med ankare, `#sida-N`.
* Dåligt, eftersom webbplatsen växer från omkring 235 MB till 330 MB, och
  en kommun till av samma storlek tar den till två tredjedelar av gränsen
  på 1 GB.
* Dåligt, eftersom söket kräver JavaScript, och bygget får ett program till.
* Neutralt, eftersom ordet inte markeras på dokumentets sida efter
  klicket; det skulle kräva JavaScript också där.

### Confirmation

`tests/test_webbplats_sok.py` bygger en liten webbplats ur påhittade
dokument, kör Pagefind på den och läser Pagefinds index: att bara
dokumenten och deras text indexerades, utan webbplatsens egen text, och
att titeln, filtren och sidornas rubriker med ankare är de väntade. Att en
sökning i webbläsaren når rätt sida prövades för hand på hela poolen.

## Pros and Cons of the Options

### A – Pagefind

* Bra, eftersom indexet är delat och varje sökning hämtar lite.
* Bra, eftersom träffarna kan leda till sidans ankare och filtreras.
* Bra, eftersom ingen sökkod behöver skrivas eller underhållas här.
* Dåligt, eftersom det är ett program till i bygget och JavaScript på en
  sida.

### B – Eget index och egen JavaScript

* Bra, eftersom inget nytt beroende tillkommer.
* Dåligt, eftersom ordindelning, böjningar, delning av indexet,
  utdrag och filter blir egen kod att skriva och underhålla.

### C – GitHubs kodsök

* Bra, eftersom inget behöver byggas.
* Dåligt, eftersom kodsöket kräver inloggning, inte söker i stora filer
  och visar `.md`-filerna utan märkning eller länk till sidan.

### D – Ett index i en fil

* Bra, eftersom biblioteken är små och kända.
* Dåligt, eftersom hela indexet, tiotals MB, måste hämtas innan första
  sökningen.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet (projektägaren).** Det ska gå att söka efter ord i poolens
   dokument och komma till träffen, med härkomst och kvalitet synliga.
   Issuet frågade om ett index i webbläsaren eller GitHubs sök, hur stort
   ett index blir och om det kan delas per organ eller år.
2. **Provet (agenten).** Agenten byggde webbplatsen med hela poolen och
   körde Pagefind på den: omkring 100 MB index, 132 kB för att öppna söksidan och
   0,5–0,9 MB per sökning, med träffar som länkar till rätt sida.
   Pagefind delar indexet självt, så det behöver inte delas per organ
   eller år. GitHubs kodsök kräver inloggning och föll därför bort.
3. **Förslaget (agenten).** Pagefind, med JavaScript bara på söksidan,
   filter för organ, år, typ och kvalitet, och "obekräftade tal" i sidans
   rubrik. Projektägaren sa ja till alla fyra.
4. **Omprövas** när en kommun till läggs till, om webbplatsen närmar sig
   gränsen på GitHub Pages (ett index per kommun, eller egen server,
   [#18](https://github.com/moggleif/kommunhandlingar/issues/18)).
