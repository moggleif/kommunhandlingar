---
kommun: kungsbacka
organ: bygg-projekt
datum: 2025-06-10
lopnr: null
typ: handlingar
namn: utredning-av-onsalamotet-avs-onsalamotet-bilaga-1-validerings-pm
kallnyckel: sitevision:18.4590b12c19749b756fc7d0c6
tidigare_kallnycklar: []
arenden: null
kalla_url: https://kungsbacka.se/download/18.4590b12c19749b756fc7d0c6/1749542945107/%C3%85VS%20Onsalamotet%20Bilaga%201%20Validerings-PM%20trafiksimulering.pdf
sha256: c625f4f1bd61875925fa87333557809cc708a66a42f9313e265e0c63bab2242d
bytes: 1929326
sidor: 34
hamtad: 2026-11-13T17:40:18+00:00
konverterad: 2026-11-13T17:40:26+00:00
pipeline: kommunhandlingar 0.11.0 / pdfplumber 0.11.10 / pdfminer.six 20260107
kvalitet: full
fel: null
kvalitet_per_sida: [ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok]
tal_obekraftade: [18]
figurer: [1, 7, 8, 10, 12, 13, 15, 16, 17, 19, 21, 22, 23, 24, 26, 27, 28, 30, 31, 34]
tolkade: []
granskad: null
---

<!-- sida 1 -->

Onsalamotet

Åtgärdsvalsstudie

Bilaga 1 Validerings-PM trafiksimulering

2025-06-10

<!-- sida 2 -->

Onsalamotet

Åtgärdsvalsstudie

Bilaga 1 – Validerings-PM Trafiksimulering

2025-06-10

BESTÄLLARE

Kungsbacka kommun

UTREDARE

Bouvier Sverige AB

2

<!-- sida 3 -->

Innehåll

1  Inledning .......................................................................................................................... 4
2  Trafikflöden och trafikmätningar ................................................................................. 5

2.1  Indata trafikflöden nulägesmodell ..................................................................... 5

2.2  Kompletterande drönarfilmningar Bouvier ...................................................... 5
3  Trafikprognoser .............................................................................................................. 6

3.1  Markanvändning ................................................................................................... 6

3.2  Sampers, Basprognos 2024 (BP24) .................................................................... 9
3.3  Kungsbacka kommuns trafikprognos .............................................................. 11

3.4  Skillnad mellan BP24 och Kungsbackas prognosstyrda scenario ................ 13
3.5  Rimlighetsbedömning befintliga prognoser.................................................... 16

3.6  Framtagande av ny prognos ............................................................................. 18

3.7  Rimlighetsbedömning av ny prognos .............................................................. 21
4  Mikrosimuleringsmodell .............................................................................................. 22

4.1  Mikrosimulering i VISSIM ................................................................................... 22

4.2  Basmodell ............................................................................................................ 22
4.3  Validering trafikflöden och kölängder .............................................................. 23

4.4  Validering/Kalibrering trafikbeteende och kölängder ................................... 26

4.5  Osäkerheter och psykologiska effekter ........................................................... 29
Bilaga 1 – Trafikflöden nuläget (mätningar) FM 07.00-08.00. ......................................... 30

Bilaga 2 – Trafikflöden nuläget (mätningar) EM 16.00-17.00 .......................................... 31
Bilaga 3 – Validering trafikflöden FM .................................................................................. 32

Bilaga 4 – Validering trafikflöden EM .................................................................................. 33

3

<!-- sida 4 -->

1  Inledning

Detta PM syftar till att validera den mikrosimuleringsmodell som tagits fram för
Onsalamotet, och att bedöma dess tillförlitlighet som underlag för vidare planering.
Valideringen baseras på jämförelser mellan simulerade och uppmätta trafikflöden
samt observationer från platsbesök. Vidare beskrivs även metoden som använts för
att ta fram den framtidsprognos som använts i utredningsalternativen.

4

<!-- sida 5 -->

2  Trafikflöden och trafikmätningar

2.1 Indata trafikflöden nulägesmodell
Trafikflödena och svängandelarna för nulägesscenariot i denna analys är baserade
på en tidigare genomförd trafikanalys1 av sträckan E6/E20 mellan Mölndal och
Kungsbacka, framtagen inom ramen för projektet ÅVS Varberg–Göteborg. I denna

analys togs indata fram genom trafikräkningar, drönarfilmningar och användning av
nationella databaser (TIKK och STRESS). Räkningarna genomfördes under
maxtimmarna på morgon och eftermiddag och utvärderades genom att identifiera

de mest belastade halvtimmarna, vilka sedan dubblerades för att erhålla
dimensionerande timflöden.

De observerade flödena och svängandelarna från denna tidigare analys har använts
som grund för mikrosimuleringsmodellen i nuläget för Onsalamotet, då de

representerar en väldokumenterad och kalibrerad bild av trafikläget vid tidpunkten
för mätningarna. Genom att återanvända detta underlag säkerställs en konsekvent
metodik samtidigt som modellen kan jämföras med tidigare analyser och resultat.
Bilaga 1–2 visar trafikflöden för förmiddagens och eftermiddagens maxtimme utifrån

befintliga trafikmätningar i området, drönarfilmer samt trafikflöden från den tidigare
trafikanalysen.

2.2 Kompletterande drönarfilmningar Bouvier
I den förra trafikanalysen som genomfördes så ingick inte cirkulationsplatsen vid
Inlagsleden/Onsalavägen norr i modellområdet (vid Circle K). För att samla in
information kring flöden och svängandelar i denna korsning genomfördes

kompletterande drönarfilmningar. Vid platsbesöket var det dock mörkt och dimmigt
vilket gjorde det svårt att samla in data för hela maxtimmarna varför endast
korttidsräkningar används från dessa drönarfilmer. Detta bedömdes räcka för att
uppskatta svängandelar och ungefärliga flöden. Även köbildningar och till viss del

