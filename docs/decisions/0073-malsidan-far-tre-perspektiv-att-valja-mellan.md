---
status: accepted
date: 2026-11-15
decision-makers: projektägaren
consulted: AI-agenten
---

# Målsidan får tre perspektiv att välja mellan – tidslinje, ett år i taget och målkort – och valet står i adressen

## Context and Problem Statement

Målsidan (K29, [ADR-0050](0050-malsidan-visas-som-tidslinje-och-malkort.md))
valdes ur tre skisser: A tidslinje, B ett år i taget och C målkort. Sidan
fick A och C under varandra, och B lämnades. Projektägaren vill nu ha alla
tre och låta den som läser välja perspektiv för stunden
([#271](https://github.com/moggleif/kommunhandlingar/issues/271)). B svarar
på en fråga som de andra två inte gör: vad ville nämnden ett visst år, och
vad ändrades från året innan? Hur ska tre perspektiv rymmas på samma sida?

## Decision Drivers

* **Ett perspektiv i taget.** Tre vyer under varandra gör en lång sida
  längre.
* **Länkbart.** Ett perspektiv och ett år ska gå att skicka till någon.
* **Tomt är inte noll.** En lucka i poolen får inte se ut som ett år utan
  mål, och efter en lucka går det inte att säga vad som är nytt.
* **Sidan fungerar utan skript**, och inga nya beroenden.
* **Samma urval överallt**, så att valet av till exempel direktiv inte
  försvinner när perspektivet byts.

## Considered Options

* Tre perspektiv på samma sida med en väljare, valet i adressens
  frågesträng
* Tre sidor, en per perspektiv, som flikar
* Tre perspektiv på samma sida, valet i adressens fragment (`#ar-2025`)
* Allt under varandra som i dag, med B tillagt sist

## Decision Outcome

Valt: tre perspektiv på samma sida med en väljare, valet i frågesträngen.

* **Väljaren** står under sammandraget och urvalet: Tidslinje, Ett år i
  taget och Målkort. Utan val visas tidslinjen (projektägarens val).
  Sammandraget och urvalet är gemensamma och gäller alla tre.
* **Adressen** är `?vy=tidslinje`, `?vy=ar&ar=2025` eller `?vy=kort`.
  Varje val läggs i webbläsarens historik, så bakåt och framåt fungerar.
  Fragmentet behålls för det det redan används till: `#mal-3` pekar på ett
  kort, och en sådan adress visar målkorten.
* **Ett mål som väljs i tidslinjen** byter till målkorten och öppnar
  kortets historik, som tidigare.
* **Ett år i taget** har en knapp per år från målens första till sista år;
  utan val är det senaste året valt (projektägarens val). Året visar
  årets antal (samma ruta som sammandragets), ett kort per mål med årets
  rubrik, formulering, status och källa, märkt "nytt" när spåret inte
  fanns året innan, de spår som fanns året innan men inte i år, och
  protokollens uppföljningar och dragningar det året. Ett spår är samma mål
  också när det bytt rubrik. En lucka i poolen och ett år utan mål sägs
  med ord, och efter en lucka jämförs inte med året innan.
* **Utan skript** står alla tre efter varandra och Ett år i taget som ett
  avsnitt per år, nyast först, ungefär som sidan såg ut före K29.

### Consequences

* Good, eftersom varje fråga har sitt perspektiv: målens livslängd,
  ett års mål och ett måls historik.
* Good, eftersom ett perspektiv och ett år går att länka till.
* Good, eftersom B räknas ur samma filer som A och C och inga nya data
  behövs.
* Bad, eftersom sidan blir större: Ett år i taget upprepar årets rader ur
  korten, och utan skript blir sidan mycket lång.
* Bad, eftersom ett skript till får ett tillstånd att hålla i takt med
  adressen.

### Confirmation

`tests/test_malar.py` prövar Ett år i taget med en påhittad kommun: nytt,
försvann, luckan, år utan mål och protokollen, och att perspektiven,
väljarna och skriptet `perspektiv.js` står på sidan. Skriptet prövas för
hand i en webbläsare: perspektiven, åren, urvalet i alla tre, adressen,
bakåt och framåt, och ett mål valt i tidslinjen.

## Pros and Cons of the Options

### Tre perspektiv på samma sida, valet i frågesträngen

* Good, eftersom urvalet och sammandraget delas och bara byggs en gång.
* Good, eftersom frågesträngen är fri, medan fragmentet redan pekar på
  korten.
* Bad, eftersom valet bara fungerar med skript; utan står allt.

### Tre sidor som flikar

* Good, eftersom varje sida är kort och fungerar utan skript.
* Bad, eftersom urvalet inte följer med mellan sidorna utan ett skript
  som för det i adressen ändå.
* Bad, eftersom organets flikar (K39) redan är en rad med sidor; tre till
  per målsida blir flikar i flikar.

### Valet i fragmentet

* Good, eftersom ett fragment inte laddar om sidan.
* Bad, eftersom fragmentet redan pekar på ett kort (`#mal-3`), och ett år
  och ett kort kan inte stå i samma fragment utan en egen syntax.

### Allt under varandra med B sist

* Good, eftersom inget skript behövs.
* Bad, eftersom sidan blir mycket lång, och det är just det väljaren ska
  lösa.

## More Information

Projektägaren såg de tre skisserna igen 2026-11-14, gillade alla tre och
bad att de skulle finnas samtidigt med ett val för stunden. AI-agenten
föreslog i fas 0 tidslinjen som förval, det senaste året först i Ett år i
taget och att valet ska stå i adressen, och projektägaren sa ja till alla
tre. Frågesträngen valdes framför fragmentet eftersom `#mal-N` redan är
länkarna från tidslinjen till korten och ska fortsätta fungera utan
skript. Flikar som egna sidor avvisades för att urvalet då inte följer med
och för att organets sidor redan har en flikrad. Ett år i taget räknar ett
mål som nytt per spår, inte per rubrik: ett mål som bytt rubrik är samma
mål med ny rubrik, och kortet visar den rubrik målet hade det året.
