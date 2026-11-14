---
status: proposed
date: 2026-11-12
decision-makers: projektägaren
consulted: AI-agenten
---

# Projektsidornas filer blir handlingar under ett eget organ, daterade med dagen de lades upp

## Context and Problem Statement

Kommunens webbplats har en lista med aktuella projekt inom bygga, bo och
miljö: detaljplaner, planprogram, utbyggnad av vatten och avlopp, vägar,
skolor. I Kungsbacka var det 146 projekt 2026-11-12, och 81 av dem hade
filer, sammanlagt cirka 690 och 3 GB: planbeskrivningar, plankartor,
samrådsredogörelser, granskningsutlåtanden och utredningar (geoteknik,
dagvatten, buller, trafik, naturvärden). Inget av det fanns i poolen;
byggnadsnämndens handlingar har bara tjänsteskrivelserna
([#254](https://github.com/moggleif/kommunhandlingar/issues/254)).

Projektägaren vill ha in alla filerna, också utredningarna, som
handlingar under byggnadsnämnden, som arbetsutskottet står under den, och
i nattkörningen. Hur de ska visas bestäms senare.

Poolens modell är organ, sammanträde och dokument (ADR-0003). Ett projekt
är inget sammanträde och har inget datum. Hur passar projektens filer in?

## Decision Drivers

* **Ingen ny modell** för det som ryms i den gamla: datakontrollen,
  webbplatsen och steg 2 ska fungera som de är.
* **Projektet ska gå att se** i dokumentets plats, eftersom sidan som
  visar vilket projekt en fil hörde till kan försvinna när projektet är
  klart (ADR-0007).
* **Inget hårdkodat om en kommun** (AGENTS.md).
* **Ett fel på en projektsida får inte stoppa mötena**: nattkörningen
  hoppar över kommunens levande steg 2 när en källsida stoppar
  upptäckten (ADR-0061).

## Considered Options

* A – Ett eget organ under byggnadsnämnden; varje fil är handlingar med
  dagen den lades upp som datum och projektets och filens namn som namn
* B – En ny nivå i modellen, projekt i stället för sammanträde, med egna
  fält i front matter
* C – Som A, men med dagen filen först hittades som datum
* D – Ett organ per projekt

## Decision Outcome

Valt: A, eftersom det ryms i modellen som den är och ändå bär projektet i
sökvägen.

* **Organet** heter `bygg-projekt`, med `hor_till = "bygg"`, så att det
  står under nämnden på kommunens sida som arbetsutskottet. Det står sist i
  kommunfilens organlista, så att ordningen mellan de andra organen
  (ADR-0010) är densamma och mötena hämtas först när de första nätterna
  har hundratals projektfiler att ta in.
* **Källan** är ett nytt fält i Sitevision-källan, `projekt`: organet och
  adressen till listan. Listans bläddringssidor (samma adress med en
  enda parameter vars värde är ett tal från 2) följs, men inte filtren, som
  `robots.txt` stänger. Varje länk en nivå under listan är ett projekt,
  och så är varje länk på en projektsida en nivå under den
  ([#262](https://github.com/moggleif/kommunhandlingar/issues/262)):
  kommunen lägger ibland ett delprojekt, som en detaljplan inom ett större
  projekt, på en egen sida där. Sidor längre ner följs inte; det fanns
  inga 2026-11-14.
* **Typen** är alltid `handlingar`.
* **Datumet** är dagen filen lades upp, i svensk tid, ur tidsstämpeln i
  Sitevisions adress (`/download/18.<nod-id>/<millisekunder>/…`). Den
  finns i båda formerna av fillista. Platsen bestäms en gång (ADR-0003),
  så en ny version av filen, med en ny tidsstämpel, hamnar på samma plats.
* **Namnet** bildas som andra namn (ADR-0003) ur projektsidans sista del i
  adressen och filnamnet utan ändelse:
  `bostader-i-fjaras-planbeskrivning`, och för en sida under ett annat
  projekt ur den sidans sista del:
  `detaljplan-for-kungsbacka-arena-planbeskrivning`. Ett dokument från en projektsida
  har alltid ett namn, som en bilaga.
* **En fil på flera ställen** blir en kandidat (K2): mötessidan går före,
  sedan den första projektsidan i listans ordning, och projektsidan före
  sidan under den.
* **En lista eller projektsida som inte går att hämta eller läsa** står i
  sammanfattningen, och upptäckten fortsätter. Till skillnad från
  mötessidorna stoppar den aldrig upptäckten: ett fel bland projekten ska
  inte hindra mötena, och inget kan placeras fel av att projektens
  kandidater saknas en natt, eftersom deras platser bara kan tas av
  projektens filer.
* Kontaktuppgifterna på projektsidorna läses inte; bara filerna.

### Consequences

* Good, eftersom inget i front matter, datakontrollen eller webbplatsen
  ändras: projektens filer syns direkt på organets sida, under nämnden.
* Good, eftersom projektet står i varje dokuments sökväg och namn, också
  när sidan är borta.
* Bad, eftersom datumet är när filen lades upp, inte när något beslutades.
  Det säger när kommunen publicerade, och det är det som går att belägga.
* Bad, eftersom ett långt projektnamn kan korta bort filnamnet (80 tecken).
  Två filer i samma projekt samma dag får då ett löpnummer efter namnet,
  `<namn>-2`, så att projektet står kvar.
* Bad, eftersom upptäckten varje natt hämtar listan och alla
  projektsidor, cirka 160 sidor med 5 sekunder emellan, ungefär 13 minuter
  av tidsbudgeten. Sidorna under andra projekt var fem 2026-11-14.
* Neutral, eftersom organets sida på webbplatsen räknar varje
  uppläggningsdag som ett sammanträde tills visningen är bestämd.
* Neutral, eftersom bilder och kartor utan text blir `ej-konverterad`
  sida för sida, och filer som inte är PDF (en presentation) registreras
  som `ej-konverterad` med orsaken, som allt annat som inte går att läsa.

### Confirmation

Testerna i `tests/test_sitevision_projekt.py` läser en påhittad lista med
två bläddringssidor och projektsidor i båda formerna av fillista, och
kontrollerar datum, namn, organ, dubbletter och en projektsida som inte
svarar, och att en sida under en projektsida läses men inte sidorna under
den. Den första nattkörningen efter mergen ska visa organet
`bygg-projekt` med kandidater i sammanfattningen.

## Pros and Cons of the Options

### A – Eget organ, uppläggningsdag och projektets namn

* Good, eftersom modellen, front matter och webbplatsen är oförändrade.
* Good, eftersom datumet går att belägga i källan, och platsen behåller
  det också när filen byts ut.
* Bad, eftersom "organ" och "datum" betyder lite annat här än för möten.

### B – En ny nivå i modellen

* Good, eftersom ett projekt är ett projekt och inte ett låtsasmöte.
* Bad, eftersom front matter, datakontrollen, sökvägen, steg 2 och
  webbplatsen måste ändras, och varje dokument i poolen skrivas om för ett
  nytt fält.

### C – Dagen filen först hittades

* Good, eftersom det inte kräver något av adressen.
* Bad, eftersom hela listan får samma datum den första natten, och datumet
  då inte säger något.

### D – Ett organ per projekt

* Bad, eftersom kommunfilen får 146 organ som ändras varje månad, och
  projekten inte är organ.

## More Information

Projektägaren bad 2026-11-12 om alla dokument, också utredningarna, under
byggnadsnämnden "precis som vi har AU under bygg", i nattkörningen, och
att bara läsa in dem nu.

AI-agenten valde A framför B därför att B skulle skriva om hela poolen
för att lägga till ett fält som bara projektens dokument behöver, och
projektet går att bära i namnet. Visningen kan senare bygga på namnen
och sökvägarna, eller på en spårfil som detaljplanerna (ADR-0067), där
fastighetsbeteckningen på projektsidan kopplar ett projekt till en plan.

Organet står sist och inte direkt efter arbetsutskottet, som ADR-0010
annars gör med utskott. Den första fyllningen är cirka 3 GB, mest kartor
och utredningar, och skulle annars ta nätternas tid före
kommunstyrelsens och fullmäktiges nya möten. Ordningen på kommunens sida
följer `hor_till`, inte listan.
