---
status: proposed
date: 2026-10-09
decision-makers: projektägaren
consulted: AI-agenten
---

# Luckorna räknas fram ur poolen på statussidan och lagras inte

## Context and Problem Statement

K7 säger att ett dokument som saknas från ett sammanträde som hållits
ska redovisas. Kravet hade ingen implementation
([#49](https://github.com/moggleif/kommunhandlingar/issues/49)), och
issuet frågade hur vi vet att ett möte hållits, hur ett ojusterat
protokoll skiljs från ett som saknas, hur ett inställt möte märks och var
en lucka registreras.

Poolen hade 2026-10-09 445 sammanträden i 15 organ. 373 hade kallelse,
handlingar och protokoll. Revisionen publicerar bara protokoll.
Mötessidorna listar varje möte som en rubrik, men bara tre rubriker i
de sparade sidorna saknade filer, och ingen sa "inställt". Arkivet
(ADR-0018) är avstängt.

## Decision Drivers

* **Hellre märka än gissa.** En lucka ska bara redovisas där något
  visar att mötet hölls.
* **Inget hårdkodat om en kommun.** Vilka dokument ett organ publicerar
  skiljer sig mellan organ och kommuner.
* **Poolen är tillståndet** (ADR-0004). Ett nytt tillstånd måste löna
  sig.
* **Enkelt först**, och inga diffar från en körning som inte hittat
  något nytt.

## Considered Options

* A – Luckorna räknas fram ur poolen när statussidan byggs
* B – En `.md` med en ny kvalitet `saknas` per lucka, som ADR-0004 gör
  för `ej-hamtad`
* C – Upptäckten skriver mötesrubrikerna till en fil i poolen, och
  luckorna räknas mot den
* D – Luckorna räknas i steg 3, indexet

## Decision Outcome

Valt: A, eftersom allt som behövs redan står i front matter och
statussidan redan räknar ur den (ADR-0012). Inget lagras, och det som
redovisas följer poolen när den ändras.

Reglerna:

* **Ett möte har hållits** när poolen har minst ett dokument från det
  och datumet har passerat. Ett möte utan dokument tas inte med.
* **Vilka typer som väntas** avgörs per organ av poolen: kallelse,
  handlingar och protokoll väntas för ett organ som har typen vid något
  annat sammanträde. Bilagor väntas aldrig.
* **Ett protokoll** saknas först 21 dagar efter mötet: kommunallagen ger
  14 dagar för justeringen, och en vecka till för anslag och
  publicering. Lagen gäller alla svenska kommuner, så gränsen står i
  koden.
* **Ett inställt möte** märks inte.
* **Ett `ej-hamtad`** är ingen lucka; dokumentet finns och syns under
  kvalitet (K6).
* **Källorna och tiden.** Luckan redovisas med organets källor i
  kommunfilen och sidans byggtid, inte med en tid per lucka.

### Consequences

* Good, eftersom ingenting nytt lagras och nattkörningen inte ändras.
* Good, eftersom regeln för väntade typer gör att ett organ som aldrig
  publicerar en typ, som revisionen och kallelser, inte får falska
  luckor, utan att något står i kommunfilen.
* Good, eftersom en fil som inget mönster känner igen syns som en lucka
  i stället för att försvinna tyst i sammanfattningen.
* Bad, eftersom ett möte utan något dokument inte syns, och ett organ
  som aldrig publicerat en typ aldrig får en lucka för den.
* Bad, eftersom en lucka inte har någon egen tid; den gäller poolen när
  sidan byggdes.
* Bad, eftersom ett möte som ställs in efter att kallelsen publicerats
  blir en lucka för protokollet.

### Confirmation

`tests/test_luckor.py` prövar reglerna med påhittade dokument, och
`tests/test_webbplats.py` att statussidan visar luckorna.

## Pros and Cons of the Options

### A – Räknas fram på statussidan

* Good, eftersom det är en ren funktion av front matter.
* Good, eftersom inga platshållare hamnar i poolen.
* Bad, eftersom möten utan dokument inte syns.

### B – En `.md` per lucka

* Good, eftersom luckan blir en fil som går att länka och läsa utan
  webbplatsen.
* Bad, eftersom filen är en platshållare för ett dokument vars namn och
  plats bara går att gissa.
* Bad, eftersom en tid för senaste försöket ger diffar varje natt, och
  utan den säger filen inte mer än A.

### C – Mötesrubrikerna som fil i poolen

* Good, eftersom möten utan dokument syns.
* Bad, eftersom det är ett nytt tillstånd som upptäckten måste skriva och
  datakontrollen kontrollera.
* Bad, eftersom ett möte utan filer inte går att skilja från ett
  inställt; det blir de luckor som är minst säkra.

### D – I indexet

* Good, eftersom indexet är där flödet säger att luckorna hör hemma.
* Bad, eftersom indexet inte finns, och ingen behöver det än.

## More Information

Agenten föreslog A i fas 0 och projektägaren sa ja till alla fyra
frågorna: räkna fram i stället för att lagra, möte känt genom minst ett
dokument, väntade typer per organ med 21 dagar för protokollet, och K7
omskrivet så att "vilka källor som prövats och när" blir organets
källor och sidans byggtid.

Den andra källan, som issuet tänkte sig kom med arkivet, behövs inte i
A: luckan bygger på att mötet har dokument, inte på att två källor
jämförts. Fyller arkivet en lucka när det slås på försvinner luckan
från sidan av sig själv.

Med reglerna gav poolen 2026-10-09 30 luckor: 24 möten utan handlingar,
5 utan kallelse och ett utan protokoll. Mötena utan handlingar kan vara
luckor i källan eller filer som inget mönster känner igen; att de syns
är poängen.

C prövas igen om möten utan dokument visar sig vara vanliga, och en
lista med inställda möten i kommunfilen, som `rattelser`, om ett inställt
möte blir en lucka.
