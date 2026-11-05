---
status: proposed
date: 2026-11-05
decision-makers: projektägaren
consulted: AI-agenten
---

# Ett tillfälligt fel på `robots.txt` försöks igen och stoppar inte arkivet, och körningen går två gånger om dygnet tills arkivet är ikapp

## Context and Problem Statement

Statussidan visade 2026-11-05 214 luckor, nästan alla 2013–2023, den del
av poolen som fylls ur arkivet (ADR-0018, ADR-0047). Arkivet var inte
ikapp: körningen 2026-11-04 konverterade 80 filer, och 1 387 väntade på
nästa körning
([#215](https://github.com/moggleif/kommunhandlingar/issues/215)).

Två fel på `robots.txt` gjorde det långsammare än det behövde vara:

1. **En omdirigering stoppade hela körningen.** Tre av de åtta senaste
   nattkörningarna stoppades efter en minut, när kungsbacka.se svarade 307
   på `robots.txt`. Upptäckten stoppas då (K2), och arkivet körs inte,
   fast det inte hämtar något från kungsbacka.se. Nästa körning har gått
   igenom varje gång.
2. **Ett fel på `robots.txt` mindes för värden hela körningen** (K10,
   ADR-0013). En enda gång när web.archive.org inte gick att nå gjorde att
   varje fil från arkivet därefter blev `ej-hamtad` med
   `robots-anslutning`, utan att något hämtades. ~475 dokument i poolen
   har den orsaken.

Hur kommer arkivet ikapp snabbare, utan att hämtningen blir mindre artig?

## Decision Drivers

* **Artig hämtning** (AGENTS.md): `robots.txt` följs, intervallet hålls,
  inget hämtas utan att ha prövats mot `robots.txt`.
* **Hellre stanna än gissa**: en värd vars `robots.txt` inte går att läsa
  hämtas det inget från.
* **Ett tillfälligt fel ska kosta lite**: en fil, inte en natt.
* **Enkelhet**: ingen ny konfiguration.

## Considered Options

* A – Nya försök på `robots.txt` vid omdirigering och `anslutning`, felet
  minns inte, och ett stopp i det levande hoppar bara över kommunens
  levande steg 2
* B – Följa omdirigeringen på `robots.txt`, som RFC 9309 tillåter
* C – Minnas felet en stund, till exempel en kvart, i stället för hela
  körningen
* D – Bara köra oftare, och låta felen vara

## Decision Outcome

Valt: A, tillsammans med två körningar om dygnet ur D, eftersom A tar bort
orsakerna och den extra körningen tar igen tiden.

* **Nya försök.** När `robots.txt` svarar med en omdirigering, eller
  värden inte går att nå, görs nya försök med samma väntan som vid 429 och
  5xx (5, 10 och 20 sekunder). Omdirigeringen följs inte. För alla andra
  adresser gäller K10 som förut.
* **Felet minns inte.** Går `robots.txt` inte att hämta efter försöken
  hämtas inget från värden för den adressen, som förut, men nästa adress
  på värden prövar `robots.txt` igen. Regler som gick att läsa minns
  fortfarande hela körningen.
* **Ett stopp i det levande stoppar inte arkivet.** Stoppas upptäckten i
  en kommuns levande källor för att en källsida inte går att hämta,
  avslutas den med en egen kod (3). Nattkörningen hoppar då över
  kommunens levande steg 2, skriver adressen och orsaken i
  sammanfattningen och går vidare till arkivet. Ett konfigurationsfel
  eller ett oväntat fel i upptäckten stoppar körningen som förut.
  Upptäckten skriver bara i arbetskatalogen, så inget halvfärdigt kan nå
  poolen. Ett fel i det levande steg 2 stoppar körningen som förut (K11).
* **Två körningar om dygnet**, i samma `concurrency`-grupp, så att de
  aldrig går samtidigt. Den andra raden i `cron` tas bort när arkivet är
  ikapp, det vill säga när sammanfattningen inte längre har "väntar på
  nästa körning" för arkivet.

### Consequences

* Good, eftersom en blipp mot arkivet kostar en fil och inte resten av
  natten, och en omdirigering på kungsbacka.se inte längre stoppar
  arkivet.
* Good, eftersom ~475 dokument med `robots-anslutning` och de 1 387 som
  väntar hämtas på ungefär en vecka i stället för två–tre.
* Good, eftersom inget hämtas utan att ha prövats mot `robots.txt`.
* Bad, eftersom en värd som är nere hela natten nu får `robots.txt`
  frågad en gång per fil, med nya försök. Intervallet och väntan gäller
  fortfarande, så det blir som mest ett anrop var femte sekund. Svarar
  värden inte alls, utan når tidsgränsen, kostar varje fil runt fyra och
  en halv minut, och arkivets del av natten kan gå åt; tidsbudgeten sätter
  taket, och inget som redan finns i poolen påverkas.
* Bad, eftersom en natt där det levande stoppas checkar in arkivets filer
  utan dagens nya sammanträden. De hämtas nästa körning.
* Neutral, eftersom den andra raden i `cron` måste tas bort för hand.

### Confirmation

`tests/test_klient.py` prövar nya försök vid omdirigering och
`anslutning` på `robots.txt`, att en omdirigering på en vanlig adress
fortfarande inte försöks igen, och att nästa adress prövar `robots.txt`
igen efter ett fel. Nattkörningens sammanfattning visar om arkivet kommer
ikapp.

## Pros and Cons of the Options

### A – Nya försök, felet minns inte, stoppet hoppar bara över det levande

* Good, eftersom varje orsak tas bort där den uppstår.
* Good, eftersom inget nytt behöver konfigureras.
* Bad, eftersom en värd som är nere frågas oftare (se ovan).

### B – Följa omdirigeringen på `robots.txt`

* Good, eftersom RFC 9309 säger att en läsare bör följa minst fem
  omdirigeringar.
* Bad, eftersom vi inte vet vart kungsbacka.se:s 307 leder; samma adress
  svarar 200 nästa gång. Leder den till en sida som inte är `robots.txt`
  blir resultatet inga regler, och då hämtas allt.
* Bad, eftersom klienten i övrigt aldrig följer omdirigeringar (ADR-0013),
  och ett undantag med en egen hanterare är mer kod än nya försök.

### C – Minnas felet en stund

* Good, eftersom en värd som är nere frågas mer sällan.
* Bad, eftersom varje fil under den stunden blir `ej-hamtad` direkt, utan
  nätverk; hundratals filer kan hinna märkas på några sekunder. Det är
  just det felet som ska bort.
* Bad, eftersom en tid till står i koden.

### D – Bara köra oftare

* Good, eftersom det är en rad.
* Bad, eftersom var tredje körning ändå dör efter en minut, och en blipp
  fortfarande märker resten av natten.

## More Information

Analysen gjordes i fas 0 mot poolen och nattkörningarnas loggar 29
oktober–5 november 2026. Den hittade också ~690 filer i arkivet som inte
blir kandidater för att de saknar datum eller typ, och att statussidan
inte visar år då ett organ saknar varje dokument. De tas i en egen
ändring.

Agenten övervägde att låta hela det levande steget fortsätta vid fel,
som arkivets (`continue-on-error`). Det avvisades: ett oväntat fel i steg
2 kan ha skrivit i `data/`, och K11 säger att en sådan körning inte ska nå
poolen. Upptäckten skriver bara i arbetskatalogen, så den kan hoppas över
utan den risken.

Att `anslutning` försöks igen bara för `robots.txt` och inte för filerna
är en avvägning. Den första kontakten med en värd är `robots.txt`, så det
är där ett avbrott syns; går `robots.txt` att läsa men en fil inte, blir
filen `ej-hamtad` och försöks igen nästa körning (K6), utan att något
annat påverkas.
