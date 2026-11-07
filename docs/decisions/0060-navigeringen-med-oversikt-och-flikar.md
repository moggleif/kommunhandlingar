---
status: accepted
date: 2026-11-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Kommunens sida blir en översikt över organen och deras sidor, organets sidor får flikar och statusen en egen sida

## Context and Problem Statement

Menyn har startsidan, kommunerna och avvikelserna. Kalendern och sidorna
över tid – mål och direktiv, lokalbehov, initiativärenden och
handlingsplaner – nås bara genom en länk på statussidan eller en textrad
på organets sida, och kommunens sida är en tabell över dokument och
kvalitet. Sidorna över tid finns i dag för ett par organ men ska göras
för alla nämnder ([#210](https://github.com/moggleif/kommunhandlingar/issues/210)).
Hur hittar läsaren dem när varje nämnd har fyra eller fler?

## Decision Drivers

* **Varje sida ska gå att nå i högst två klick** från kommunens sida.
* **En ny nämnd eller en ny slags sida ska synas utan ny navigering.**
* **Statisk HTML, inget skript** för navigeringen.
* **Inget hårdkodat om en kommun.**
* **Adresserna som redan finns ska fungera.**

## Considered Options

* A – Kommunens sida som översikt organ × sida, flikar på organets
  sidor, statusen på en egen sida
* B – En meny med en rullgardin per organ
* C – En sida per slags sida över tid som listar alla organ
  (`<kommun>/lokalbehov.html` …)
* D – Behåll sidorna, men lägg kalendern och statusen i menyn

## Decision Outcome

Valt: A, eftersom översikten visar både vad som finns och vad som
återstår, och flikarna gör att alla organs sidor ser likadana ut.

* **Menyn**: Start, för varje kommun dess sida, kalendern när den finns och
  Poolens status, och sist Avvikelser.
* **Kommunens sida** (`<kommun>.html`) börjar med antalet dokument och
  har en rad per organ med antalet sammanträden och en kolumn per slags
  sida över tid med antalet mål eller saker ("12 behov"), eller ett
  streck. Utskotten står under sin nämnd med det `hor_till` som
  kommunfilen redan har för kalenderns färger.
* **Grupperna** (fullmäktige och styrelse, nämnderna, övriga) står i
  kommunfilen: `grupper` med rubrikerna i ordning och `grupp` på varje
  organ som inte är utskott. Utan grupper blir sidan en enda tabell.
* **Statussidan** flyttar till `<kommun>/status.html` med samma innehåll.
* **Flikarna** ersätter textraden och stigen på organets sida och på
  dess sidor över tid. Översikten och flikarna byggs ur samma lista.
* Övriga adresser är oförändrade.

### Consequences

* Good, eftersom en nämnd som får en ny sida syns i både översikten och
  flikarna utan att någon navigering ändras.
* Good, eftersom strecken visar vad som är gjort och inte.
* Neutral, eftersom den som bokmärkt statustabellerna hittar dem via menyn.
* Bad, eftersom översikten blir bred när slagen blir fler; tabellen
  rullar i sidled på en smal skärm.

### Confirmation

`tests/test_navigering.py` prövar menyn, översiktens kolumner, antal och
streck, att utskottet står under sin nämnd och flikarna på organets sida
och en sida över tid. `tests/test_webbplats.py` prövar statussidan på sin
nya adress.

## Pros and Cons of the Options

### A – Översikt, flikar och egen statussida

* Good, eftersom allt nås i två klick och utan skript.
* Bad, eftersom kommunens sida inte längre visar dokumenten och kvaliteten
  direkt.

### B – Rullgardiner per organ

* Good, eftersom allt nås från varje sida.
* Bad, eftersom sjutton organ med fyra sidor var blir en lång meny som
  behöver skript eller `<details>` för att gå att använda på en telefon.

### C – En sida per slags sida över tid

* Good, eftersom det går att jämföra nämndernas lokalbehov.
* Bad, eftersom det är fyra nya sidor som var och en bara är en lista
  över länkar, och organets sidor fortfarande hänger löst.

### D – Bara kalendern och statusen i menyn

* Good, eftersom ändringen är minst.
* Bad, eftersom sidorna över tid fortfarande gömmer sig på organets sida.

## More Information

Projektägaren tyckte att navigeringen "inte var någon höjdare" och skulle
snart göra sidorna över tid, som i dag finns för nämnden för Gymnasium
& Arbetsmarknad (`ga`), för alla nämnder. AI-agenten föreslog A med skisser,
där översikten också delade organen i grupper (fullmäktige och styrelse,
nämnder, övriga) och flikarna hade antalet i sig. Projektägaren sa ja.

När sidan byggdes första gången lät agenten grupperna, enheterna och
raden om dokumenten vänta, eftersom grupperna kräver en ny uppgift i
kommunfilen. Projektägaren frågade varför sidan inte såg ut som skissen,
och de lades till. Grupperna står i kommunfilen och inte i koden,
eftersom vilka organ en kommun har och hur de hör ihop är kommunens.
Antalet står i översikten men inte i flikarna, eftersom sidorna över tid
inte har organets sammanträden att räkna. Rubrikerna på sidorna över tid
är som förut.

Brödsmulorna på dokumentens sidor och kalendern står kvar.