trafikantbeteende observerades under detta platsbesök och användes i validerings-
och kalibreringsprocessen av basmodellen.

1 ÅVS Varberg-Göteborg - Trafikanalys E6/E20 Mölndal-Kungsbacka - WSP 2019

5

<!-- sida 6 -->

3  Trafikprognoser

I denna trafikanalys har två olika prognoser använts vid framtagandet av de framtida
trafikmängderna: Trafikverkets basprognos 2024 (BP 2024) samt Kungsbacka
kommuns egen prognos (prognosstyrt scenario). Prognoserna skiljer sig åt både vad
gäller indata och resultat, det vill säga de beräknade trafikflödena. Dessa skillnader

beskrivs i följande kapitel.

3.1 Markanvändning

Inom trafikprognosmodeller avser markanvändning hur olika delar av samhällets
ytor utnyttjas – exempelvis för bostäder, arbetsplatser, handel, service och
utbildning. Det handlar både om typen av användning och den geografiska
placeringen av dessa funktioner.

Markanvändning är en grundläggande faktor i modeller som Sampers och andra
liknande prognosverktyg, eftersom den påverkar antalet resor, resornas start- och
målpunkt samt val av färdmedel. Exempelvis ökar tillgången till kollektivtrafik i
bostadsnära områden sannolikheten för att människor väljer att resa kollektivt,

medan utspridd bebyggelse ofta medför en ökning av bilresor. Placeringen av skolor,
arbetsplatser och handelsområden påverkar också hur människor rör sig samt hur
långa resorna blir.

Tillförlitliga indata om markanvändning är därför avgörande för att skapa trovärdiga
prognoser kring framtida resande, kapacitetsbehov och planering av investeringar i
transportsystemet.

Figur 1och Figur 2 visar skillnader i nattbefolkning mellan Kungsbackas trafikmodell
och Sampers.

6

<!-- sida 7 -->

Figur 1 - Markanvändningsutveckling nattbefolkning enligt kommunens trafikmodell.

Figur 2 - Markanvändningsutveckling nattbefolkning enligt Trafikverkets basprognos 2024 (BP24).
Figur 3 och Figur 4 visar skillnaden i dagbefolkning i Kungsbackas trafikmodell

respektive Sampers.

7

<!-- sida 8 -->

Figur 3 - Markanvändningsutveckling dagbefolkning enligt kommunens trafikmodell

Figur 4 - Markanvändningsutveckling dagbefolkning enligt Trafikverkets basprognos 2024 (BP24).

8

<!-- sida 9 -->

Tabell 1 visar en sammanställning över hur markanvändningen förändras i
Kungsbackas trafikmodell respektive Sampers.

Tabell 1 - Skillnad i markanvändningsutveckling mellan BP24 och Kungsbacka kommuns prognos.

Som visas i tabellen ovan så innebär kommunens prognosstyrda scenario en
markant större tillväxt både vad gäller dagbefolkning och nattbefolkning än det som
prognosticeras i Sampers BP24.

3.2 Sampers, Basprognos 2024 (BP24)
Sampers är Trafikverkets nationella modell för persontransporter, som används för

att förutse efterfrågan på resor inom Sverige. I den senaste versionen, Sampers 4,
beräknas inte enbart hur människor reser, utan även hur många som har körkort,
periodkort och tillgång till bil – faktorer som tidigare angavs som indata. Modellen
omfattar resor med personbil, kollektivtrafik, gång och cykel, samt färdmedel som

tunnelbana, spårvagn och färjor. Däremot inkluderas inte moped, motorcykel eller
internationella resor, med undantag för vissa resor över Öresund.

Enligt Trafikverket2 förväntas det totala persontransportarbetet i Sverige öka med
28 % från 2019 till 2045, vilket motsvarar en genomsnittlig årlig tillväxt på cirka 0,9 %.

Den största relativa ökningen väntas ske för resor med tåg och spårtrafik – 47 %
respektive 42 % – framför allt till följd av utbyggd infrastruktur. Personbilen förblir
dock det dominerande färdmedlet och beräknas stå för omkring 72 % av det totala
transportarbetet, medan flygets andel bedöms minska till 2 %.

För Onsalamotet visar den aktuella basprognosen beräknade trafikflöden för åren
2019 och 2045, se Figur 5 och Figur 6

2 Prognos för persontrafik 2045 - Trafikverket 2024

9

[Tabell 9-1](handlingar-utredning-av-onsalamotet-avs-onsalamotet-bilaga-1-validerings-pm.tabeller/9-1.csv)

|  | BP2024 |  |  | Kommunprognos |  |  |
| --- | --- | --- | --- | --- | --- | --- |
|  | År 2019 | År 2045 | Ökning | År 2021 | År 2050 | Ökning |
| Nattbefolkning | 25 800 | 33 800 | 31 % | 25 700 | 54 500 | 112 % |
| Dagbefolkning | 15 700 | 18 900 | 20 % | 13 300 | 25 300 | 90 % |

<!-- sida 10 -->

Figur 5 - Nulägesflöden (VVMD, 2019) i BP24.

Figur 6 - Prognosflöden (VVMD, 2045) i BP24.

10

<!-- sida 11 -->

3.3 Kungsbacka kommuns trafikprognos
Kungsbacka kommun förväntas öka sin befolkning från cirka 85 000 till 130 000
invånare fram till år 2050, varav hälften av tillväxten beräknas ske inom Kungsbacka

stad. Denna utveckling medför en kraftig ökning av trafikvolymerna, särskilt om
resebeteendet förblir oförändrat. I ett prognosstyrt scenario – där resvanorna antas
ligga kvar på dagens nivå – uppstår enligt beräkningar allvarliga trafikproblem redan
år 2027. År 2050 bedöms trafiksystemet vara så belastat att det inte längre fungerar

