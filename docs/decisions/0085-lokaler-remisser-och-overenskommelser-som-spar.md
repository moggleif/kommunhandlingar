---
status: accepted
date: 2026-11-17
decision-makers: projektägaren
consulted: AI-agenten
---

# Lokaler och investeringar, remisser och yttranden och överenskommelser och vårdval blir tre nya slag av spår över tid

## Context and Problem Statement

Region Hallands handlingar hämtas till ett eget datarepo med samma kod
(ADR-0080). Regionens sidor ska ha samma sidor över tid som Kungsbackas.
En analys av de första nämndernas handlingar, Driftnämnden Närsjukvård och
den gemensamma nämnden för hemsjukvård och hjälpmedel, visade att mål och
direktiv, initiativärenden, handlingsplaner, redovisningar och granskningar
passar som de är. Tre saker gör det inte:

* **Lokaler.** Kungsbackas lokalbehov följer kommunens lokalplan med
  löpnummer och prioritet. Regionens nämnder beslutar i stället om egna
  lokaler, avsiktsförklaringar om hyresavtal och investeringar.
* **Remisser.** Regionens nämnder svarar på statliga utredningar och på
  regionens egna strategier. Det är vad nämnden tycker utåt, och det
  har ingen sida i dag.
* **Överenskommelser och vårdval.** Regionen styr mycket genom avtal:
  hemsjukvårdsöverenskommelsen med kommunerna, statens överenskommelser
  och Vårdval Halland. Det har ingen sida i dag.

Detaljplaner och projekt behövs inte för regionen, men de visas redan
bara när filen finns.

## Decision Drivers

* **Inget hårdkodat om en kommun:** slagen är generella, och en kommun
  som har en fil får sidan.
* **Ingen kod för säkerhets skull:** sidorna för spår över tid finns
  redan (ADR-0057–0059, ADR-0065–0067).
* **Varje uppgift bär sin härkomst.**

## Considered Options

* A – Tre nya slag med egna faser, och översikten visar bara kolumner som
  kommunen har
* B – Lokalbehovens slag med ett annat namn per kommun i kommunfilen,
  och remisser och överenskommelser som redovisningar
* C – Inga nya slag; regionen använder bara de sex som passar

## Decision Outcome

Valt: A, eftersom regionens lokaler, remisser och avtal har egna steg som
inte ryms i lokalplanens eller redovisningarnas faser, och tre slag är
bara data.

* **`investeringar`** ("Lokaler och investeringar"): `behov`, `beslut`,
  `pagar`, `utfort`. Hyresavtal står här.
* **`remisser`** ("Remisser och yttranden"): `remiss`, `yttrande`,
  `beslut`. Motioner står bland initiativärendena, revisionsrapporter
  bland granskningarna.
* **`overenskommelser`** ("Överenskommelser och vårdval"): `forslag`,
  `beslut`, `revidering`, `uppfoljning`, `uppsagd`.
* **Översikten** har bara kolumner för slag som något av kommunens organ
  har, så att Kungsbacka inte får tre tomma kolumner och regionen inte
  får lokalbehov och detaljplaner.
* **Listan** över slagen flyttar till `slagen.py`, eftersom `sparslag.py`
  annars går över den hårda gränsen. Varje nytt slag står i en egen fil,
  som granskningarna.
* **Texterna** på sidorna om granskningar och handlingsplaner säger
  "revisionen", "styrelsen" och "gemensamma planer" i stället för
  "kommunrevisionen", "kommunstyrelsen" och "kommunens planer".

### Consequences

* Good, eftersom regionens sidor visar det som skiljer regionen från
  kommunen, och en kommun kan använda slagen när den vill.
* Good, eftersom översikten blir smalare för båda.
* Neutral, eftersom varje slag är handarbete per nämnd, som de andra.
* Bad, eftersom slagen nu står i fem filer.

### Confirmation

`tests/test_nya_spar.py` prövar att varje nytt slag får en sida och en
flik, och att en okänd fas stoppar bygget. `tests/test_navigering.py`
prövar att översikten bara har kolumner för sidor som kommunen har.

## Pros and Cons of the Options

### A – Tre nya slag

* Good, eftersom faserna passar det som står i handlingarna.
* Bad, eftersom det blir fler slag att hålla isär.

### B – Annat namn per kommun och redovisningarnas faser

* Good, eftersom inga nya slag behövs.
* Bad, eftersom lokalplanens löpnummer och prioritet inte finns i
  regionen, och en remiss eller ett avtal är inte en redovisning: ett
  yttrande eller en uppsägning har ingen fas där.

### C – Inga nya slag

* Good, eftersom inget nytt byggs.
* Bad, eftersom det som skiljer regionen från kommunen inte syns.

## More Information

Projektägaren bad 2026-11-17 om en analys av vilka kolumner regionen
behöver, och sa sedan ja till AI-agentens förslag: de sex kolumner som
passar, lokalbehov ersatt av lokaler och investeringar, inga
detaljplaner och projekt, och två nya kolumner för remisser och
överenskommelser. AI-agenten valde tre nya slag i stället för att döpa om
lokalbehoven per kommun, eftersom faserna skiljer sig. Intern kontroll och
taxor fanns också i handlingarna men får ingen sida, som i kommunen.
