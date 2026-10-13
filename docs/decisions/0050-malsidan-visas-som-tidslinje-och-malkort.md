---
status: proposed
date: 2026-10-13
decision-makers: projektägaren
consulted: AI-agenten
---

# Målsidan visas som en tidslinje över alla mål och ett kort per mål, med sammandraget överst

## Context and Problem Statement

Sidan om ett organs mål och direktiv (K26–K28) har en översikt med ett
mål per rad och ett år per kolumn, och sedan ett avsnitt per år. För
GA blir översikten 47 rader och 14 kolumner där de flesta rutorna är
tomma, och sidan blir mycket lång. Det går att läsa ut vad som gällde ett
visst år, men inte att se på en gång vilka mål som levt länge, när de
bytt rubrik och hur nämnden följt upp dem
([#151](https://github.com/moggleif/kommunhandlingar/issues/151)).
Projektägaren vill att sidan ska bli bra att titta på, inte bara visa
fakta. Hur ska den se ut?

## Decision Drivers

* **Överblick först.** Läsaren ska se målens livslängd och status utan
  att rulla genom alla år.
* **Varje uppgift bär sin härkomst.** Varje rad ska fortfarande gå att
  följa till sin sida i källan.
* **Tomt är inte noll.** Luckor i poolen ska synas som luckor.
* **Sidan fungerar utan skript.** Ingen kod för säkerhets skull, och
  inga nya beroenden.

## Considered Options

* A – En tidslinje: ett band per mål över åren, och en panel med målets
  historik
* B – Ett år i taget: ett val av år, årets mål som kort och vad som är
  nytt eller försvann
* C – Målkort: ett kort per mål med en remsa per år och en hopfälld
  historik, de som gäller i dag först
* C med A:s tidslinje: korten och tidslinjen på samma sida

## Decision Outcome

Valt: C med A:s tidslinje (projektägarens val). Det ger både en
överblick över alla mål och en plats för varje måls hela historik.

* **Ordningen** på sidan är sammandraget (det senaste årets antal och
  grafen, med tabellen hopfälld), ett urval, tidslinjen och korten.
* **Åren** går från målens första till sista år, som i antalet per år.
  Poolens dokument från år före målen ger inga tomma kolumner; sidan
  säger i stället från vilket år poolen har dokument. Ett år med
  dokument men utan mål står som "inga mål", så att det inte tas för en
  lucka.
* **Tidslinjen** har en rad per mål, nämndmålen för sig och direktiven
  för sig. Ett år med målet är en del av ett band med årets status: ett
  utfall går före en rapport, en prognos och beslutet. Ett år utan
  uppföljning har en punkt för beslutet. En ny rubrik är en markering vid
  året. Sist står nämndens uppföljningar och dragningar ur protokollen
  (K28) på samma tidsaxel. Ett mål som varit både nämndmål och direktiv
  står under sitt senaste slag, märkt med det andra.
* **Korten** kommer i ordning efter sista och första år. Ett kort har
  slaget, åren, den senaste rubriken och de tidigare, den senaste
  formuleringen, en remsa med ett fält per år och en hopfälld historik.
  Historiken ersätter avsnitten per år.
* **Urvalet** är knappar för alla, de som gäller det senaste året,
  nämndmål, direktiv (bara de slag som finns) och de som bytt rubrik. Det gäller både tidslinjen
  och korten. Ett klick på ett mål i tidslinjen går till kortet och
  öppnar historiken. Utan skript står allt, och länkarna går till korten.
* **Stilen** står i en egen fil bredvid skriptet, `webbplats/mal.css`.

### Consequences

* Good, eftersom hela GA:s målhistoria ryms på en skärmbredd.
* Good, eftersom nämndens uppföljningar och målen ligger på samma
  tidsaxel.
* Good, eftersom ett mål med alla rubriker och rader står på ett ställe.
* Bad, eftersom en läsare som vill se allt från ett visst år får läsa
  kolumnen i tidslinjen och öppna korten, i stället för ett avsnitt.
* Bad, eftersom tidslinjen behöver rullas i sidled på en smal skärm.

### Confirmation

`tests/test_malkort.py` prövar tidslinjen, korten, urvalet och
sammandraget med en påhittad kommun, och `tests/test_mal.py` att varje
rad har sin status och källa.

## Pros and Cons of the Options

### A – Tidslinje med panel

* Good, eftersom den visar målens livslängd och namnbyten tydligast.
* Bad, eftersom formuleringarna bara syns i panelen, ett mål i taget.

### B – Ett år i taget

* Good, eftersom den svarar på vad nämnden ville ett visst år och vad
  som ändrades från året innan.
* Bad, eftersom ett mål över många år delas upp på lika många vyer.

### C – Målkort

* Good, eftersom varje mål har en egen plats med formulering och
  historik.
* Bad, eftersom korten ensamma inte visar hur målen följer på varandra.

### C med A:s tidslinje

* Good, eftersom den har både överblicken och historiken.
* Bad, eftersom sidan får två vyer över samma mål.

## More Information

AI-agenten tog fram de tre skisserna med GA:s riktiga data och
rekommenderade A. Projektägaren valde C och bad att A:s tidslinje med
alla mål skulle läggas till.