effektivt, även med genomförda infrastrukturanpassningar. Många korsningar
förväntas då sakna tillräcklig kapacitet.

I ett alternativt målstyrt scenario, där andelen bilresor minskar med 5 % till 2027 och

40 % till 2050, blir trafikbelastningen betydligt mer hanterbar. Även om viss trängsel
kvarstår, särskilt under eftermiddagens maxtimme, förkortas köerna och
trafikavvecklingen sker snabbare. En viss nivå av trängsel kan också bidra till ett ökat
inslag av hållbara färdmedelsval.

Det viljestyrda scenariot förutsätter dock att kommunen aktivt styr utvecklingen mot
politiskt och strategiskt uppsatta mål, i stället för att enbart anpassa infrastrukturen
efter befolkningstillväxt och ökande trafik – vilket är fallet i det prognosstyrda

scenariot. Av denna anledning valdes det viljestyrda scenariot inte som underlag för
vidare analys. Figur 7 och Figur 8visar trafikmängderna för nuläget och 2050
(prognosstyrt scenario) från Kungsbackas trafikmodell i VISUM.

11

<!-- sida 12 -->

Figur 7 – Nulägesflöden (ÅDT, 2021) i kommunens trafikmodell.

12

<!-- sida 13 -->

Figur 8 - Prognosflöden (ÅDT, 2050) i kommunens trafikmodell för prognosstyrda scenariot.

3.4 Skillnad mellan BP24 och Kungsbackas prognosstyrda scenario
I Tabell 2 och Figur 9 nedan redovisas skillnader i trafikflöden mellan BP24 (2019 och

2045\) och Kungsbackas prognosstyrda scenario (2021 och 2050).

Analysen visar att trafikflödena längs E6 är likvärdiga i respektive nuläge, vilket

innebar att ingen uppräkning gjordes för att kompensera för skillnaden i basår.
Jämfört med tillgängliga mätpunkter ligger båda prognoserna något över eller under
de faktiska värdena, beroende på var längs E6 jämförelsen sker. Dessa avvikelser
bedömdes vara marginella, och därför genomfördes inga justeringar.

13

<!-- sida 14 -->

För Onsalavägen Ö, på Kungsbackasidan av Onsalamotet, är skillnaderna mellan
prognoserna däremot betydande. I Trafikverkets BP24 anges ett trafikflöde på
endast 7 800 fordon, medan Kungsbackas prognos visar nära 15 000 – att jämföra

med cirka 17 000 enligt en faktisk mätning på platsen.

I framtidsscenarierna uppvisar Kungsbackas prognosstyrda scenario genomgående
högre trafikflöden än BP24 för samtliga studerade länkar. För tre av fyra länkar rör

det sig om en skillnad på cirka 10 %, medan Onsalavägen in mot Kungsbacka avviker
mest med en skillnad på närmare 70 %.

Tabell 2 - Trafikökning på utvalda länkar vid Onsalamotet. Nuläget motsvaras av 2019 i BP24 och
2021 i Kungsbackas prognos (Kba). Framtidsprognoserna motsvarar 2045 i BP24 och 2050 i
Kungsbackas prognosstyrda scenario.

14

[Tabell 14-1](handlingar-utredning-av-onsalamotet-avs-onsalamotet-bilaga-1-validerings-pm.tabeller/14-1.csv)

| E6 N |  |  | E6 S |  |  | Onsalav. Ö |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Mätning | 41 400 |  | Mätning | 32 400 |  | Mätning | 17 000 |
| BP24 2019 | 39 300 |  | BP24 2019 | 36 000 |  | BP24 2019 | 7 800 |
| Kba 2021 | 39 400 |  | Kba 2021 | 36 700 |  | Kba 2021 | 14 800 |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
| E6 N |  |  | E6 S |  |  | Onsalav. Ö |  |
| BP24 2045 | 54 800 |  | BP24 2045 | 49 000 |  | BP24 2045 | 9 900 |
| Kba 2050 | 61 700 |  | Kba 2050 | 52 700 |  | Kba 2050 | 29 600 |

<!-- sida 15 -->

Figur 9 - Skillnad i trafikflöde (dubbelriktad trafik) 2045/2050 mellan BP24 och kommunprognos.
Grå boxar visar nettoskillnaden (kommunsprognos – BP24) och guldig box visar den procentuella
skillnaden (kommunprognos – BP24).

15

<!-- sida 16 -->

Figur 10 - Skillnad i genomgående trafikflöde för prognos 2045/2050.

3.5 Rimlighetsbedömning befintliga prognoser
Vid en rimlighetsbedömning av de två befintliga prognoserna – Trafikverkets
basprognos och Kungsbackas prognosstyrda scenario identifierades brister i båda.
Kungsbackas prognos utgår från en kraftig befolkningstillväxt i kombination med ett

oförändrat resebeteende, vilket leder till en betydande ökning i biltrafik. Den
trafikanalys3 som genomfördes i samband med framtagandet av den nya fördjupade
översiktsplanen (FÖP) för Kungsbacka stad visar dock att den förväntade
trafikmängden inte kan hanteras inom stadens vägnät.

3 Trafikanalys – Underlag till fördjupad översiktsplan för Kungsbacka stad -
Kungsbacka kommun 2023

16

<!-- sida 17 -->

Resultaten indikerar att trafiksituationen i hela Kungsbacka riskerar att bli kraftigt
överbelastad (Kungsbacka kommun 2023a). Se Figur 11 för resultat från
trafikanalysen.

Figur 11 - Resultat från Trafikanalys av Norconsult i samband med framtagandet av ny FÖP för
Kungsbacka stad (Kungsbacka kommun 2023a).

17

<!-- sida 18 -->

