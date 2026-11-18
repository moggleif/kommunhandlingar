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
gren (`.github/nattkorning/spara.sh`), och startar nästa del.

Varje kandidat provas en gång per körning, som förut. Steg 2 skriver
källnycklarna det provat i en fil bredvid kandidatlistan och hoppar över
dem i nästa del. Utan det tas en omkonvertering som når dokumentets
gräns på 30 minuter (K52), eller ett dokument som inte går att hämta,
om först i varje del, och resten av jobbet kommer aldrig fram. Ett
dokument som redan är helt går ändå fort, men ett `ej-hamtad` hämtas om.

Faller en kontroll eller en push stoppar jobbet direkt; det som redan
pushats står kvar på grenen. Grenen får sin PR också när jobbet fallit,
eftersom varje sparad del klarat kontrollerna, men inte när körningen
avbrutits för hand: då är avbrottet en nödbroms. Grenen har körningens
försök i namnet, så att en omkörning inte krockar med det första
försökets gren.

Beslutet ändrar två äldre. ADR-0015 och K11 lovade att ett jobb som
fallit inte ändrar något; nu når det som sparats före felet `main`.
ADR-0077 lät arkivets jobb börja från `main` när mötenas jobb fallit; nu
börjar det från mötenas gren när den finns, eftersom den bara har
kontrollerat innehåll. Incheckningens action
(`.github/actions/checka-in`) ersätts av skripten och av
`.github/actions/grenen`, som ger grenen som output också när jobbet
fallit.

### Consequences

* Bra, eftersom ett avbrott kostar högst en del: 15 minuter, plus ett
  dokument som pågick, upp till dokumentets gräns på 30 minuter.
* Bra, eftersom en körning ger ett tjugotal commits, inte tusentals.
* Dåligt, eftersom datakontrollerna körs ett tjugotal gånger per jobb. De
  tar omkring en minut för Kungsbackas pool; växer de blir delen längre
  i praktiken.
* Dåligt, eftersom sammanfattningen får en rad med utfallet per del, och
  "väntar på nästa körning" betyder där nästa del.

### Confirmation

`tests/test_delar.py` prövar delens gräns, slutkoden och att en provad
kandidat inte tas om. Skripten prövades före beslutet med en falsk
`python` och ett lokalt repo som remote: tre delar ger tre commits på
grenen, en fallerande kontroll stoppar utan push, och en commit vars
push föll pushas av nästa sparning. Nattkörningens sammanfattning visar
varje del.

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

Diskussion. Projektägaren frågade om ett fel kunde ge tjugo kvartar i
rad som fallerar. Svaret är nej: ett fel i kontrollerna eller pushen
stoppar jobbet direkt, och det som sparats står kvar. Granskningen
invände att en del börjar om från början av kandidatlistan, så att ett
dokument som inte går att hämta eller konvertera skulle tas om i varje
del; därför filen med provade kandidater. Den invände också att en push
som föll i arkivets steg, som får falla utan att stoppa jobbet, kunde
försvinna tyst; därför pushar `spara.sh` varje commit som inte nått
remote, också när inget nytt har ändrats. Att spara med en `trap` när
jobbet faller valdes bort: efter ett oväntat fel är poolen inte känd som
hel, och det är just det kontrollerna ska avgöra före varje sparning.

Regionens datarepo kör samma steg med kommunhandlingars kod och har sin
egen kopia av slingan i sitt workflow. Där står också kodversionen i en
egen fil, `kodversion.txt`, så att en ny version inte ändrar workflow-filen
medan en körning pågår: GitHub låter inte körningens token pusha en gren
vars workflow-fil skiljer sig från `main`.
