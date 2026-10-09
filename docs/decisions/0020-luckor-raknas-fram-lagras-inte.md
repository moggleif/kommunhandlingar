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

Organen publicerar olika: en del aldrig kallelser, en del kallelsen och
handlingarna i en och samma fil, ibland med rubriken "Handlingar", ibland
"Kallelse och handlingar". Mötessidorna listar varje möte som en rubrik,
och ett möte utan filer går inte att skilja från ett inställt. Hur
Kungsbacka publicerar står i
[kallor/kungsbacka.md](../kallor/kungsbacka.md). Arkivet (ADR-0018) är
avstängt.

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
* **Vad som väntas** avgörs per organ av poolen, i två grupper: kallelse
  eller handlingar, och protokoll. En grupp väntas för ett organ som har
  den vid något annat sammanträde, och den saknas när mötet inte har
  någon av dess typer. Kallelsen och handlingarna är en grupp eftersom de
  ofta är samma fil, under endera namnet. Bilagor väntas aldrig.
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
  publicerar en typ inte får falska luckor, utan att något står i
  kommunfilen.
* Good, eftersom en fil som inget mönster känner igen syns som en lucka
  i stället för att försvinna tyst i sammanfattningen.
* Bad, eftersom ett möte med bara kallelsen, när handlingarna verkligen
  saknas, inte blir en lucka.
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

I fas 0 väntades varje typ för sig. Med den regeln gav poolen 2026-10-09
29 möten med luckor. Granskningen visade att de flesta var falska: filer
med rubriken "Handlingar för möte …" börjar med kallelsen, och "Kallelse
och handlingar för möte …" är båda. Agenten slog därför ihop kallelse
och handlingar till en grupp. Då återstod två luckor, båda trovärdiga:
ett möte med kallelse och handlingar men inget protokoll, och ett med
protokoll men varken kallelse eller handlingar. Att en grupp missar ett
möte där bara handlingarna saknas bedömdes som bättre än att visa
luckor som inte finns ("hellre märka än gissa").

ADR-0004 sköt upp två frågor till luckorna. "Vilka källor som prövats
och när" besvaras här: organets källor och sidans byggtid. Om en fil som
länkas från flera sammanträden ska räknas för det andra avgörs inte: den
står på det första mötets plats, och det andra mötet blir en lucka om
det inte har något annat dokument i gruppen. Det är en sann beskrivning
av poolen, och frågan tas upp om det visar sig hända.

Den andra källan, som issuet tänkte sig kom med arkivet, behövs inte i
A: luckan bygger på att mötet har dokument, inte på att två källor
jämförts. Fyller arkivet en lucka när det slås på försvinner luckan
från sidan av sig själv.

C prövas igen om möten utan dokument visar sig vara vanliga, och en
lista med inställda möten i kommunfilen, som `rattelser`, om ett inställt
möte blir en lucka.