Mot bakgrund av dessa resultat bedömdes Kungsbackas prognosstyrda scenario inte
vara lämplig att använda som underlag för trafikanalysen för Onsalamotet. Framför
allt ansågs prognosen riskera att överskatta de framtida trafikflödena i området.

I Trafikverkets prognos BP24 så kunde de konstateras att nulägesflödet in mot
Kungsbacka stad vid Onsala motet var lågt i förhållande till de mätningar som fanns
tillgängliga. Vid en översikt av trafikflödena in mot Kungsbacka stad vid samtliga tre

trafikplatser längs E6 kunde de även konstateras att Sampers inte fördelade trafiken
mellan trafikplatserna på ett rimligt sätt. Tabell 3 redovisar hur fördelningen mellan
trafikplatserna ser ut i respektive framtidsscenario. En jämförelse mellan
Kungsbackas prognosstyrda scenario och BP24 påvisar stora skillnader i

Onsalamotet. Framför allt skiljer sig trafiken till och från E6 N där BP24 knappt har
någon trafik. Den stora orsaken till att det skiljer sig bedöms vara skillnaden i
detaljkodning inne i Kungsbacka stad. I Sampers där BP24 används är kodningen

enkel samtidigt som den är väldigt detaljerad i Kungsbacka stads trafikmodell. Detta
medför skillnader i restider inne i Kungsbacka stad och således påverkar detta även
valet av trafikplats. Baserat på detta bedömdes Kungsbackas trafikmodell ha ett mer
pålitligt resmönster vilket också medförde att BP24 ensamt inte ansågs vara en

tillräckligt pålitlig prognos.

Tabell 3 - Fördelning av trafik mellan trafikplatserna i Kungsbackas prognosstyrda scenario 2050
och BP24 2045.

Sammantaget bedömdes ingen av de två befintliga prognoserna vara lämpliga att

använda enskilt. En ny prognos togs fram baserat på de två befintliga prognoserna,
se kapitel 3.6.

3.6 Framtagande av ny prognos
För den nya prognosen bestämdes att trafikutvecklingen i huvudsak skulle baseras
på Trafikverkets BP24. Detta dels för att Trafikverket är väghållare för trafikplatsen,
dels för att BP24 är Trafikverkets nationella prognoser för vägtrafik och för att

Kungsbacka kommuns prognosstyrda scenario bedöms överskatta
trafikutvecklingen. I stället för att använda BP24 utan justering så beslutades att
resmönstret i den nya prognosen skull baseras på Kungsbacka kommuns

18

n

rå 4

if 2 % %

% %

r P 6 2 % % 4 8

e B 5 6 0 0 4 3

d

ö

s

g 6

a E

d

a % %

% % %

id

Kb 71 53 9% 25 20 22

rm

e

ft

E n 4

rå 2 % % % %

if P 2 9 2 8 % %

rr B 6 7 3 1 6 3

o

n

E6

a % % % % % %

Kb 48 39 29 30 24 31

n

rå 4

if 2 % %

% %

r P 7 8 % % 3 2

e B 6 4 0 0 3 5

d

ö

s

g E6

a

a

d

b 6% 7% 3% 0% 2% 3%

id

K 5 4 2 1 2 4

rm

ö

F n 4

rå 2 % %

%

if P 1 4 % 3 % %

rr B 9 6 9 3 0 3

o

n

E6

a % % % %

%

Kb 63 51 30 28 6% 21

a

a

a

a ck a ck a ck

ck a ck a ck a

a sb a sb a sb

sb g sb g sb g

g n g n g n

n u n u n u

u K u K u K

K n K n K n

ll å ll å ll å

i r i r i r

T F T F T F

a

la

r

ö

r

r

sa

o

ä

n

N

S

O

<!-- sida 19 -->

prognosstyrda scenario. Det prognosstyrda scenariot bedömdes vara det scenario
som på bästa sätt återspeglar hur trafiken rör sig till och från Kungsbacka
(Kungsbacka stad och Onsala), även om trafikmängderna bedömdes vara för höga.

Figur 12 visar zonindelningen för framtagandet av den nya prognosen.

Figur 12 - Zonindelning för OD-matris (nuläget).

Följande steg genomfördes för att ta fram den nya prognosen:
1\. Två likadana OD-matriser skapades, en för BP24 och en för kommunens

prognosstyrda scenario.

Tabell 4 - Matris BP24 2045 FM innan justeringar.

19

[Tabell 19-1](handlingar-utredning-av-onsalamotet-avs-onsalamotet-bilaga-1-validerings-pm.tabeller/19-1.csv)

| BP24<br>FM |  | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  | Nod | Norr (E6) | Söder (E6) | Väster | Cirkulation norr (4) | Cirkulation öst (5) | Cirkulation söder (6) |
| 1 | Norr (E6) | 0 | 1113 | 222 | 0 | 0 | 0 |
| 3 | Söder (E6) | 1917 | 0 | 110 | 89 | 46 | 0 |
| 2 | Väster | 651 | 150 | 0 | 168 | 87 | 0 |
| 4 | Cirkulation norr (4) | 20 | 43 | 70 | 0 | 0 | 0 |
| 5 | Cirkulation öst (5) | 16 | 34 | 56 | 0 | 0 | 0 |
| 6 | Cirkulation söder (6) | 0 | 0 | 0 | 0 | 0 | 0 |

<!-- sida 20 -->

Tabell 5 - Matris kommunens prognosstyrda prognos 2050 FM.

2\. Totaltrafik till/från Kungsbacka stad samt till/från E6 beräknades i BP24.
Sedan beräknades mängden trafik som trafikerar Onsalamotet baserat på
den procentuella fördelningen i kommunens prognosstyrda scenario. Utöver

detta lades trafik från Cirkulationsplats söder (6) som saknades i BP24. Denna
trafik hämtades från kommunens prognosstyrda scenario.

