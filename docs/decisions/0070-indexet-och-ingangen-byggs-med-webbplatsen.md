---
status: proposed
date: 2026-11-14
decision-makers: projektägaren
consulted: AI-agenten
---

# Indexet byggs med webbplatsen som JSON Lines per kommun, med en `llms.txt` som ingång, och checkas inte in

## Context and Problem Statement

Poolen har drygt 4 800 dokument och 33 000 tabeller, ett dokument i
taget. För att en AI, eller en människa, ska kunna ställa frågor över
hela historiken behövs en ingång som säger vad som finns och var
([#56](https://github.com/moggleif/kommunhandlingar/issues/56)). Steg 3 i
flödet, indexet, har aldrig blivit kod. Var ska indexet bo, i vilket
format, och hur hittar en AI dit?

Issuet rymmer också protokollen delade per paragraf och tidsserier ur
tabellerna. De delas ut i egna issues och ingår inte här.

## Decision Drivers

* **Poolen är tillståndet** (ADR-0004). Det som går att räkna fram ur
  front matter ska inte lagras en gång till.
* **Inga diffar i onödan.** Nattkörningen ska inte ändra en stor fil varje
  natt.
* **Härkomsten och kvaliteten följer med.** Inget fält ska tappas på vägen,
  och tomt är inte noll.
* **Enkelt först.** Ingen ny tjänst, inget nytt beroende.

## Considered Options

* A – Indexet byggs med webbplatsen, en JSON Lines-fil per kommun, och en
  `llms.txt` i roten
* B – Ett eget kommando i steg 3 skriver indexet till repot, och
  nattkörningen checkar in det
* C – Som A men i CSV, med ett urval av fälten
* D – Inget index, bara en `llms.txt` som beskriver katalogstrukturen

## Decision Outcome

Valt: A, eftersom allt som behövs redan läses när webbplatsen byggs, och
indexet då följer poolen utan att något lagras.

* **Indexet** är `<kommun>/index.jsonl` på webbplatsen, en rad per
  dokument i sökvägarnas ordning. Raden har hela front matter i schemats
  ordning med JSON-typer: `null`, listor, och tal för `lopnr`, `bytes`,
  `sidor` och sidnumren i `tal_obekraftade`, `figurer` och `tolkade`.
  Dessutom `fil` (sökvägen i repot), `sida` (sidan på webbplatsen) och
  `tabeller` (tabellernas filnamn, bredvid sidan i `<sida>.tabeller/`).
* **`llms.txt`** följer förslaget på <https://llmstxt.org/>: en rubrik, en
  sammanfattning, hur kvaliteten och `tal_obekraftade` ska läsas, och per
  kommun länkar till indexet, översikten, organens sidor och kommunens
  filer skrivna för hand. Filerna i repot länkas med `/raw/main/`, så att
  länken ger själva filen.
* **Versionerna** står i git (ADR-0003). Indexet visar poolen som den är
  nu.

### Consequences

* Good, eftersom ingenting nytt lagras och nattkörningen inte ändras.
* Good, eftersom hela front matter följer med, också listorna per sida.
* Good, eftersom en AI hittar allt från en adress.
* Bad, eftersom indexet bara finns där webbplatsen finns. Den som klonar
  repot får bygga webbplatsen, eller läsa front matter själv.
* Bad, eftersom JSON Lines är sämre att öppna i ett kalkylark än CSV.
* Bad, eftersom indexet är en fil per kommun, 7,6 MB för Kungsbacka när
  beslutet togs, och växer med poolen. Ett verktyg som kapar långa filer
  får inte allt. Indexet delas per organ om det blir ett problem.
* Neutral, eftersom steg 3 inte blir ett eget kommando, som arkitekturen
  tänkte sig. Det blir det om något annat än webbplatsen behöver indexet.

### Confirmation

`tests/test_dokumentindex.py` prövar indexets rader och `llms.txt` på en liten
påhittad pool. Webbplatsens bygge i CI kör båda mot hela poolen.

## Pros and Cons of the Options

### A – Med webbplatsen, JSON Lines, `llms.txt`

* Good, eftersom bygget redan läser varje dokuments front matter.
* Good, eftersom JSON Lines bär listor och `null` utan omskrivning.
* Bad, eftersom indexet inte finns i repot.

### B – Eget kommando, incheckat

* Good, eftersom indexet följer med en klon.
* Bad, eftersom en fil med tusentals rader ändras varje natt, och samma
  sanning står två gånger.
* Bad, eftersom ett nytt steg i nattkörningen måste hållas i takt med
  poolen.

### C – CSV med ett urval

* Good, eftersom den går att öppna i ett kalkylark och GitHub visar den
  som en tabell.
* Bad, eftersom listorna inte får plats i en cell och måste bli antal,
  så att något tappas och urvalet måste motiveras.

### D – Bara `llms.txt`

* Good, eftersom det är minst kod.
* Bad, eftersom en AI då måste öppna tusentals filer för att veta vad som
  finns, och en statisk webbplats inte kan lista en katalog.

## More Information

Fas 0 föreslog att dela #56 i tre: indexet och ingången nu, protokollen
per paragraf som ett eget steg senare, och tidsserierna när tabellerna är
rättade (#84), eftersom serierna annars ärver dagens fel. Projektägaren
sade ja.

Agenten rekommenderade först CSV, med JSON Lines som alternativ, för att
CSV är lätt att öppna. Projektägaren frågade varför det skulle bli CSV och
inte JSON Lines. Svaret blev att JSON Lines är enklare: hela
front matter följer med utan urval och utan att listorna görs om till
antal, och koden blir kortare. En AI läser båda lika bra. Agenten bytte
rekommendation, och projektägaren valde JSON Lines.

Indexet checkas inte in, av samma skäl som luckorna (ADR-0020): det går
att räkna fram ur poolen, och en incheckad kopia skulle ge en diff varje
natt. Omprövas när något annat än webbplatsen behöver indexet, till
exempel paragrafindelningen eller tidsserierna.
