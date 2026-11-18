---
status: accepted
date: 2026-11-18
decision-makers: projektägaren
consulted: AI-agenten
---

# Nattkörningen sparar det klara var 15:e minut

## Context and Problem Statement

Nattkörningen har hittills sparat allt eller inget: steg 2 hämtar och
konverterar i upp till fem timmar, och först sedan körs kontrollerna och
grenen pushas (K11,
[ADR-0015](0015-nattkorningen-pa-egen-gren-och-pr.md)). Faller något
efter hämtningen går hela körningens arbete förlorat. Så gick det för
Region Hallands körning 2026-11-17: den konverterade 2 314 filer på fem
timmar, men pushen vägrades eftersom workflow-filen på `main` hade
ändrats under tiden, och allt kastades. Hur kan ett fel sent i en
körning kosta lite i stället för allt?

## Decision Drivers

* Ett avbrott ska kosta så lite arbete som möjligt.
* Bara det som klarat datakontrollerna får nå körningens gren, och bara
  genom en PR når det `main` (ADR-0015, ADR-0052).
* Historiken ska inte svälla: varje commit i ett repo med tusentals
  dokument tar plats för alltid.
* Projektägaren valde 2026-11-18 att spara var 15:e minut.

## Considered Options

* A – Steg 2 i delar om 15 minuter, och efter varje del kontroller,
  commit och push på körningens gren
* B – En commit och push efter varje dokument
* C – En commit och push efter varje möte
* D – Som i dag, allt på en gång efter steg 2

## Decision Outcome

Valt: A. `hamta --del 15` slutar efter 15 minuter, eller vid budgetens
mjuka gräns om den kommer först, och avslutar med kod 4 när kandidater
väntar inom budgeten. Körningen (`.github/nattkorning/hamta_i_delar.sh`)
kör då datakontrollerna, checkar in det klara och pushar det på jobbets
gren (`.github/nattkorning/spara.sh`), och startar nästa del. Kandidater
som redan är klara går fort i nästa del, eftersom steg 2 ser dem som
oförändrade utan att hämta något. Faller en kontroll eller en push
stoppar jobbet direkt; det som redan pushats står kvar på grenen, och
PR:en öppnas också när jobbet fallit, eftersom varje sparad del klarat
kontrollerna.

### Consequences

* Bra, eftersom ett avbrott kostar högst 15 minuters arbete.
* Bra, eftersom en körning ger ett tjugotal commits, inte tusentals.
* Dåligt, eftersom datakontrollerna körs ett tjugotal gånger per jobb. De
  tar under en minut i dag; växer de blir delen längre i praktiken.
* Dåligt, eftersom K11 inte längre lovar att ett fallerat jobb inte
  ändrar något: det som sparats före felet når `main` genom sin PR.

### Confirmation

`tests/test_delar.py` prövar delens gräns och slutkoden. Skripten körs
av nattkörningen; dess sammanfattning visar varje del.

## Pros and Cons of the Options

### A – Delar om 15 minuter

* Bra, eftersom förlusten är liten och historiken liten.
* Dåligt, eftersom upptäckten inte delas: faller den sparas inget, men
  den skriver heller inget i `data/`.

### B – Efter varje dokument

* Bra, eftersom inget går förlorat.
* Dåligt, eftersom 2 000 dokument per körning blir 2 000 commits och
  pushar, och repot sväller.

### C – Efter varje möte

* Neutralt: några hundra commits per körning, och ett möte med många
  bilagor kan ändå ta lång tid.

### D – Som i dag

* Dåligt, eftersom ett fel efter fem timmar kastar fem timmar.

## More Information

Regionens datarepo kör samma steg med kommunhandlingars kod och har sin
egen kopia av skripten i sitt workflow. Där står också kodversionen i en
egen fil, `kodversion.txt`, så att en ny version inte ändrar workflow-filen
medan en körning pågår: GitHub låter inte körningens token pusha en gren
vars workflow-fil skiljer sig från `main`.
