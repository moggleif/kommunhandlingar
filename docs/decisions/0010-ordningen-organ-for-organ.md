---
status: proposed
date: 2026-10-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Kandidaterna hämtas organ för organ i konfigurationens ordning, och inom organet protokoll före handlingar

## Context and Problem Statement

Kungsbackas 17 mötessidor hade 2026-10-07 1 672 filer på 13,2 GB (en
fil mer än när källan kartlades samma dag), och Wayback och diariet (#23,
#24) kommer att lägga till mer. En körning har en tidsbudget på fem
timmar (ADR-0006), så poolen fylls natt för natt
([#27](https://github.com/moggleif/kommunhandlingar/issues/27)).

I vilken ordning tas kandidaterna, så att det som ger mest nytta finns i
poolen först? Och var står ordningen, så att en annan kommun kan ha en
annan?

## Decision Drivers

* **Mest nytta per natt.** Poolen ska vara användbar innan den är
  komplett.
* **Användbar betyder hel.** Fullständiga uppgifter om ett organ går att
  bygga på; lite om varje organ gör det inte.
* **Ingen kod "för säkerhets skull"** (AGENTS.md). Ingen
  konfigurationsflagga som inte löser ett verkligt problem.
* **Inget hårdkodat om en kommun** (AGENTS.md). Ordningen mellan organ är
  kommunens, inte kodens.
* **Förutsägbarhet.** Samma kandidatlista ska alltid tas i samma ordning,
  så att det går att se var nästa natt fortsätter.

### Vad siffrorna säger

Räknat ur de 17 mötessidornas länktexter och JSON-poster 2026-10-07, per
typ:

| Typ | Filer | Samlat | Median | Störst |
| --- | ---: | ---: | ---: | ---: |
| Protokoll | 660 | 0,26 GB | 0,3 MB | 5,6 MB |
| Kallelser | 505 | 0,09 GB | 0,2 MB | 0,9 MB |
| Handlingar | 493 | 12,8 GB | 6,65 MB | 308,8 MB |
| Annat | 14 | 0,02 GB | 0,6 MB | 3,7 MB |

"Annat" är kommunbudget, årsredovisning, delårsrapport, nämndbudget,
avfallsföreskrifter, ett enskilt ärende och några protokollsparagrafer
utan typ i filnamnet. Vilka av dem som blir kandidater, och med vilken
typ, avgörs när adaptern skrivs (#25).

Storlekarna är som kommunen anger dem, och 1 GB räknas här som 1 000 MB.

Per organ, i den ordning som beslutas nedan:

| Organ | Filer | Samlat |
| --- | ---: | ---: |
| Gymnasium & Arbetsmarknad | 98 | 314 MB |
| Förskola & Grundskola | 94 | 267 MB |
| Förskola & Grundskolas arbetsutskott | 92 | 222 MB |
| Byggnadsnämnden | 107 | 217 MB |
| Byggnadsnämndens arbetsutskott | 123 | 220 MB |
| Teknik | 103 | 660 MB |
| Tekniks arbetsutskott | 72 | 282 MB |
| Service | 90 | 137 MB |
| Individ & Familjeomsorg | 83 | 156 MB |
| Kultur & Fritid | 90 | 319 MB |
| Miljö & Hälsoskydd | 104 | 86 MB |
| Vård & Omsorg | 101 | 311 MB |
| Valnämnden | 39 | 46 MB |
| Kommunrevisionen | 63 | 12 MB |
| Kommunstyrelsen | 92 | 4 096 MB |
| Kommunstyrelsens arbetsutskott | 238 | 4 073 MB |
| Kommunfullmäktige | 83 | 1 751 MB |

Protokollen och kallelserna är 70 procent av filerna men under 3 procent
av storleken. De tre sista organen är 9,9 GB av 13,2; de 14 första är
tillsammans 3,2 GB. 34 av de 36 filerna över 100 MB finns hos de tre
sista.

**Grov tidsuppskattning.** Mätningen nedan gav ungefär 18 minuter för
309 MB, hämtning och konvertering. Räknat på samma sätt per megabyte blir
de 14 första organen ungefär 3 timmar, alltså en natt, och de tre sista
ungefär 10 timmar, två till tre nätter. Uppskattningen är grov: tiden
följer antalet sidor och inskannade sidor, inte megabyten.

## Considered Options

* A – Organ för organ i konfigurationens ordning; inom organet typ för
  typ, äldst först
* B – Som A, men ordningen står i ett eget prioritetsfält per organ
* C – Typ före organ: alla protokoll och kallelser för alla organ först,
  sedan alla handlingar
* D – Organ för organ, och inom organet möte för möte
* E – Minsta filen först
* F – Ingen bestämd ordning: kandidaterna tas som upptäckten hittade dem

## Decision Outcome

Valt alternativ: "A – Organ för organ i konfigurationens ordning; inom
organet typ för typ, äldst först", eftersom ett helt organ är användbart
och lite om varje organ inte är det, och eftersom listans ordning räcker
som prioritering utan nytt fält.

Beslutet i korthet. Beteendet står i K13 och var ordningen läses i
[03-ARKITEKTUR.md](../03-ARKITEKTUR.md).

* **Ordningen mellan organ är `[[organ]]`-listans ordning** i
  `kommuner/<kommun>.toml` (ADR-0008). Inget nytt fält: listan är redan
  ordnad, och en annan kommun ordnar sin lista som den vill. Ett
  föregångarorgan är ett eget `[[organ]]` och tas där det står i listan.
* **Ordningen inom ett organ står i koden**, eftersom den inte handlar om
  någon särskild kommun: protokoll, kallelse, bilaga, handlingar. Inom en
  typ tas det äldsta sammanträdet först, och lika värden skiljs åt med
  källnyckeln.
* **För Kungsbacka** är ordningen den i tabellen ovan. Den skrivs in i
  `kommuner/kungsbacka.toml` när filen skapas
  ([#25](https://github.com/moggleif/kommunhandlingar/issues/25)).
* **Ingen särskild regel för stora filer.** Den största filen tar ungefär
  18 minuter av fem timmar (mätningen nedan).

### Consequences

* Bra, eftersom varje organ blir helt innan nästa börjar, och de 14 första
  organen bör bli klara redan första natten.
* Bra, eftersom ordningen inte kostar någon kod utöver en sortering, och
  inget nytt konfigurationsfält.
* Bra, eftersom ordningen är förutsägbar: den beror bara på
  konfigurationen och kandidaternas egna uppgifter.
* Dåligt, eftersom besluten i kommunstyrelsen och fullmäktige – de organ
  som rör hela kommunen – kommer sist, trots att deras protokoll
  tillsammans är under 50 MB. Det är ägarens val: hela organ i tur och
  ordning, de tunga sist.
* Dåligt, eftersom de tre tunga organen under två till tre nätter har
  sina protokoll men inte alla sina handlingar – just det läge som
  alternativ C avvisades för. Det är en avvägning: det gäller bara de tre
  sista organen och bara tills deras handlingar är hämtade, och under
  tiden finns åtminstone alla deras beslut.
* Dåligt, eftersom ny historik för ett tidigt organ, till exempel från
  Wayback eller diariet, tas före nya dokument från ett senare organ. Ett
  nytt protokoll från fullmäktige kan då vänta flera nätter medan äldre
  handlingar hämtas.
* Dåligt, eftersom ett dokument som ensamt tar mer än budgetens hårda
  gräns läggs åt sidan (ADR-0006), tas först nästa natt igen och läggs åt
  sidan igen. Med en fast ordning stoppar det allt som kommer efter det.
  Med ADR-0005:s takt krävs ett inskannat dokument på över 6 000 sidor för
  det, mot 1 716 sidor i den största filen hittills. Händer det behövs en
  regel.
* Neutralt, eftersom ordningen bara avgör *när* ett dokument tas in. Allt
  tas in till slut, och K8 gör att en avbruten körning fortsätter där den
  var.

### Confirmation

När koden som sorterar kandidaterna skrivs (#25) testas den mot en
kandidatlista i `tests/fixtures/`: organen kommer i konfigurationens
ordning, typerna i sin ordning inom varje organ, det äldsta
sammanträdet först, lika värden i källnyckelns ordning, och samma lista i
en annan upptäcktsordning ger samma resultat.

## Pros and Cons of the Options

### A – Organ för organ, inom organet typ för typ

* Bra, eftersom ett helt organ går att bygga analyser på.
* Bra, eftersom prioriteringen inte kräver något nytt fält.
* Bra, eftersom ordningen syns direkt i kommunfilen, där den som lägger
  till en kommun redan arbetar.
* Bra, eftersom ett tungt organ får alla sina beslut i poolen innan
  handlingarna börjar, som tar längst.
* Neutralt, eftersom ordningen inom organet ligger i koden. Den handlar
  inte om någon särskild kommun, så den bryter inte mot "inget hårdkodat
  om en kommun".
* Dåligt, eftersom det är lätt att flytta en rad i kommunfilen utan att
  mena att prioriteringen ändras.

### B – Ett eget prioritetsfält per organ

* Bra, eftersom avsikten står uttryckligen och inte går att ändra av
  misstag.
* Dåligt, eftersom det är en konfigurationsflagga utan ett andra fall som
  behöver den: listan är redan ordnad. ADR-0008 strök ett prioritetsfält
  av samma skäl.
* Dåligt, eftersom två organ kan få samma prioritet, och då behövs en
  regel för vad som händer då.

### C – Typ före organ

* Bra, eftersom alla besluten – 660 protokoll på 0,26 GB – skulle kunna
  finnas i poolen efter en natt.
* Dåligt, eftersom inget organ är helt förrän nästan allt är hämtat: ett
  protokoll utan sina handlingar går inte att följa till källan för ett
  tal.
* Dåligt, eftersom ordningen inte syns i kommunfilen och därmed inte går
  att ändra per kommun utan ett nytt fält.

### D – Organ för organ, inom organet möte för möte

* Bra, eftersom varje möte blir helt, med protokoll och handlingar, innan
  nästa börjar.
* Dåligt, eftersom ett tungt organ som kommunstyrelsen, med 4,1 GB, under
  flera nätter bara har sina äldsta möten i poolen, och inga av de nyare
  besluten.
* Neutralt, eftersom ett lätt organ blir klart samma natt med båda
  ordningarna.

### E – Minsta filen först

* Bra, eftersom antalet dokument i poolen växer snabbast möjligt.
* Dåligt, eftersom resultatet blir strimlat: lite av varje organ och
  varje år, inget helt.
* Dåligt, eftersom storleken bara är känd för de källor som anger den, och
  då går ordningen inte alltid att räkna ut före hämtningen.

### F – Ingen bestämd ordning

* Bra, eftersom det inte kräver någon kod.
* Dåligt, eftersom det inte går att se var nästa natt fortsätter, och två
  körningar kan ta kandidaterna i olika ordning.
* Dåligt, eftersom nyttan av de första nätterna blir slumpens verk.

## More Information

### Mätningen av den största filen

Frågan som avgjorde om stora filer behöver en egen regel var om en enda
fil kan ta mer än en natts budget. Den största filen på sidorna,
"Kommunstyrelsen handlingar 2025-04-22.pdf" på 308,8 MB
(`18.6d76bb7f1963d5107e616b38`), mättes 2026-10-07 med samma verktyg som
ADR-0005 valde:

| Mått | Värde |
| --- | --- |
| Hämtning | 4 min 31 s (323 783 886 byte) |
| Sidor | 1 716 |
| Textlager med pdfplumber | 452 s för alla sidor, 0,26 s per sida |
| Sidor utan textlager | 124, som med ADR-0005:s 3 s per inskannad sida blir ungefär 6 min OCR |

Hämtning, textlager och OCR blir tillsammans ungefär 18 minuter, mot en
budget på 5 timmar. Tabellerna är inte medräknade: filen har 685 761
ritade linjer, och hur lång tid det tar att läsa tabeller ur dem är inte
mätt. Mätningen gjordes i en molnsession, inte i Actions. En annan fil kan
ha fler inskannade sidor; ett helt inskannat dokument på 1 716 sidor
skulle med samma takt ta omkring 1,5 timme.

Storleken i megabyte säger alltså lite om tiden: det är antalet sidor,
och särskilt antalet inskannade sidor, som kostar. ADR-0006 nämner att
den största PDF:en som setts hade 228 sidor; den här har 1 716, och
slutsatsen där – att ett dokument som ensamt spränger budgeten måste vara
inskannat och på flera tusen sidor – står sig.

### Diskussionen

1. **Agentens första rekommendation var alternativ C**, typ före organ:
   protokollen och kallelserna för alla organ på en natt, handlingarna
   sedan. Argumentet var siffrorna – 70 procent av filerna för 3 procent
   av storleken – och att protokollen är det som bär besluten.
2. **Ägaren valde organ för organ** och satte ordningen: Gymnasium &
   Arbetsmarknad, Förskola & Grundskola, Byggnadsnämnden, Teknik,
   Service, övriga nämnder, och sist kommunstyrelsen, dess arbetsutskott
   och fullmäktige. Ordningen inom ett organ lämnades åt agenten.
3. **Det som avgjorde:** ett helt organ är användbart, och lite om varje
   organ är det inte. Ett protokoll utan sina handlingar går inte att
   följa till källan, och poängen med poolen är att ett tal ska gå att
   spåra. De tre tyngsta sist betyder också att de 14 lätta – 3,2 GB mot
   9,9 – blir färdiga först.
4. **Ordningen inom organet (A mot D) är agentens.** Det avgörande gäller
   mellan organ. Inom ett lätt organ spelar ordningen ingen roll, eftersom
   det blir klart samma natt. Inom ett tungt ger protokollen först alla
   organets beslut innan handlingarna, som tar flera nätter; möte för
   möte skulle under de nätterna bara ge de äldsta mötena.
5. **Agentens tolkningar av ägarens ordning,** som ändras genom att
   flytta en rad i kommunfilen:
   * Varje arbetsutskott ligger direkt efter sin nämnd, eftersom de
     bereder samma ärenden. Ägaren nämnde bara kommunstyrelsens.
   * "Övriga nämnder" tas i den ordning sidorna står i källbeskrivningen,
     med Valnämnden och Kommunrevisionen, som inte är facknämnder, sist.
6. **Att samma ärende troligen går igen** i arbetsutskottets,
   kommunstyrelsens och fullmäktiges handlingar är inte kontrollerat. Det
   skulle förklara varför just de tre är så stora. Kontrollen kräver att
   handlingarna är konverterade och är därmed något för senare.
7. **Äldst först** valdes för att det äldsta är det som kan försvinna när
   ett år plockas bort från sidorna (#24). Ägarens ordning gör att
   kommunstyrelsens och fullmäktiges äldsta år ändå kommer sist av allt.
   Med tre till fyra nätter för allt är risken liten.
8. **Prioritetsfältet (B) avvisades** som kod före behov. Blir det en gång
   fel att listans ordning också är prioriteringen, är det två konkreta
   fall och fältet kan läggas till då.

### När beslutet bör omprövas

* När en kommun vill ha organen i en annan ordning i filen än i
  hämtningen (då blir B aktuellt).
* När ett dokument visar sig ta mer än en natts budget.
* När tiden för att läsa tabellerna är mätt, eftersom den inte ingår i
  tidsuppskattningen ovan.
* När körningen flyttas till en egen server (#18), som ändrar budgeten.
* När ny historik (#23, #24) får nya dokument för senare organ att vänta
  märkbart.
