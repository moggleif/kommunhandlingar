---
status: proposed
date: 2026-11-15
decision-makers: projektägaren
consulted: AI-agenten
---

# Sammanträdet visas punkt för punkt ur kallelsens dagordning, med handlingens sidor, beslutet och historiken räknade fram vid bygget

## Context and Problem Statement

Organets sida listar varje sammanträde med dess dokument. Den som vill
veta vad kommunstyrelsen behandlar får läsa en kallelse, hundratals sidor
handlingar och ett protokoll, och själv leta upp vad samma ärende har
varit med om tidigare i andra organ
([#277](https://github.com/moggleif/kommunhandlingar/issues/277)).
Projektägaren vill ha en sida per sammanträde: dokumenten överst, sedan
punkt för punkt med handlingen och protokollet i sammanfattad form och
historiken. Hur byggs den, och var kommer varje del ifrån?

## Decision Drivers

* **Återge, skriv inget eget.** Sammanfattningen ska vara källans ord.
* **Hellre märka än gissa.** En punkt vars handling eller beslut inte
  hittas säger det.
* **Poolen är tillståndet** (ADR-0004, ADR-0071). Det som går att räkna
  fram ur texten lagras inte en gång till.
* **Inget hårdkodat om en kommun.** Vilka organ som får sidan står i
  kommunfilen.
* **Pröva formen i liten skala först.** Projektägaren vill se
  kommunstyrelsen 2026 på riktigt innan resten byggs (#283).

## Considered Options

* A – Dagordningen ur kallelsens tabell, handlingen delad där punktens
  diarienummer står, beslutet och historiken ur paragraferna, allt vid
  bygget
* B – Dagordningen ur protokollets paragrafer
* C – En CSV per sammanträde med punkterna, skriven av AI-agenten
* D – Sammanfattningar skrivna av en språkmodell vid bygget

## Decision Outcome

Valt: A, eftersom kallelsen finns innan sammanträdet, har förslaget till
beslut och diarienumret i samma tabell, och allt annat går att nå med
diarienumret utan att något lagras.

* **Dagordningen** är kallelsens tabellrader som börjar med punktens
  nummer. Rubriken slutar före raden med tidpunkten för en föredragning,
  så att föredragandenas namn inte står i rubriken.
* **Diarienumret** i kallelsen saknar organets förled. Punktens nummer är
  det i handlingen eller protokollet som slutar med kallelsens nummer,
  så att historiken inte blandar ihop `KS-2026-00543` med ett
  `GA-2026-00543`.
* **Handlingen** delas efter dagordningen: handlingarna följer
  dagordningens ordning, och varje punkt börjar på sidan där dess
  diarienummer står efter `Dnr` eller `Diarienummer`, i arbetsutskottets
  protokollsutdrag eller i tjänsteskrivelsen.
* **Sammanfattningen** är tjänsteskrivelsens avsnitt "Sammanfattning av
  ärendet", som det står.
* **Beslutet** är paragrafen i sammanträdets protokoll med punktens
  diarienummer (ADR-0071).
* **Historiken** är paragraferna i alla organ med punktens diarienummer
  eller ett diarienummer som står i handlingen, så att en nämnds eget
  beslut i ett remissvar kommer med, och korten över tid vars steg står i
  en sådan paragraf.
* **Vilka sammanträden** står i kommunfilen, `sammantradessidor` på
  organet, med första året. Kungsbacka har `ks` från 2026.

### Consequences

* Good, eftersom punkten visar förslaget, beslutet och vad ärendet varit
  med om i alla organ på ett ställe, med länkar till sidorna i poolen.
* Good, eftersom inget nytt lagras och nattkörningen inte ändras.
* Good, eftersom en kommande punkt syns så fort kallelsen finns, och
  beslutet kommer till när protokollet finns.
* Bad, eftersom delningen bygger på att handlingarna följer dagordningen
  och att diarienumret står på punktens första sida. För kommunstyrelsen
  2026 hittas handlingen för omkring sju av tio punkter; de flesta andra
  är informationspunkter utan egen handling.
* Bad, eftersom en punkt som konverteringen inte läste som tabellrad
  (till exempel budgeten 2026-10-20, punkt 35) saknar förslaget.
* Bad, eftersom en sammanfattning som fortsätter på nästa sida slutar vid
  sidans slut. Länken till handlingen står alltid bredvid.
* Bad, eftersom en sida i ett protokoll kan ha flera paragrafer, så att
  ett kort över tid kan kopplas till en punkt det inte gäller. Den
  kopplingen märks `tolkad`.
* Neutral, eftersom rubrikerna som avslutar sammanfattningen
  (Beskrivning av ärendet, Beslutsunderlag, …) är svenska
  tjänsteskrivelsers, inte Kungsbackas.

### Confirmation

`tests/test_dagordning.py`, `tests/test_punktsidor.py` och
`tests/test_sammantradessida.py` prövar delarna på påhittade kallelser,
handlingar och paragrafer. Kommunstyrelsens sammanträden 2026 gås igenom
för hand på den byggda webbplatsen innan PR:en.

## Pros and Cons of the Options

### A – Kallelsens tabell, handlingen delad efter diarienumret, vid bygget

* Good, eftersom kallelsen finns före sammanträdet och har förslaget.
* Good, eftersom allt annat redan finns i poolen och i paragraferna.
* Bad, eftersom delningen av handlingarna kan missa en punkt.

### B – Dagordningen ur protokollets paragrafer

* Good, eftersom paragraferna redan finns (ADR-0071).
* Bad, eftersom protokollet kommer en till tre veckor efter
  sammanträdet, så att ett kommande sammanträde inte får någon sida.
* Bad, eftersom paragrafen har beslutet men inte förslaget.

### C – En CSV per sammanträde skriven av AI-agenten

* Good, eftersom varje punkt kan kontrolleras för hand.
* Bad, eftersom samma uppgifter då står två gånger och kan glida isär.
* Bad, eftersom varje sammanträde kräver en ny omgång arbete.

### D – Sammanfattningar skrivna av en språkmodell

* Good, eftersom varje punkt skulle få en kort sammanfattning, också de
  utan tjänsteskrivelse.
* Bad, eftersom texten då inte är källans, och poolen återger, den drar
  inga slutsatser.
* Bad, eftersom bygget skulle behöva en tjänst utanför repot.

## More Information

Projektägaren beskrev först en sida som öppnas från kalendern, där varje
punkt är ett ärende som på sidorna över tid. Agenten föreslog i fas 0 att
sidan hör till organets sidor, eftersom de redan har sammanträdena och
dokumenten, och projektägaren landade i en sammanträdessida som ersätter
listan med dokument: en rad per dokument överst, sedan punkt för punkt
"i summeringsform". Agenten tolkade summeringsformen som utdrag i
källans egna ord – förslaget, tjänsteskrivelsens sammanfattning och
beslutet – och inte text som webbplatsen skriver, vilket avgjorde mot D.

Ett utkast för kommunstyrelsen 2026-10-20 visades som skärmdump innan
något byggdes. Projektägaren godkände formen och bad att bara
kommunstyrelsen 2026 byggs nu, så att formen kan justeras på riktigt;
resten står i #283. Därför står första året i kommunfilen i stället för
att alla år och organ får sidan på en gång.

Diarienumrens förled diskuterades: kallelsen skriver `2026-00543` och
protokollet `KS-2026-00543`. Att matcha bara på numret efter förledet
hade blandat organen, eftersom varje nämnd har en egen nummerserie. Att
läsa förledet ur kommunfilen hade krävt ett nytt fält. Agenten valde att
ta förledet från handlingen eller protokollet, där numret står helt.

En sida i ett protokoll har ofta flera korta paragrafer. Ett steg i ett
kort över tid pekar på en sida, inte en paragraf, så kopplingen kan bli
fel; den märks `tolkad` när sidan har paragrafer med andra diarienummer,
i stället för att utelämnas.

Samma sida för kommande eller senaste sammanträde på systerprojektets
webbplats följs i ett eget issue där.