3\. Efter steg 1–2 skapades en ny OD-matris baserat på trafikfördelningen i

kommunens prognosstyrda scenario med inkommande trafik från BP24. På
så vis skapades en matris där trafiken rör sig enligt kommuns prognosstyrda
scenario men med totala trafikmängder enligt BP24 (efter steg 2).

Tabell 6 - Matris BP24 2045 FM efter omfördelning enligt kommunens prognosstyrda scenario och
med trafik från Cirkulation söder (6).

4\. Utöver trafiken i BP24 lades trafik till/från Gräskärr till i prognosen baserat på
trafiken i kommunens prognosstyrda scenario, se Figur 13 nedan. Denna
trafik är tillkommande för framtidsscenariot 2045–2050 och saknas

ursprungligen i BP24. Detta steg görs inte för nuläget 2019–2021.
5\. Trafik till/från Onsala hämtades från BP24 men fördelades i vägnätet enligt
kommunens prognosstyrda scenario.
6\. Baserat på steg 1–5 skapades en OD-matris för Onsalamotet genom en

kombination av BP24 och kommunens prognosstyrda scenario.

20

[Tabell 20-1](handlingar-utredning-av-onsalamotet-avs-onsalamotet-bilaga-1-validerings-pm.tabeller/20-1.csv)

| Kommun<br>FM |  | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  | Nod | Norr<br>(E6 ) | Söder<br>(E6) | Väste<br>r | Cirkulation norr<br>(4) | Cirkulation öst<br>(5) | Cirkulation söder<br>(6) |
| 1 | Norr (E6) |  | 1370 | 242 | 14 | 12 | 0 |
| 3 | Söder (E6) | 2443 |  | 46 | 185 | 154 | 5 |
| 2 | Väster | 761 | 68 |  | 600 | 501 | 16 |
| 4 | Cirkulation norr (4) | 114 | 79 | 64 |  | 124 | 22 |
| 5 | Cirkulation öst (5) | 367 | 255 | 206 | 227 |  | 21 |
| 6 | Cirkulation söder<br>(6) | 15 | 11 | 9 | 15 | 25 |  |

[Tabell 20-2](handlingar-utredning-av-onsalamotet-avs-onsalamotet-bilaga-1-validerings-pm.tabeller/20-2.csv)

| BP24<br>F M |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | Norr (E6) | Söder (E6) | Väster | Cirkulation norr (4) | Cirkulation öst (5) | Cirkulation söder (6) |
| 1 | Norr (E6) | 0 | 1117 | 197 | 29 | 25 | 0 |
| 3 | Söder (E6) | 1868 | 0 | 35 | 47 | 39 | 1 |
| 2 | Väster | 416 | 37 | 0 | 328 | 274 | 16 |
| 4 | Cirkulation norr (4) | 63 | 15 | 22 | 0 | 43 | 22 |
| 5 | Cirkulation öst (5) | 201 | 47 | 21 | 23 | 0 | 21 |
| 6 | Cirkulation söder (6) | 8 | 2 | 9 | 15 | 25 | 0 |

<!-- sida 21 -->

Figur 13 - Zonindelning inklusive Gräskärr.

Tabell 7 - Ny matris 2045–2050 FM baserat på de två ursprungliga scenariona, BP24 och
kommunens prognosstyrda scenario.

Steg 1–6 genomfördes för nuläget 2019–2021 (baserat på BP24 2019 och
kommunens nulägesscenario 2021) och för framtidsprognosen 2045–2050 (baserat

på BP24 2045 och kommunens prognosstyrda scenario 2050). Beräkningar
genomfördes för både förmiddagen och eftermiddagens trafik.

Med hjälp av nuläget och en framtidsprognos kunde två differensmatriser skapas, en

för förmiddagen och en för eftermiddagen. Dessa differensmatriser användes senare
som påslag på de beräknades nulägesflödena från tidigare trafikanalys och de
drönarfilmer som låg till grund för trafiken i den tidigare nulägesmodellen, både
förmiddag och eftermiddag.

3.7 Rimlighetsbedömning av ny prognos
Den använda metoden för framtagande av framtidsprognosen bedömdes vara
lämplig där de två befintliga prognoserna kombineras och således även en rimlig

prognos för trafikanalysen utifrån tillgängligt underlag.

21

[Tabell 21-1](handlingar-utredning-av-onsalamotet-avs-onsalamotet-bilaga-1-validerings-pm.tabeller/21-1.csv)

| Ny prognos<br>F M |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | Norr<br>(E6) | Söder<br>(E6) | Väster | Cirkulation norr<br>(4) | Cirkulation öst<br>(5) | Cirkulation söder<br>(6) | Gräskärr |
| 1 | Norr (E6) | 0 | 1117 | 197 | 29 | 25 | 0 | 53 |
| 3 | Söder (E6) | 1868 | 0 | 35 | 47 | 39 | 1 | 55 |
| 2 | Väster | 416 | 37 | 0 | 328 | 274 | 16 | 71 |
| 4 | Cirkulation norr (4) | 63 | 15 | 22 | 0 | 43 | 22 | 70 |
| 5 | Cirkulation öst (5) | 201 | 47 | 21 | 23 | 0 | 21 | 223 |
| 6 | Cirkulation söder<br>(6) | 8 | 2 | 9 | 15 | 25 | 0 | 9 |
| 7 | Område nordöst | 21 | 1 | 1 | 16 | 13 | 0 | 0 |

<!-- sida 22 -->

4  Mikrosimuleringsmodell

4.1 Mikrosimulering i VISSIM
Kapacitet och framkomlighet i vägnätet har analyserats med mikrosimulering i
mjukvaran VISSIM. VISSIM simulerar samtliga trafikslag på individnivå, vilket innebär
att det är möjlig att analysera hur motorfordon, gående och cyklister integrerar med

