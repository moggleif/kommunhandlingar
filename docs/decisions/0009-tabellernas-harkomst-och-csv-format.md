---
status: accepted
date: 2026-10-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Tabellernas härkomst är dokumentets, sidnumret står i filnamnet, och CSV skrivs i ett fast format

## Context and Problem Statement

`AGENTS.md` lovar att varje textfil bär sin härkomst, och K5 att varje säker tabell
blir en CSV-fil med sidnummer. Front matter bär härkomsten för
dokumentets `.md`, men inget var bestämt om var en CSV:s härkomst och
sidnummer står, eller hur filen skrivs
([#9](https://github.com/moggleif/kommunhandlingar/issues/9); ADR-0005
lämnade frågan hit).

Var står en CSV-fils härkomst och sidnummer, och i vilket format skrivs
den?

## Decision Drivers

* **Ett faktum på ett ställe** (`AGENTS.md`).
* **Varje textfil bär sin härkomst** (`AGENTS.md`). En CSV ska gå att
  föra tillbaka till sitt original och sin sida.
* **CSV:n ska gå att läsa med vanliga verktyg**, utan förbehandling.
* **Ingen kod för säkerhets skull.**
* Tabellkatalogen skrivs om som helhet tillsammans med sin `.md`
  ([ADR-0004](0004-inkrementell-korning-poolen-ar-tillstandet.md)), och
  en körning som avbrutits mellan dem checkas inte in (K11, ADR-0006).
  Det som checkats in har därför tabeller från samma original som `.md`
  beskriver.

## Considered Options

* A – Sidnumret i filnamnet, härkomsten är dokumentets `.md`
* B – En lista över tabellerna i dokumentets front matter
* C – En sidofil med härkomst för varje CSV
* D – Härkomsten i kommentarsrader överst i CSV:n

## Decision Outcome

Valt alternativ: "A – Sidnumret i filnamnet, härkomsten är dokumentets `.md`", eftersom det är det enda
alternativet där varken härkomsten eller sidnumret står på två ställen,
och tabellkatalogen redan hör till sin `.md`.

* **Filnamnet** är `<sida>-<nr>.csv` i dokumentets `.tabeller/`-katalog:
  sidnumret räknat från 1, och tabellens nummer på sidan, från 1.
  `3-2.csv` är den andra tabellen på sidan 3.
* **Härkomsten** är front matter i katalogens `.md`, som har samma namn
  som katalogen utan `.tabeller`. Där står original, tider, pipeline och
  sidans kvalitet.
* **Formatet** är CSV som i RFC 4180, men med radslut LF, UTF-8 utan
  BOM och komma. Cellerna står som de lästes, och inget tal görs om.

Detaljerna står i [03-ARKITEKTUR.md](../03-ARKITEKTUR.md#tabeller).

### Consequences

* Bra, eftersom inget nytt fält behövs och inget kan glida isär.
* Bra, eftersom sidnumret syns utan att någon fil öppnas.
* Bra, eftersom CSV:n läses som den är av vanliga verktyg.
* Dåligt, eftersom en CSV som lyfts ut ur poolen inte bär sin härkomst
  själv. Sökvägen pekar ut dokumentet.
* Dåligt, eftersom `10-1.csv` sorteras före `2-1.csv` som text.
* Dåligt, eftersom en CSV från en sida i `tal_obekraftade` inte bär den
  märkningen själv; den står bara i `.md`.
* Dåligt, eftersom en tom cell och en cell som täcks av en sammanslagen
  cell ser likadana ut. Att upprepa texten i varje täckt cell vore att
  skriva tal som inte står där.
* Neutralt, eftersom radslutet LF avviker från RFC 4180:s CRLF. Vanliga
  CSV-läsare tar båda, och repots textfiler har LF.

### Confirmation

Datakontrollerna (ADR-0006) kontrollerar att varje CSV heter
`<sida>-<nr>.csv`, att numren på varje sida är 1, 2, … utan lucka, och
att sidan finns i dokumentet och är `ok` eller `tabell-osaker`. När
konverteringen skrivs testas formatet mot ett dokument med tabeller i
`tests/fixtures/`.

## Pros and Cons of the Options

### A – Sidnumret i filnamnet, härkomsten är dokumentets `.md`

* Bra, eftersom härkomsten och sidnumret står på ett ställe vardera.
* Bra, eftersom ingen ny fil och inget nytt fält tillkommer.
* Dåligt, eftersom en ensam CSV saknar sin härkomst utan sökvägen.

### B – En lista i front matter

`tabeller: [{fil: 1.csv, sida: 3}, …]`

* Bra, eftersom allt om dokumentet står i en fil.
* Dåligt, eftersom filnamnen står både i listan och i katalogen, och de
  två kan glida isär.
* Dåligt, eftersom front matter växer med varje tabell.

### C – En sidofil per CSV

* Bra, eftersom varje tabell bär sin härkomst också utanför poolen.
* Dåligt, eftersom samma härkomst upprepas i varje sidofil och i `.md`.
* Dåligt, eftersom antalet filer fördubblas.

### D – Kommentarsrader i CSV:n

* Bra, eftersom härkomsten följer med filen.
* Dåligt, eftersom RFC 4180 inte har kommentarer, och vanliga CSV-läsare
  läser raderna som data.
* Dåligt, eftersom samma härkomst upprepas i varje tabell.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet** pekade på att härkomstfälten räknades upp på flera ställen
   och frågade om CSV:ns härkomst ska stå i en sidofil eller i
   dokumentets front matter.
2. **Agentens rekommendation** i fas 0 var A: det som checkas in har tabeller
   från samma original som `.md`, eftersom tabellkatalogen ersätts som
   helhet med sin `.md` (ADR-0004), så en egen härkomst för varje CSV
   vore samma värden en gång till. Agenten rekommenderade också att
   formatet bestäms här, eftersom ADR-0005 lämnade det hit.
3. **Agentens invändning mot sig själv:** den som hämtar en enda CSV
   förlorar härkomsten. Svaret är att sökvägen pekar ut dokumentet, och
   att C, som löser det, upprepar samma fakta i varje fil. Regeln i
   `AGENTS.md` säger därför att tabellerna bär sin härkomst genom sitt
   dokument.
4. **Cellerna står som de lästes**, eftersom tal som tolkas kan tolkas
   fel, och ADR-0005 säger att talen i ett läst textlager är de tal
   PDF:en innehåller. Att göra om dem är analysens sak.
5. **Ägarens beslut** 2026-10-07: A, formatet här och en fälttabell för
   front matter i arkitekturen.
6. **Granskningen** (fas 6) fann att en sammanslagen cell inte var
   bestämd, att ordningen mellan två tabeller på samma höjd saknades, och
   att den som läser en CSV inte ser att sidans tal kan vara
   obekräftade. Den sammanslagna cellens text står därför i dess första
   cell, tabeller på samma höjd numreras från vänster, och
   konsekvensen om obekräftade tal står ovan. Rättelserna efter
   granskningen bekräftas av ägaren i pull requesten.

### När beslutet bör omprövas

Om tabeller som fortsätter över en sidbrytning slås ihop (ADR-0005 lämnar
det öppet). Då har en tabell mer än en sida, och filnamnet räcker inte.
