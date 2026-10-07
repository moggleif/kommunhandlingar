---
status: proposed
date: 2026-10-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Kandidaterna hämtas organ för organ i konfigurationens ordning, och inom organet protokoll före handlingar

## Context and Problem Statement

Kungsbackas mötessidor hade 2026-10-07 1 672 filer på 13,2 GB, och
Wayback och diariet (#23, #24) kommer att lägga till mer. En körning har
en tidsbudget på fem timmar (ADR-0006), så poolen fylls natt för natt
([#27](https://github.com/moggleif/kommunhandlingar/issues/27)).

I vilken ordning tas kandidaterna, så att det som ger mest nytta finns i
poolen först? Och var står ordningen, så att en annan kommun kan ha en
annan?

## Decision Drivers

* **Mest nytta per natt.** Poolen ska vara användbar innan den är
  komplett.
* **Användbar betyder hel.** Halva uppgifter om ett organ är svårare att
  bygga på än fullständiga uppgifter om ett organ.
* **Ingen kod "för säkerhets skull"** (AGENTS.md). Ingen
  konfigurationsflagga som inte löser ett verkligt problem.
* **Inget hårdkodat om en kommun** (AGENTS.md). Ordningen mellan organ är
  kommunens, inte kodens.
* **Förutsägbarhet.** Två körningar med samma kandidatlista ska ta dem i
  samma ordning, så att det går att se var nästa natt fortsätter.

### Vad siffrorna säger

Räknat ur de 17 mötessidornas länktexter och JSON-poster 2026-10-07:

| Typ | Filer | Samlat | Median | Störst |
| --- | ---: | ---: | ---: | ---: |
| Protokoll | 660 | 0,26 GB | 0,3 MB | 5,6 MB |
| Kallelser | 505 | 0,09 GB | 0,2 MB | 0,9 MB |
| Handlingar | 493 | 12,8 GB | 6,7 MB | 308,8 MB |
| Övrigt | 14 | 0,02 GB | 0,6 MB | 3,7 MB |

Protokollen och kallelserna är 70 procent av filerna men under 3 procent
av storleken. Handlingarna är resten, och tre organ bär tre fjärdedelar av
dem: kommunstyrelsen 4,1 GB, dess arbetsutskott 4,0 GB och fullmäktige
1,7 GB. 34 av de 36 filerna över 100 MB finns hos just dem. De tolv
övriga organen är tillsammans 2,1 GB.

## Considered Options

* A – Organ för organ i konfigurationens ordning; inom organet protokoll,
  kallelser, övrigt, handlingar, äldst först
* B – Som A, men ordningen står i ett eget prioritetsfält per organ
* C – Typ före organ: alla protokoll och kallelser för alla organ först,
  sedan alla handlingar
* D – Minsta filen först
* E – Ingen bestämd ordning: kandidaterna tas som upptäckten hittade dem

## Decision Outcome

Valt alternativ: "A – Organ för organ i konfigurationens ordning; inom
organet protokoll, kallelser, övrigt, handlingar, äldst först", eftersom
ett helt organ är användbart och ett halvt inte är det, och eftersom
listans ordning räcker som prioritering utan nytt fält.

Beslutet i korthet. Beteendet står i K13 och var ordningen läses i
[03-ARKITEKTUR.md](../03-ARKITEKTUR.md).

* **Ordningen mellan organ är `[[organ]]`-listans ordning** i
  `kommuner/<kommun>.toml` (ADR-0008). Inget nytt fält: listan är redan
  ordnad, och en annan kommun ordnar sin lista som den vill.
* **Ordningen inom ett organ står i koden**, eftersom den inte handlar om
  någon särskild kommun: protokollet först (det bär besluten och är
  litet), sedan kallelsen, sedan övriga dokument, sist handlingarna.
* **Äldst först inom varje typ.** Det nyaste ligger kvar på kommunens
  sidor; det äldsta är det som kan försvinna när ett år plockas bort
  (#24).
* **För Kungsbacka** blir listans ordning: Gymnasium & Arbetsmarknad,
  Förskola & Grundskola med sitt arbetsutskott, Byggnadsnämnden med sitt
  arbetsutskott, Teknik med sitt arbetsutskott, Service, Individ &
  Familjeomsorg, Kultur & Fritid, Miljö & Hälsoskydd, Vård & Omsorg,
  Valnämnden, Kommunrevisionen, och sist kommunstyrelsen, dess
  arbetsutskott och kommunfullmäktige. Den skrivs in i
  `kommuner/kungsbacka.toml` när filen skapas
  ([#25](https://github.com/moggleif/kommunhandlingar/issues/25)).
* **Ingen särskild regel för stora filer.** ADR-0006 lägger redan ett
  dokument som inte hinner åt sidan, och mätningen nedan visar att en fil
  på 308,8 MB är långt under en natts budget.

### Consequences

* Bra, eftersom varje organ blir helt innan nästa börjar: den som vill
  följa en nämnd kan göra det innan poolen är komplett.
* Bra, eftersom de elva mindre organen tillsammans är 2,1 GB och alltså
  kan bli färdiga på några nätter, medan de tre stora tar flest.
* Bra, eftersom ordningen inte kostar någon kod utöver en sortering, och
  inget nytt konfigurationsfält.
* Bra, eftersom ordningen är förutsägbar: den beror bara på
  konfigurationen och kandidaternas egna uppgifter.
* Dåligt, eftersom besluten i kommunstyrelsen och fullmäktige – de organ
  som rör hela kommunen – kommer sist, trots att deras protokoll
  tillsammans är under 50 MB. Det är avsiktligt valt av ägaren: hellre
  hela organ i tur och ordning än alla protokoll först.
* Dåligt, eftersom ett organ vars handlingar är stora kan hålla på en
  körning i flera nätter utan att något annat organ rör sig.
* Neutralt, eftersom ordningen bara avgör *när* ett dokument tas in. Allt
  tas in till slut, och K8 gör att en avbruten körning fortsätter där den
  var.

### Confirmation

När koden som sorterar kandidaterna skrivs (#25) testas den mot en
kandidatlista i `tests/fixtures/`: organen kommer i konfigurationens
ordning, typerna i sin ordning inom varje organ, det äldsta
sammanträdet först, och samma lista i en annan upptäcktsordning ger samma
resultat.

## Pros and Cons of the Options

### A – Organ för organ i konfigurationens ordning

* Bra, eftersom ett helt organ går att bygga analyser på.
* Bra, eftersom prioriteringen inte kräver något nytt fält.
* Bra, eftersom ordningen syns direkt i kommunfilen, där den som lägger
  till en kommun redan arbetar.
* Neutralt, eftersom ordningen inom organet ligger i koden. Den handlar
  inte om någon särskild kommun, så den bryter inte mot "inget hårdkodat
  om en kommun".
* Dåligt, eftersom det är lätt att flytta en rad i kommunfilen utan att
  mena att prioriteringen ändras.
* Dåligt, eftersom de tyngsta organen är de som rör hela kommunen, och de
  kommer sist.

### B – Ett eget prioritetsfält per organ

* Bra, eftersom avsikten står uttryckligen och inte går att ändra av
  misstag.
* Dåligt, eftersom det är en konfigurationsflagga utan ett andra fall som
  behöver den: listan är redan ordnad (AGENTS.md, ingen abstraktion före
  två konkreta fall).
* Dåligt, eftersom två organ kan få samma prioritet, och då behövs en
  regel för vad som händer då.

### C – Typ före organ

* Bra, eftersom alla besluten – 660 protokoll på 0,26 GB – skulle kunna
  finnas i poolen efter en natt.
* Bra, eftersom underlaget till ett beslut är intressant först när man vet
  vilket beslut det ledde till.
* Dåligt, eftersom inget organ är helt förrän nästan allt är hämtat: ett
  protokoll utan sina handlingar går inte att följa till källan för ett
  tal.
* Dåligt, eftersom ordningen inte syns i kommunfilen och därmed inte går
  att ändra per kommun utan ett nytt fält.

### D – Minsta filen först

* Bra, eftersom antalet dokument i poolen växer snabbast möjligt.
* Dåligt, eftersom resultatet blir strimlat: lite av varje organ och
  varje år, inget helt.
* Dåligt, eftersom storleken bara är känd för de källor som anger den.
  Wayback-adaptern gör det inte nödvändigtvis, och då går ordningen inte
  att räkna ut före hämtningen.

### E – Ingen bestämd ordning

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
| Hämtning | MÄTNING_HAMTNING |
| Sidor | MÄTNING_SIDOR |
| Textlager med pdfplumber | MÄTNING_TEXT |
| Sidor utan textlager | MÄTNING_UTAN |

MÄTNING_SLUTSATS

Storleken i megabyte säger alltså lite om tiden: det är antalet sidor,
och särskilt antalet inskannade sidor, som kostar. ADR-0006 har redan en
regel för ett dokument som inte hinner bli klart, och tills ett dokument
som faktiskt spränger budgeten dyker upp behövs ingen regel till.

### Diskussionen

1. **Agentens första rekommendation var alternativ C**, typ före organ:
   protokollen och kallelserna för alla organ på en natt, handlingarna
   sedan. Argumentet var siffrorna – 70 procent av filerna för 3 procent
   av storleken – och att protokollen är det som bär besluten.
2. **Ägaren valde organ för organ** och satte ordningen: Gymnasium &
   Arbetsmarknad, Förskola & Grundskola, Byggnadsnämnden, Teknik,
   Service, övriga nämnder, och sist kommunstyrelsen, dess arbetsutskott
   och fullmäktige. Inom ett organ fick agentens rekommendation gälla.
3. **Det som avgjorde:** ett helt organ är användbart och ett halvt är det
   inte. Ett protokoll utan sina handlingar går inte att följa till
   källan, och poängen med poolen är just att ett tal ska gå att spåra.
   De tre tyngsta organen sist betyder också att de tolv lätta hinner bli
   färdiga först – 2,1 GB mot 9,8 GB.
4. **Agentens invändning mot sig själv, om arbetsutskotten:** ägaren
   nämnde inte arbetsutskotten utom kommunstyrelsens. Varje arbetsutskott
   ligger direkt efter sin nämnd, eftersom de bereder samma ärenden och
   läses tillsammans. Det är en tolkning och inte ett eget beslut; det
   ändras genom att flytta en rad i kommunfilen.
5. **Att samma ärende troligen går igen** i arbetsutskottets,
   kommunstyrelsens och fullmäktiges handlingar är inte kontrollerat. Det
   skulle förklara varför just de tre är så stora, och det skulle betyda
   att ordningen ovan hämtar hela kommunens ärenden sist. Kontrollen
   kräver att handlingarna är konverterade och är därmed något för senare.
6. **Prioritetsfältet (B) avvisades** som kod före behov. Blir det en gång
   fel att listans ordning också är prioriteringen, till exempel när en
   kommun vill ha organen i en läsbar ordning i filen men hämta i en
   annan, är det två konkreta fall och fältet kan läggas till då.

### När beslutet bör omprövas

* När en kommun vill ha organen i en annan ordning i filen än i
  hämtningen (då blir B aktuellt).
* När ett dokument visar sig ta mer än en natts budget.
* När Wayback och diariet (#23, #24) ger kandidater vars organ eller typ
  inte går att veta före hämtningen.