varandra i vägnätet. Exempel på resultat som kan plockas ut från
simuleringsmodellerna är kölängder, hastigheter, fördröjningar, restider och generell
nätverksprestanda.

4.2 Basmodell
Som grund för de utredningsförslag som analyserats i denna trafikanalys byggdes
först en basmodell upp i VISSIM. Basmodellen representerar dagens infrastruktur

och trafikflöden utifrån indata som beskrivs i kapitel 1. Modellens utbredning och
zonindelning visas i Figur 14. Zonerna representerar platser i modellen där trafik
antingen skickas in i modellen, eller platser dit trafiken åker.

Figur 14 - Basmodell i VISSIM med tillhörande zoner
I basmodellen ligger även övergångsställen med oskyddade trafikanter samt

kollektivtrafiklinjer inlagda. Gående och cyklister som korsar respektive överfart har
endast uppskattats översiktligt för att skapa ett störningsmoment för biltrafiken.
Busslinjer som trafikerar modellen visas i Tabell 8.

22

<!-- sida 23 -->

Tabell 8 - Busslinjer som trafikerar modellen samt antal avgångar under maxtimme

Antal avgångar och ungefärliga tider har hämtats från Västtrafiks tidtabeller.
4.3 Validering trafikflöden och kölängder
Utifrån trafikmätningar och kompletterande drönarobservationer har de

modellerade trafikflödena för nuläget jämförts med de uppmätta för att validera att
de representerar nuläget på ett bra sätt. Figur 15 visar de platser där de modellerade
trafikflödena har jämförts med mätningar.

Figur 15 - Punkter i vägnätet där modellerade trafikflöden jämförts med trafikmätningar och
drönarobservationer

Tabell 9 visar tillhörande namn för respektive punkt.

23

[Tabell 23-1](handlingar-utredning-av-onsalamotet-avs-onsalamotet-bilaga-1-validerings-pm.tabeller/23-1.csv)

| Linje | Antal avgångar<br>maxtimme FM | Antal avgångar<br>maxtimme EM |
| --- | --- | --- |
| 730 södergående | 5 | 0 |
| 730 norrgående | 0 | 5 |
| 731 södergående | 5 | 10 |
| 731 norrgående | 10 | 5 |

<!-- sida 24 -->

Tabell 9 - Punkter där modellerade trafikflöden jämförts med uppmätta trafikflöden

Det finns även trafikmätningar över bron på Onsalavägen från 2015. Dessa

mätningar visar något högre/lägre trafikflöden än de modellerade trafikflödena
beroende på riktning och tidpunkt. Bedömningen gjordes att nulägesmodellen inte
bör kalibreras mot mätningar som är 10 år gamla. Den befintliga trafikmodellen och
nyare mätningar bedömdes vara mer pålitliga för att representera nuläget på ett bra

sätt.

För att validera de modellerade trafikflödena har det statistiska måttet GEH (Geoffrey
E. Havers mått) använts. GEH är ett vanligt förekommande verktyg inom

trafikmodellering som används för att jämföra simulerade trafikflöden med
uppmätta flöden. Måttet tar hänsyn till både relativa och absoluta skillnader mellan
modell och verklighet och lämpar sig väl för trafikflöden i storleksordningen 100–10
000 fordon.

GEH beräknas enligt formeln:

där M är det modellerade flödet och O är det uppmätta trafikflödet.
För att modellen enligt denna metod ska anses vara väl kalibrerad ska 80–85% av

länkarna i modellen ha ett GEH-värde < 5.
Under förmiddagens maxtimme påvisade två punkter i nulägesmodellen ett GEH > 5,
se Tabell 10.

24

[Tabell 24-1](handlingar-utredning-av-onsalamotet-avs-onsalamotet-bilaga-1-validerings-pm.tabeller/24-1.csv)

| 1 | E6 N södergående | 9 | Avfartsramp E6 norrgående |
| --- | --- | --- | --- |
| 2 | E6 N norrgående | 10 | Påfartsramp E6 norrgående |
| 3 | Avfartsramp E6 södergående | 11 | Kollavarvsvägen södergående |
| 4 | Påfartsramp E6 södergående | 12 | Kollavarvsvägen norrgående |
| 5 | Onsalavägen S södergående | 13 | Inlagsleden Ö östgående |
| 6 | Onsalavägen S norrgående | 14 | Inlagsleden Ö västgående |
| 7 | E6 S södergående | 15 | Onsalavägen N södergående |
| 8 | E6 S norrgående | 16 | Onsalavägen N norrgående |

<!-- sida 25 -->

Tabell 10 - Punkter med GEH > 5 under förmiddagen

Vad gäller Onsalavägen S i södergående riktning stämdes denna punkt endast av
mot den tidigare trafikanalysen som hade ett något mindre flöde. Detta bedöms
bero på de justeringar som gjorts i modellen vad gäller inkommande trafikflöden till
följd av tillkommande zoner (cirkulationsplats vid macken). Trafikflödena i modellen

har justerats i mindre steg upp eller ner för att få trafikflödena från gamla analysen
att stämma överens med mätningarna vid cirkulationsplatsen
Inlagsleden/Onsalavägen, vilket ger vissa avvikelser från gamla analysen.
Bedömningen är att denna skillnad inte är något som gör att nulägesmodellen för

förmiddagen inte representerar nuläget i tillräckligt bra omfattning. Kollavarvsvägen i
södergående riktning stämdes enbart av mot en korttidsräkning från den
kompletterande drönarfilmningen. När drönarfilmningen genomfördes var det
mörkt och problem med dimma, vilket gjorde att endast korttidsräkning under 15

