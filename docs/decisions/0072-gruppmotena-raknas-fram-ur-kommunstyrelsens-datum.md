---
status: proposed
date: 2026-11-14
decision-makers: projektägaren
consulted: AI-agenten
---

# Partiernas gruppmöten räknas fram ur kommunstyrelsens datum när kalendern byggs, och visas diskret som en vana

## Context and Problem Statement

Partierna har gruppmöte måndagskvällen före varje sammanträde i
kommunstyrelsen
([#269](https://github.com/moggleif/kommunhandlingar/issues/269)). Det är
en viktig händelse i det politiska året, men inget beslutat sammanträde:
det står inte i någon mötessida eller i något protokoll. Kalendern
([ADR-0032](0032-kalendern-las-ur-besluten-och-skrivs-for-hand.md)) har
bara sammanträden med en källa. Hur kommer gruppmötena in i kalendern
utan att se ut som beslutade sammanträden, och så att de följer med när
kommunstyrelsens datum läggs till?

## Decision Drivers

* **Det ska följa med av sig självt** när ett nytt datum för
  kommunstyrelsen läggs in, för hand nu eller av en automatik senare.
* **Inget hårdkodat om en kommun** (AGENTS.md). Organet och veckodagen hör
  till kommunen.
* **Hellre märka än gissa.** Ett datum utan källa får inte se ut som ett
  med källa.
* **Enkelt först.** Inget nytt filformat för en enda vana.

## Considered Options

* A – Gruppmötena räknas fram ur organets sammanträden när sidan byggs,
  med regeln i kommunfilen
* B – Gruppmötena skrivs som egna rader i kalenderfilen
* C – En egen fil för återkommande händelser, `kalender/<kommun>-vanor.csv`
* D – Bara en mening på kalendersidan, inga datum

## Decision Outcome

Valt: A, eftersom gruppmötet då alltid följer kommunstyrelsens datum,
också när ett datum flyttas, utan att någon behöver komma ihåg det.

* **Regeln** står i kommunfilen som `gruppmote = { fore = "ks",
  veckodag = "måndag", tid = "kväll" }`: organet, veckodagen före och
  tiden som visas.
* **Datumet** är den närmaste veckodagen före sammanträdet, aldrig samma
  dag. Ett sammanträde på en tisdag ger måndagen dagen före.
* **Bara framåt.** Gruppmöten före dagen webbplatsen byggs tas inte med,
  eftersom det inte går att veta om de hölls. Nästa bygge tar bort dem
  som passerat.
* **Visningen** är diskret: en ruta med prickad grå kant och texten
  "Gruppmöte kväll", inte i ett organs färg. I listan och urvalet heter
  det "Partiernas gruppmöte inför Kommunstyrelsen", och en mening över
  urvalet säger att det är en vana hos partierna, inget beslutat
  sammanträde, och att datumen är räknade, inte lästa i en källa. Det går
  att välja bort som ett organ.
* **Gruppmötena räknas inte** bland sammanträdena under Kvalitet och har
  ingen rad under Källor.

### Consequences

* Good, eftersom gruppmötet flyttar med när kommunstyrelsen flyttar ett
  sammanträde.
* Good, eftersom en annan kommun med samma vana bara behöver en rad i sin
  kommunfil.
* Bad, eftersom ett inställt eller flyttat gruppmöte inte syns; kalendern
  visar vanan, inte det enskilda mötet.
* Bad, eftersom kalendersidan har en sorts händelse som inte är ett
  sammanträde, och vyerna får ett undantag för dess namn.
* Neutral, eftersom regeln bara rymmer ett organ. En lista blir det när
  en andra vana behövs.

### Confirmation

`tests/test_gruppmoten.py` prövar regeln i kommunfilen, datumen, att bara
kommande tas med och hur sidan visar dem, och läser Kungsbackas
kommunfil.

## Pros and Cons of the Options

### A – Räknas fram ur sammanträdena

* Good, eftersom inget datum skrivs två gånger.
* Good, eftersom en ny rad för kommunstyrelsen räcker.
* Bad, eftersom ett undantag ett enskilt år inte går att skriva in.

### B – Egna rader i kalenderfilen

* Good, eftersom ett inställt gruppmöte kan strykas.
* Bad, eftersom varje rad kräver en källa, och det finns ingen.
* Bad, eftersom raderna måste skrivas för hand och glider isär från
  kommunstyrelsens datum.

### C – En egen fil för vanor

* Good, eftersom det rymmer fler vanor och undantag.
* Bad, eftersom det är ett nytt filformat och en ny kontroll för en enda
  vana.

### D – Bara en mening

* Good, eftersom det är enklast.
* Bad, eftersom besökaren själv får räkna ut dagen, och gruppmötet inte
  syns i månadsvyn.

## More Information

Projektägaren bad om gruppmötet "på ett snyggt och informellt sätt" och
att det skulle med i automatiken när kommunstyrelsens möten läses in.
Någon sådan automatik finns inte: kalenderfilen skrivs för hand. Agenten
föreslog därför A, så att gruppmötet följer varje rad för
kommunstyrelsen, hur raden än kommer in. Projektägaren valde bara
kommunstyrelsen, inte fullmäktige, och bara kommande gruppmöten.