minuter genomfördes. Denna korttidsräkning multiplicerades sedan med 4 för att få
ett uppskatta maxtimmesflöde. Skillnaden i denna punkt beror troligtvis på att
korttidsräkningen genomfördes under en ”lugnare” del av maxtimmen under
förmiddagen. Det ska dock tilläggas att skillnaden i dessa två punkter inte är stor och

trafikflödena ligger ändå i samma härad som observationerna.

Under eftermiddagen erhåller samtliga punkter GEH < 5 minst en del av intervallet av
observationerna.

Avslutningsvis vad gäller validering av trafikflöden är det generellt ofrånkomligt att
vissa punkter i modellen uppvisar avvikelser mot de uppmätta trafikflödena. Detta

beror bland annat på att modellen representerar ett genomsnitt över tio separata
modellkörningar, vilket i praktiken kan jämföras med att beskriva ett medelvärde för
tio olika dagar med varierande trafikförhållanden.

De modellerade flödena jämförs sedan med ett fåtal verkliga trafikmätningar under
maxtimmen. I praktiken skulle variationen troligtvis vara relativt stor om man skulle
jämföra fler dagar med varandra genom fler trafikmätningar.

25

[Tabell 25-1](handlingar-utredning-av-onsalamotet-avs-onsalamotet-bilaga-1-validerings-pm.tabeller/25-1.csv)

|  |  | Modellerat<br>trafikflöde FM | Trafikmätningar | GEH<br>min | GEH<br>max | Påvisar<br>GEH < 5 |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | Onsalavägen S<br>södergående | 440 | 340 | 5,06 | 5,06 | NEJ\* |
| 11 | Kollavarvsvägen<br>södergående | 210 | 120 | 7,01 | 7,01 | NEJ\* |

<!-- sida 26 -->

Därför är viss avvikelse mellan modell och mätdata både förväntad och accepterad,
så länge nulägesmodellen som helhet uppvisar god överensstämmelse enligt
vedertagna valideringsmått, vilket i detta fall visas genom GEH-analysen. Där GEH-

värdet överstiger 5, eller är nära 5 är troligtvis dagsvariationerna för trafikflödet i
punkten större än skillnaden som krävs för att värdet ska bli under 5.

4.4 Validering/Kalibrering trafikbeteende och kölängder
Utöver validering av trafikflödena i modellen i föregående avsnitt har även
trafikantbeteende och ungefärliga kölängder validerats. Exempel på
trafikantbeteenden som har validerats och kalibrerats:

•  Hur stor andel av trafikanterna som använder blinkers, vilket då innebär att
inkommande trafik kan våga sig ut i korsningen/cirkulationsplatsen tidigare
•  Tidsluckor som generellt krävs vid väjningssituationer
•  Vävningssituationer

Ovanstående beteenden har validerats visuellt genom att granska trafikanternas
beteende när modellen kör och stämt av med det som kunde observeras från
drönarfilmerna.

Vad gäller kölängderna har dessa dels bedömts utifrån kartor som visar den relativa
fördröjningen i nulägesmodellerna, dels via observationer från drönarfilmerna. Den
relativa fördröjningen visar var fordon i modellen inte lyckas köra i sin önskade
hastighet (rödare färg i kartan), vilket uppstår vid korsningar och köbildning.

Observera att den relativa fördröjningen i kartorna visar den 85:e percentilen, vilket
innebär att fördröjningen är mindre än vad figurerna visar 85% av tiden, och värre
15% av tiden. Kartbilderna visar alltså de lite värre perioderna under maxtimmen.

Figur 16 visar den relativa fördröjningen för nuläget under förmiddagens maxtimme.

Figur 16 - Relativ fördröjning nuläget FM

26

<!-- sida 27 -->

Figuren ovan visar att trafiken går trögt in mot Kungsbacka under förmiddagens
maxtimme, med köbildningar vid cirkulationsplatsen Inlagsleden/Onsalavägen. Detta
observerades även under platsbesöket och kommunen bekräftar att den

modellerade fördröjningen representerar den verkliga trafiksituationen på ett bra
sätt under förmiddagens maxtimme. Figur 17 visar den relativa fördröjningen för
eftermiddagens maxtimme.

Figur 17 - Relativ fördröjning nuläget EM

Den relativa fördröjningen under eftermiddagen påvisar en än mer belastad
trafiksituationen än under eftermiddagen, vilket också upplevdes under

platsbesöket. Köer sträcker sig in mot Kungsbacka vid cirkulationsplatsen vid
macken, och trafiken går även trögt i södergående riktning längs hela bron söderut
mot Onsala. Figur 18 visar en ögonblicksbild som visar denna situation från
drönarfilmen.

27

<!-- sida 28 -->

Figur 18 - Ögonblicksbild drönarfilm under eftermiddagens maxtimme

Observera att trafiken går trögt i södergående riktning mot Onsala, precis som den
relativa fördröjningen från modellen visar under eftermiddagens maxtimme. Figur 19

visar en exempelbild från simuleringen under eftermiddagens maxtimme som även
där påvisar köer över bron i riktning mot Onsala.

Figur 19 - Ögonblicksbild från simuleringen under eftermiddagens maxtimme
Det ska också noteras att mycket av fördröjningarna som sker över bron på

Onsalavägen i båda riktningarna (som påvisar gul färg i fördröjningskartorna) beror
på långsamtgående fordon som skapar kösvansar och fördröjningar. I basmodellen
ligger det med 4% långsamtgående fordon, vilket var den andel som observerades
under platsbesöket.

28

<!-- sida 29 -->

Sammanfattningsvis är bedömningen att utifrån observationer från drönarfilmer,
platsbesök samt utlåtanden från kommunen så representerar modellen
förmiddagens- och eftermiddagens maxtimme på ett bra sätt vad gäller köbildning

och tröghet i systemet.

4.5 Osäkerheter och psykologiska effekter
Vid all typ av trafikmodellering och simulering finns det osäkerheter kopplade till
prognoser, trafikantbeteende och indata. Tumregeln är att prognoser och
simuleringar görs på bästa möjliga sätt utifrån rådande kunskap och underlag som

finns kring objektet. Syftet med nulägesmodellen är att ta fram en basmodell som
representerar nuläget på bästa sätt. Detta för att känna trovärdighet i de
utredningsalternativ som sedan simuleras med nya utformningar och prognoser. En
viktig faktor att belysa vad gäller tolkning av resultatet av utredningsalternativen är

att resultaten bygger på fasta ruttval. Detta innebär att oavsett belastning i vägnätet
så kommer fordonen vilja följa sin förbestämda rutt och tar ingen hänsyn till
köbildningar och fördröjningar som påvisas i vissa utredningsalternativ. I

verkligheten är ruttvalen mer dynamiska och resenärer tenderar att lära sig att
undvika de värsta köerna genom att ta andra rutter, resa under andra tider eller i
stället åka kollektivt om detta är ett snabbare alternativ. Dessa effekter är ingenting
som fångas upp i simuleringsresultaten, men bör tas med i beaktande vid tolkning av

resultaten.

29

<!-- sida 30 -->

Bilaga 1 – Trafikflöden nuläget (mätningar) FM 07.00-08.00.

<!-- sida 31 -->

Bilaga 2 – Trafikflöden nuläget (mätningar) EM 16.00-17.00

31

<!-- sida 32 -->

Bilaga 3 – Validering trafikflöden FM

32

[Tabell 32-1](handlingar-utredning-av-onsalamotet-avs-onsalamotet-bilaga-1-validerings-pm.tabeller/32-1.csv)

|  |  | Modellerat<br>trafikflöde FM | Trafikmätningar | GEH min | GEH max | Påvisar GEH < 5 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | E6 N södergående | 1290 | 1041–1280 | 0,28 | 7,29 | JA |
| 2 | E6 N norrgående | 2580 | 2314–2658 | 1,52 | 5,38 | JA |
| 3 | Avfartsramp E6 södergående | 170 | 193–246 | 1,71 | 5,27 | JA |
| 4 | Påfartsramp E6 södergående | 200 | 158–211 | 0,77 | 3,14 | JA |
| 5 | Onsalavägen S södergående | 440 | 340 | 5,06 | 5,06 | NEJ\* |
| 6 | Onsalavägen S norrgående | 1280 | 1351 | 1,96 | 1,96 | JA |
| 7 | E6 S södergående | 1350 | 1075–1243 | 2,97 | 7,9 | JA |
| 8 | E6 S norrgående | 1970 | 1471–2009 | 0,87 | 12,03 | JA |
| 9 | Avfartsramp E6 norrgående | 193 | 187–234 | 0,44 | 2,81 | JA |
| 10 | Påfartsramp E6 norrgående | 813 | 865–1045 | 1,80 | 7,61 | JA |
| 11 | Kollavarvsvägen södergående | 210 | 120 | 7,01 | 7,01 | NEJ\* |
| 12 | Kollavarvsvägen norrgående | 150 | 120 | 2,58 | 2,58 | JA |
| 13 | Inlagsleden Ö östgående | 550 | 430–544 | 0,26 | 5,42 | JA |
| 14 | Inlagsleden Ö västgående | 560 | 444–498 | 2,70 | 5,18 | JA |
| 15 | Onsalavägen N södergående | 200 | 172–195 | 0,36 | 2,05 | JA |
| 16 | Onsalavägen N norrgående | 340 | 252–288 | 2,93 | 5,11 | JA |

<!-- sida 33 -->

Bilaga 4 – Validering trafikflöden EM

33

[Tabell 33-1](handlingar-utredning-av-onsalamotet-avs-onsalamotet-bilaga-1-validerings-pm.tabeller/33-1.csv)

|  |  | Modellerat<br>trafikflöde EM | Trafikmätningar | GEH min | GEH max | Påvisar GEH < 5 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | E6 N södergående | 2440 | 2462–2824 | 0,44 | 7,48 | JA |
| 2 | E6 N norrgående | 1380 | 1356–1488 | 0,65 | 2,85 | JA |
| 3 | Avfartsramp E6 södergående | 910 | 595–798 | 3,83 | 11,48 | JA |
| 4 | Påfartsramp E6 södergående | 200 | 184–269 | 1,15 | 4,51 | JA |
| 5 | Onsalavägen S södergående | 1370 | 1387 | 0,46 | 0,46 | JA |
| 6 | Onsalavägen S norrgående | 470 | 477 | 0,32 | 0,32 | JA |
| 7 | E6 S södergående | 1720 | 1766–2344 | 1,10 | 13,84 | JA |
| 8 | E6 S norrgående | 1320 | 1334–1522 | 0,38 | 5,36 | JA |
| 9 | Avfartsramp E6 norrgående | 220 | 177–255 | 2,27 | 3,05 | JA |
| 10 | Påfartsramp E6 norrgående | 341 | 335–411 | 0,33 | 3,61 | JA |
| 11 | Kollavarvsvägen södergående | 160 | 160 | 0,00 | 0,00 | JA |
| 12 | Kollavarvsvägen norrgående | 150 | 176 | 2,04 | 2,04 | JA |
| 13 | Inlagsleden Ö östgående | 500 | 509–788 | 0,40 | 11,35 | JA |
| 14 | Inlagsleden Ö västgående | 740 | 624–739 | 0,04 | 4,44 | JA |
| 15 | Onsalavägen N södergående | 390 | 414–443 | 1,20 | 2,60 | JA |
| 16 | Onsalavägen N norrgående | 340 | 298–348 | 0,43 | 2,35 | JA |

<!-- sida 34 -->

www.bouvier.se
