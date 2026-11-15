---
kommun: kungsbacka
organ: bygg-projekt
datum: 2026-06-08
lopnr: null
typ: handlingar
namn: bostader-i-notegang-rapport-skyfallsmodell-2024
kallnyckel: sitevision:18.6447748c19e63923234955da
tidigare_kallnycklar: []
arenden: null
kalla_url: https://kungsbacka.se/download/18.6447748c19e63923234955da/1780902628868/Rapport%20Skyfallsmodell%202024.pdf
sha256: 6984c6c46cccd2632655e435563f356be915238e14c6fc014181bce12094dcfe
bytes: 2262490
sidor: 26
hamtad: 2026-11-15T09:25:39+00:00
konverterad: 2026-11-15T09:25:44+00:00
pipeline: kommunhandlingar 0.11.0 / pdfplumber 0.11.10 / pdfminer.six 20260107
kvalitet: text-utan-tabeller
fel: null
kvalitet_per_sida: [ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, ok, tabell-osaker, ok]
tal_obekraftade: []
figurer: [1, 7, 9, 10, 12, 13, 14, 15, 19, 20, 21, 22, 26]
tolkade: []
granskad: null
---

<!-- sida 1 -->

Skyfallsmodellering

Detaljplan Nötegången  2:207,

Kungsbacka   kommun

Sluthandling
2024-03-13

<!-- sida 2 -->

<!-- sida 3 -->

Ändringsförteckning

Ver   Datum   Ändringsbeskrivning
001   2024-03-13 Granskningshandling

001   2024-03-13 Sluthandling

Sweco Sverige AB RegNo 556767-9849
Uppdrag        Skyfallsmodellering Nötegång 2:207
Uppdragsnummer 30044464
Kund           Kungsbacka Kommun
Kontaktperson  Maria Brink, Frida Moberg
Upppdragsledare, handläggare Anna Dahlström
Teknisk specialist, granskare Daniel Lundqvist
Datum          2024-03-13
Ver            001, Sluthandling
Dokumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313
3/26

<!-- sida 4 -->

Innehållsförteckning

1   Inledning ........................................................................................................................ 5
2   Hydraulisk modell .......................................................................................................... 6
3   Modellresultat ................................................................................................................ 8
3.1 Tolkning av resultat ........................................................................................... 8
3.2 Befintlig situation ............................................................................................... 8
3.3 Framtida situation ............................................................................................ 10

4   Slutsatser ..................................................................................................................... 16
5   Bilaga 1: Modelluppbyggnad ....................................................................................... 17
5.1 Underlag .......................................................................................................... 17
5.2 Programvara och modellavgränsning ............................................................. 18
5.3 Regnbelastning ............................................................................................... 19
5.4 Ledningsnätsmodell ........................................................................................ 20
5.4.1  Befintlig situation ............................................................................. 21
5.4.2  Framtida situation ........................................................................... 22
5.5 Markavrinningsmodell ..................................................................................... 23
5.5.1  Höjdmodell ...................................................................................... 23
5.5.2  Infiltration ........................................................................................ 23
5.5.3  Strömningsmotstånd (Mannings tal) ............................................... 24
5.6 Randvillkor ...................................................................................................... 25
5.6.1  Inflöden från uppströms avrinningsområden .................................. 25
5.6.2  Vattennivå i Skörvallabäcken ......................................................... 25
5.6.3  Utflöden........................................................................................... 25

4/26

<!-- sida 5 -->

1    Inledning

Exploatering av bostäder planeras inom detaljplan Nötegången 2:207 i Särö,
Kungsbacka kommun. På uppdrag av Kungsbacka kommun har Sweco
studerat skyfallshanteringen för området med syfte att utreda hur
exploateringen påverkas, förslagna dagvattenanläggningarnas effekt samt
påverkan på omkringliggande områden i händelse av kraftig nederbörd.
En dagvattenutredning1 har tagits fram för planområdet där det föreslås att
dagvatten avleds till öppna svackdiken och vidare till en torr damm för
fördröjning av ett klimatanpassat 20-årsregn, innan anslutning sker till befintligt
dagvattenledningsnät. Uppströmsliggande område avrinner idag till ett befintligt

dike genom planområdet, vilket det även fortsättningsvis föreslås ske.
I händelse av kraftig nederbörd fylls dagvattenledningsnät och öppna
dagvattenanläggningar. Detta eftersom ledningsnät och anläggningar inte är
dimensionerade för nederbördshändelser av högre återkomsttid, då de är
sällsynta och det inte vore ekonomiskt eller tekniskt försvarbart att anlägga.
Konsekvensen blir att avrinning av högre flöden sker på marken.
Höjdsättningen blir då styrande för vattnets väg och vart vatten blir stående.
Större rinnvägar och lågpunkter kan utgöra en risk för översvämning.

Skyfallshanteringen har tidigare studerats med ett statiskt verktyg utifrån
topografin. Denna metod för skyfallskartering beskriver bland annat inte
dynamiken under händelseförloppet, flödeshastigheter eller utbredning av
flödesvägar. Detta gör att skyfallssituationen kan under- eller överskattas
beroende på områdets förhållanden. Med anledning av att ett skyfallsstråk
korsar planområdet och att ett villaområde beläget norr om planområdet utgör
en större lågpunkt, så studeras skyfallssituationen mer ingående med en
hydraulisk modell för att bedöma planområdets lämplighet för byggnation. En
iterativ arbetsprocess för framtida situation har lett fram till de slutliga studerade
dagvatten- och skyfallsåtgärderna samt höjdsättning av området.

1 Dagvattenutredning Nötegång 2:207, Kungsbacka kommun, Sweco, 2021-10-15.

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 5/26

<!-- sida 6 -->

2    Hydraulisk       modell

Kopplade 1D-2D-modeller bestående av markavrinnings- och
ledningsnätsmodeller har tagits fram för befintlig och framtida situation
inkluderat föreslagen dagvattenhantering för området. Modellerna är uppbyggda
i programvaran MIKE+ (2022) och avgränsas av det tillrinnande
avrinningsområdet till Skörvallabäcken och planområdet. Ett 100-årsregn med
klimatfaktor 1,4 har studerats för befintlig och framtida situation. Ytterligare
beskrivning av modellernas uppbyggnad återfinns i bilaga 1.
Framtida situation inkluderar ett antal åtgärder för dagvatten- och
skyfallshantering vars utformning dels har utretts i tidigare dagvattenutredning2,

dels under föreliggande utredning genom en iterativ process tillsammans med
kommunen, Skanska och landskapsarkitekter på Sweco.
Följande dagvatten- och skyfallsåtgärder har inkluderats i modellen för framtida
situation (se Figur 14 för illustration av åtgärder):
•  Torr damm för klimatanpassat 20-årsregn (volym ca 3 200 m3, strypt
utflöde 360 l/s till anslutning i befintlig dagvattenledning i Olov
Persvägen). Utflödet från dammen regleras via en munkbrunn med
utlopp i botten på nivån +1,65 och en brädd på nivån +3,2.
•  Dike genom planområdet (utökad sektion och justerat läge jämfört med
befintligt dike). Se Figur 1 för principsektion.
o  Vägar som korsar dikesstråket har medvetet sänkts ned för att
medge att vatten att rinna över vägarna vid höga flöden i
händelse av skyfall för att motverka att vatten dämmer mot
vägtrummor och breder ut sig till omgivande tomter.
o  Tre st parallella betongkulvertar av dimension 500 mm under
vägarna som korsar dikesstråket.
•  Dike längs planområdets östra gräns med avskärande funktion för att
fånga upp ytligt flöde österifrån. Diket ansluter öppet till den torra
dammen. Se Figur 1 för principsektion.
•  Diket längs den norra plangränsen har tagits bort för att medge ytlig
avrinning från befintliga angränsande fastigheter till den framtida torra
dammen.

2 Dagvattenutredning Nötegång 2:207, Kungsbacka kommun, Sweco, 2021-10-15.

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 6/26

<!-- sida 7 -->

Figur 1  Principsektion för diket genom planområdet (”bäcken”) och för det östra diket.

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 7/26

<!-- sida 8 -->

3    Modellresultat

Modellresultat har bearbetats för maximalt vattendjup, maximalt vattenflöde
samt översvämningsvaraktighet för vattendjup över 20 cm, vilka redovisas för
befintlig och framtida situation i efterföljande kapitel. En analys av konsekvenser
inom och utom planområdet samt framkomlighet inom och till/från planområdet
redovisas även för framtida situation.

3.1  Tolkning   av resultat

Resultat för maximalt vattendjup visar det maximala vattendjupet som uppstår
lokalt någon gång under simuleringstiden. Det maximala vattendjupet inträffar
inte samtidigt överallt. Vattendjup som understiger 10 cm redovisas inte, vilket
innebär att det kan finnas översvämningsytor som ser ut att vara fristående men
som egentligen är sammanhängande. Denna avvägning är gjord för att ge
bättre helhetsförståelse för en extrem situation, där någon form av
översvämning sker överallt. Vid bedömning av framkomlighet på vägar är det
normalt att 20 cm vattendjup studeras, då överskridande vattendjup bedöms
påverka fordonens tekniska förmåga.
Resultat för maximalt vattenflöde visar det maximala ytvattenflödet som uppstår
lokalt någon gång under simuleringstiden. Ytvattenflödet, som har enheten
m2/sekund, kan ibland upplevas som något abstrakt och svårgripbart i
planeringssammanhang. Resultatet används främst för att analysera var vatten
rinner och för att särskilja storleken mellan flödesvägar.
Översvämningens varaktighet redovisas för vattendjup som överstiger 20 cm.
Resultatet används när det är intressant att veta hur lång tid det tar för vattnet
att rinna undan. I instängda områden som saknar koppling till
dagvattensystemet kan en lång översvämningsvaraktighet förväntas, eftersom
det instängda området endast kan tömmas via infiltration.
3.2  Befintlig situation

Planområdet med omgivande bebyggelse översvämmas vid skyfall i befintlig
situation. Vattendjup på upp till 1 m beräknas erhållas inom planområdet i
händelse av ett klimatanpassat 100-årsregn. För en avgränsad del av norra
planområdet beräknas vattendjup över 1 m i anslutning till en större befintlig
lågpunkt norr om planområdet. (Figur 2)
Ytliga flöden rinner till planområdet via ett befintligt dikesstråk och
Carlbergsvägen söderifrån och diffust västerifrån. Det ytliga flödet genom
planområdet breder ut sig på ett stort område inom planområdet i händelse av
ett klimatanpassat 100-årsregn. Maximala vattenflöden beräknas upp till 0,2-0,5
m2/s inom planområdet. (Figur 3)

Varaktigheten för vattendjup över 20 cm inom planområdet är mindre än en
timme, med undantag för norra delen av planområdet som angränsar till den
större lågpunkten utanför planområdet. Varaktigheten på översvämning i
lågpunkten norr om planområdet beräknas vara 5-6 timmar. (Figur 4)

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 8/26

<!-- sida 9 -->

Figur 2  Maximalt vattendjup för befintlig situation vid ett 100-årsregn med klimatfaktor
1,4. Vattendjup under 10 cm illustreras inte i resultatet.

Figur 3  Maximalt vattenflöde för befintlig situation vid ett 100-årsregn med klimatfaktor
1,4. Flöden lägre än 0,02 m2/s illustreras inte i resultatet.

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 9/26

<!-- sida 10 -->

Figur 4  Översvämningsvaraktighet för vattendjup över 20 cm för befintlig situation vid ett
100-årsregn med klimatfaktor 1,4.

3.3  Framtida   situation

Framtida situation har studerats tillsammans med åtgärdsförslag för dagvatten-
och skyfallshantering. Utformning av åtgärder och höjdsättning har tagits fram
genom en iterativ arbetsprocess för att säkerställa god skyfallshantering inom
planområdet och att planförslaget inte medför någon påverkan på
omkringliggande områden samt att det finns framkomlighet inom/till/från planen.

Maximalt vattendjup över 1 m beräknas inom dikesstråk genom planområdet
och den torra dammen, vilket är eftersträvat utifrån åtgärdernas utformning.
Modellresultatet visar att vatten blir stående mot husfasader angränsande till
den torra dammen. (Figur 5)
Färdiga golvnivåer för tomter utmed den torra dammen och dikesstråken bör
regleras i plankarta utifrån beräknade maximala vattennivåer samt en viss
säkerhetsmarginal. Beräknad maximal vattennivå i anslutning till den torra
dammen har beräknats till ca +4,4 m och längs med de båda dikesstråken upp
till ca +6,6 m. (Figur 10)

Nivåer för vägarna som korsar dikesstråket bör regleras i plankarta för att säkra
att ingen kraftigare dämning sker (ca +4,2 m för norra vägen och ca +5,2 m för
södra vägen).
Södra delen av det område som planeras medge stycketomter (norr om gatan
Nötegången) bedöms inte vara lämplig för byggnation med hänsyn till
beräknade vattendjup samt vattenflöde som rinner över gatan Nötegången och

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 10/26

<!-- sida 11 -->

korsar tomten. Det rekommenderas att södra delen av området utgör PARK i
plankarta. Det finns begränsningar i att höja upp tomtmarken för mycket med
hänsyn till tillgänglighet (lutningsförhållanden) samt geotekniska förutsättningar.
Styrning av flödet i ett dike utmed gatan har diskuterats inom uppdraget (u-
område i plankarta, (Figur 11). Utformning och effekt av en sådan åtgärd har
inte studerats inom uppdraget och därmed kan ingen slutsats dras ifall åtgärden
skulle kunna medföra byggbar yta. Bredd enligt u-område bedöms emellertid
inte vara tillräckligt. Det har även diskuterats att placera stycketomterna på
andra ytor inom planområdet. (Figur 5)
Placering av E-område inom u-området bedöms utgör en risk med hänsyn till
beräknat vattendjup och vattenflöde som rinner över gatan Nötegången. (Figur
11\)

Mindre vattenansamlingar (vattendjup under 20 cm) som ses på gata inom
planområdet bedöms kunna åtgärdas genom höjdsättning av planområdet i
kommande projekteringsskede. (Figur 5)
Stora vattenflöden beräknas i dikesstråken, genom planområdet (över 0,5 m2/s)
och längs planområdets östra gräns (0,2-0,5 m2/s), i riktning mot den torra
dammen. Norr om planområdet ses likt för befintlig situation en stor utbredning
av flöde genom ett villaområde mot Skörvallabäcken. (Figur 6)

Varaktigheten för vattendjup över 20 cm inom planområdet är mindre än en
timme, med undantag för inom dikesstråken och den torra dammen vilket är
eftersträvat. Översvämningsvaraktighet beräknas för den befintliga lågpunkten
norr om planområdet till 4-5 timmar vid framtida situation med planerade
dagvatten- och skyfallsåtgärder, vilket är en minskning jämfört med befintlig
situation. (Figur 7)

Vid jämförelse av beräknat maximalt vattendjup för befintlig situation (Figur 2)
och framtida situation (Figur 5), kan planförslagets påverkan på vattendjupet vid
skyfall analyseras. Planförslaget med dagvatten- och skyfallsåtgärder bedöms
inte medföra någon försämring, utan snarare en viss förbättring, avseende
maximalt vattendjup vid ett klimatanpassat 100-årsregn för omgivande befintlig
bebyggelse. Ett ökat vattendjup inom planområdet ses i den torra dammen och
dikesstråken, vilket är eftersträvat. (Figur 8)
Framkomligheten inom planområdet samt till/från planområdet har studerats
med avseende på maximalt beräknat vattendjup 20 cm. Infart och vägar inom
planområdet bedöms vara framkomliga. Undantag gäller för vägarna som
korsar dikesstråket genom planområdet. Dessa har medvetet sänkts ner så
långt det är möjligt med hänsyn till lutningsförhållanden på vägarna, så vatten
kan rinna över vägen istället för att dämmas upp mot vägen och breda ut sig
mot omgivande tomter. Detta medför att vägarna inte beräknas vara
framkomliga vid ett klimatanpassat 100-årsregn. Framkomlighet till planområdet
öster om dikesstråket bedöms emellertid finnas via gatan Nötegången söder om
planområdet. För en sträcka på ca 10 m bedöms det vara begränsad bredd på
gatan med vattendjup mindre än 20 cm, varför en dialog med räddningstjänst
rekommenderas gällande acceptabla vattendjup, erforderlig bredd och avstånd.
(Figur 9)

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 11/26

<!-- sida 12 -->

Figur 5  Maximalt vattendjup för framtida situation vid ett 100-årsregn med klimatfaktor
1,4. Vattendjup under 10 cm illustreras inte i resultatet.

Figur 6  Maximalt vattenflöde för framtida situation vid ett 100-årsregn med klimatfaktor
1,4. Flöden lägre än 0,02 m2/s illustreras inte i resultatet.

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 12/26

<!-- sida 13 -->

Figur 7  Översvämningsvaraktighet för vattendjup över 20 cm för framtida situation vid ett
100-årsregn med klimatfaktor 1,4.

Figur 8  Skillnad i maximalt vattendjup för befintlig och framtida situation, där rött innebär
en ökning i vattendjup och grönt en minskning i vattendjup vid framtida situation.
Skillnader i vattendjup +/- 5 cm illustreras inte i resultatet.
Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 13/26

<!-- sida 14 -->

Figur 9  Framkomliga vägar för framtida situation vid ett 100-årsregn med klimatfaktor 1,4
bedömt utifrån maximalt vattendjup 20 cm.

Figur 10 Maximal vattennivå (plushöjder) för framtida situation vid ett vid ett 100-årsregn
med klimatfaktor 1,4. Nivåerna kan utgöra underlag till bestämning av färdig
golvnivå (max vattennivå + säkerhetsmarginal) för fastigheter angränsande den
torra dammen och de båda dikesstråken. I bakgrund ses max vattendjup över 5
cm.
Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 14/26

<!-- sida 15 -->

Figur 11 Utdrag från plankarta för Nötegång 2:207, samrådshandling, upprättad 2022-01-
28, Kungsbacka kommun.

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 15/26

<!-- sida 16 -->

4    Slutsatser

Skyfallsmodelleringen för detaljplanområdet Nötegången 2:207 har resulterat i
följande slutsatser:
•  En god skyfallshantering bedöms kunna upprätthållas inom
planområdet med föreslagna åtgärder för dagvatten och skyfall samt
studerad höjdsättning. Färdiga golvnivåer bör emellertid säkras i

plankarta för fastigheter angränsande till den torra dammen och de
båda dikesstråken. Färdig golvnivå föreslås baseras på beräknade
maximala vattennivåer vid ett klimatanpassat 100-årsregn med ett visst
påslag för extra säkerhetsmarginal. Vidare bör nivåer för vägarna som
korsar diket regleras i plankarta för att kraftigare dämning inte ska
inträffa.
•  Planförslaget bedöms inte medföra försämring för omkringliggande
områden. En viss förbättring ses för ett avgränsat område norr om
planområdet till följd av studerade åtgärder.
•  Alla fastigheter inom planområdet bedöms vara framkomliga i händelse
av ett klimatanpassat 100-årsregn. Dialog med räddningstjänst gällande
erforderlig bredd, vattendjup och avstånd för framkomlighet på
Nötegången (gata söder om planområdet) rekommenderas för att säkra
framkomligheten till östra delen av planområdet.
•  Södra delen av område för stycketomter (norr om gatan Nötegången)
bedöms inte vara lämplig för byggnation och rekommenderas utgöra
PARK i plankarta.
•  Höjdsättning i kommande projekteringsskede ska, utöver att beakta
hittills utrett utformning av dagvatten- och skyfallsåtgärder samt
höjdsättning, även säkerställa att det inte blir mindre vattenansamlingar
på gata och tomter.

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 16/26

<!-- sida 17 -->

5    Bilaga     1: Modelluppbyggnad

Denna bilaga utgör inte en komplett modellteknisk dokumentation utan en
översiktlig beskrivning av skyfallsmodellernas uppbyggnad för befintlig och
framtida situation.

5.1  Underlag

Digitalt underlag som har nyttjats vid modelluppbyggnad för befintlig situation
och för framtida situation har listats i Tabell 1.
Andra utredningar vars information har nyttjats i utredningen:

•  Översvämningskartering Skörvallabäcken, Kungsbacka kommun,
Norconsult, 2020-05-07.
•  Dagvattenutredning Nötegång 2:207, Kungsbacka kommun, Sweco,
2021-10-15.
•  VA-ritning, Särö, Nötegång, Kungsbacka Förlagshandling, R-51-1-
0001, SKANSKA, Sweco, 2022-06-23, samt uppdaterad ritning R-51-P-
1-001.dwg erhållen av Sweco 2024-02-27.

Tabell 1 Digitalt underlag för modellering av befintlig och framtida situation.
Filnamn     Filtyp Beskrivning och källa       Underlaget Erhållet
beskriver i
modellen

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 17/26

[Tabell 17-18-1](handlingar-bostader-i-notegang-rapport-skyfallsmodell-2024.tabeller/17-18-1.csv)

| Modell: Befintlig/ framtida situation |  |  |  |  |
| --- | --- | --- | --- | --- |
| SGUjordarter | Shape | SGU:s jordartskarta.<br>Underlaget har laddats ner från SCALGO Live av<br>Sweco. | Infiltration | 2022-07-12 |
| 20220622_ortofoto_2<br>020 | Ecw | Ortofoto. Kungsbacka kommuns skanning. | Bakgrunds-<br>karta | 2022-06-22 |
| Modell: Befintlig situation |  |  |  |  |
| Särö_resultat_polygo<br>ner_hardgjort_och_g<br>ront_200925 | Shape | Hårdgjorda och gröna områden framtagna genom<br>IR-analys av flygfoto. Daterat 2020-09-25.<br>Underlaget kompletterades av Sweco med<br>Naturvårdsverkets marktäckesdata (nedladdat från<br>SCALGO Live) för områden utanför underlagets<br>avgränsning. | Infiltration,<br>strömnings-<br>motstånd | 2022-06-22 |
| my_1384 | Shape | Markyta-lager från fastighetskartan nyttjades som<br>ett komplement till IR-analysen, för beskrivning av<br>områden med odling, skog, låg bebyggelse och<br>öppen mark. | Infiltration,<br>strömnings-<br>motstånd | 2022-06-22 |
| byggnader_scalgo | Shape | Befintliga byggnadsytor från Lantmäteriet.<br>Underlaget har laddats ner från SCALGO Live av<br>Sweco. | Infiltration,<br>strömnings-<br>motstånd | 2022-07-11 |
| las_fil | Las | Höjdskanning av befintliga höjder inom<br>avrinningsområdet. Utfört av Kungsbacka kommun.<br>Upplösning 1x1 m.<br>Underlaget kompletterades av Sweco med höjddata<br>av Lantmäteriet, upplösning 1x1 m (nedladdat från<br>SCALGO Live) för områden utanför underlagets<br>avgränsning. | Höjdsättning | 2022-06-22 |
| Dike Nötegång<br>210526 | Dwg | Inmätning av sektioner i befintligt dike genom<br>planområdet. Utfört av Kungsbacka kommun,<br>daterat 2021-05-26. | Höjdsättning | 2022-06-28 |
| Nötegång dike | Dwg | Inmätning av sektioner i befintligt dike söder om<br>planområdet. Utfört av Kungsbacka kommun,<br>daterat 2022-08-15. | Diken och<br>trummor | 2022-08-16 |
| 220907 Nötegång<br>dike JT | Dwg | Inmätning av uppströms och nedströms vattengång<br>för befintlig trumma under väg Nötegången, från<br>dike söder om planområdet. Ledningen är ca 50 m<br>och har en dimension på 500 mm. Första delen av<br>ledningen är i betong, som övergår till plastledning.<br>Utfört av Kungsbacka kommun, daterat 2022-09-<br>07. | Diken och<br>trummor | 2022-09-08 |
| VA_karta Nötegång | Dwg | Befintligt VA-ledningsnät inom och angränsande<br>planområdet. Erhållet av Kungsbacka kommun. | Ledningsnät<br>nedströms-<br>planområdet | 2022-06-22 |
| Modell: Framtida situation |  |  |  |  |
| L-01-P-<br>001_5_SWEREF | Dwg | Situationsplan med framtida byggnadsytor och<br>vägar. Framtaget av Sweco för SKANSKA. | Infiltration,<br>strömnings-<br>motstånd | 2024-02-27 |
| Höjddgrid 1m 2024-<br>02-27 Sweref99<br>1200 | Asc | Framtida höjdmodell för beskrivning av<br>planområdet, inkluderat nya diken och torr damm.<br>Framtaget av Sweco för Kungsbacka kommun. | Höjdsättning | 2024-02-27 |

<!-- sida 18 -->

5.2  Programvara     och modellavgränsning

Skyfallsmodellerna för befintlig och framtida situation har byggts upp med
programvaran MIKE+ och består utav kopplade markavrinningsmodeller (MIKE
21\) samt ledningsnätsmodeller (MIKE+).

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 18/26

<!-- sida 19 -->

Markavrinningsmodellen beskriver avrinning som sker på markytan utifrån
komponenterna höjdmodell, infiltration och markens strömningsmotstånd.
Ledningsnätsmodellen beskriver avledning i ledningsnät, diken och fördröjning i
magasin.

Modellområdet avgränsas av det topografiska avrinningsområdet uppströms
planområdet ner till recipienten Skörvallabäcken, se Figur 12.

Figur 12 Modellen har avgränsats utifrån topografiska avrinningsområdet uppströms
planområdet ner till Skörvallabäcken.

5.3  Regnbelastning

Nederbörd har belastats på markavrinningsmodellen.

Ett CDS-regn av återkomsttid 100 år och varaktighet på sex timmar, inkluderat
en klimatfaktor på 1,4, har studerats för både befintlig och framtida situation, se
Figur 13.
Inget avdrag för avrinning i ledningsnät uppströms planområdet har gjorts med
anledning av att modellområdet följer avrinningsområdet, vilket belastar
planområdet.

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 19/26

<!-- sida 20 -->

Dagvattenledningar inom planområdet förutsätts dimensioneras för att avleda
ett 20-årsregn. Därav har avdrag gjorts för hårdgjorda ytor inom
markavrinningsmodellen och flödena har istället kopplats direkt till
dagvattenutloppen till diken och damm.

100-årsregn, klimatfaktor 1,4

6000

) 5000
g
a
d
/ 4000
m
m
( 3000
te
tis
2000
n
e
tn
1000
I
0
Tidpunkt
Figur 13 Studerad regnbelastning ett CDS-regn med 100 års återkomsttid inkluderat
klimatfaktor 1,4, med en varaktighet på sex timmar.
5.4  Ledningsnätsmodell
I ledningsnätsmodellen beskrivs ledningar och trummor i diken. För befintlig
situation beskrivs även diken av ledningsnätsmodellen, medan diken för
framtida situation beskrivs av höjdmodellen (avsnitt 5.5.1).
I Figur 14 ses omfattning av ledningsnätsmodellerna för befintlig och framtida
situation.

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 20/26

<!-- sida 21 -->

Figur 14 Ledningsnätsmodell för befintlig och framtida situation, undantaget diken och
damm (svart) för framtida situation som beskrivs av markavrinningsmodellen.
Befintliga diken som inte markerats ut i illustrationen har beskrivits av
höjdmodellen.

5.4.1 Befintlig situation
Ledningsnätsmodellen för befintlig situation beskriver befintliga
dagvattenledningar (endast huvudstråk) nedströms planområdet.
Dagvattenledningar uppströms planområdet beskrivs inte i modellen, eftersom
hela avrinningsområdet som belastar planområdet inkluderas i
markavrinningsmodellen når således allt vatten det område som är av intresse
för utredningen.

Dimension, material och vattengångar på befintligt ledningsnät har hämtats ifrån
erhållet underlag.
Följande antaganden har gjorts för ledningar:

•  Brunnar har antagits ha en dimension på 1 m. Nivå på brunnslock har
hämtats ifrån höjdmodellen.
•  Norr om planområdet finns befintliga privata dagvattenledningar, se
Figur 14. Vattengång saknas för intagsbrunnen från diket i norr, därav
har vattengång antagits till +2,48 utifrån mätning av vattenyta i brunnen

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 21/26

<!-- sida 22 -->

(erhållet från Kungsbacka kommun 2022-09-14). I Figur 15 ses
intagsbrunnen.

Befintliga diken och trummor beskrivs av ledningsnätsmodellerna utifrån
inmätningar av sektioner och trummor utförda av kommunen. Undantag gäller
befintligt dike längs planområdets norra gräns som ansluter till den privata
ledningen, vilket beskrivs av höjdmodellen.

Följande antaganden har gjorts:
•  Dikena har tilldelats Mannings tal 10 pga. tät vegetation.
•  Trumman från det befintliga södra diket, under vägen Nötegången,
utgör betong söderifrån och övergår sedan till en plastledning.
Trumman har lagts in som betong då detta utgör den begränsande
faktorn (högre strömningsmotstånd, Mannings tal, än materialet plast).

Figur 15 Intagsbrunn till befintlig privat ledning. Källa: Kungsbacka kommun.

5.4.2 Framtida situation
I framtida situation har de privata dagvattenledningarna utgått.

Befintligt dike utmed planområdets norra gräns utgår i framtida situation, för att
medge avrinning till den torra dammen från fastigheter norr om planområdet.
Inget nytt ledningsnät inom planområdet har inkluderats för framtida situation

med anledning av att hela ledningssystemet ansluter till den torr dammen.
Flöden vid 20-årsregn har anslutits till dagvattenutlopp till diken och dammar, se
avsnitt 5.3 för hur regnet har fördelats inom modellen.
Nya trummor för framtida situation beskrivs av ledningsnätsmodellen med en
antagen dimension på 500 mm i materialet betong. Tre st parallella trummor har
lagts för de båda passagerna där vägar korsar diket inom planområdet.
Vattengångar för trummorna har hämtats från höjdmodellen för framtida
situation.

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 22/26

<!-- sida 23 -->

Utloppet från den torra dammen har beskrivits med ett bottenutlopp på nivån
+1,65 med maximalt tillåtet utflöde 360 l/s till befintligt dagvattenledningsnät i
Olov Persvägen (800 mm) och en bräddnivå på +3,2, enligt erhållen VA-
projektering (Sweco, 24-02-27).

5.5  Markavrinningsmodell

5.5.1 Höjdmodell

Befintlig situation beskrivs av erhållen höjdmodell. Höjdmodellen justerades
genom att fylla igen befintliga diken, som istället beskrivs av inmätta
dikessektioner i ledningsnätsmodellen. En vägbro som korsar Skörvallabäcken
har även sänkts ner för att medge flöden att passera.
Framtida höjdmodell beskriver de nya dikena och den torra dammen, genom
nedsänkta stråk och områden. Den torra dammen har utformats för att inrymma
ca 3 200 m3, vilket motsvarar erforderlig fördröjningsvolym vid ett
klimatanpassat 20-årsregn enligt dagvattenutredning3.
Befintliga och framtida byggnaders takytor har höjts upp med 3 meter i
höjdmodellen, för att avrinning ska ske runt byggnader.
Höjdmodellernas upplösning är 1x1 meter.

5.5.2 Infiltration

För att beskriva hur en del av vattnet från genomsläppliga ytor infiltrerar ner i
marken används en så kallad infiltrationsmodul i markavrinningsmodellen. I
infiltrationsmodulen definieras jordlagrets mäktighet, porositet,
infiltrationsförmåga, det vertikala läckaget till grundvattenytan i underliggande
jordlager samt initial mättnadsgrad. De fem parametrarna som används visas i
Tabell 2.
Tabell 3 anger infiltrationsparametrar för olika klasser av jordarter och Tabell 4
anger vilken klass de jordarter som förekommer inom modellområdet tillhör.

Tabell 2 Infiltrationsparametrar som använts i markavrinningsmodellen.

3 Dagvattenutredning Nötegång 2:207, Kungsbacka kommun, Sweco, 2021-10-15.

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 23/26

[Tabell 23-1](handlingar-bostader-i-notegang-rapport-skyfallsmodell-2024.tabeller/23-1.csv)

| Infiltrationsparameter | Enhet |
| --- | --- |
| Infiltrationshastighet genom markytan | mm/h |
| Porositet i översta jordlagret | % |
| Mäktighet översta jordlagret | m |
| Läckagehastighet till grundvattenakvifer | mm/h |
| Initial vattenmängd i översta jordlagret | % |

<!-- sida 24 -->

Tabell 3 Infiltrationsparametrar för olika klasser av jordarter.

Tabell 4 Klassning av förekommande jordarter.

5.5.3 Strömningsmotstånd (Mannings tal)
I den hydrauliska modellen inkluderas en karta som beskriver markens råhet/
strömningsmotstånd, uttryckt i Mannings tal (M). Mannings tal varierar med
markanvändningen inom modellområdet och har bestämts genom att ansätta
värden enligt Tabell 5.

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 24/26

[Tabell 24-1](handlingar-bostader-i-notegang-rapport-skyfallsmodell-2024.tabeller/24-1.csv)

| Klass (namn) | Infiltrations-<br>hastighet<br>(mm/h) | Porositet<br>(%) | Mäktighet<br>(m) | Läckage<br>(mm/h) | Initial vatten-<br>mättnad (%) |
| --- | --- | --- | --- | --- | --- |
| Fingrus | 360 | 30 | 0,3 | 3600 | 0 |
| Grovsand | 360 | 30 | 0,3 | 360 | 0 |
| Mellansand | 360 | 30 | 0,3 | 36 | 0 |
| Grovsilt | 3,6 | 30 | 0,3 | 0,36 | 0 |
| Morän | 0,36 | 30 | 0,3 | 0,036 | 0 |
| Lerig morän | 0,0036 | 30 | 0,3 | 0,00036 | 0 |
| Lera | 0,0036 | 30 | 0,3 | 0,00036 | 0 |
| Vattenyta | 0 | 0 | 0 | 0 | 0 |
| Hårdgjorda ytor<br>(IR-analys) | 0 | 0 | 0 | 0 | 0 |

[Tabell 24-2](handlingar-bostader-i-notegang-rapport-skyfallsmodell-2024.tabeller/24-2.csv)

| Jordart | Klass (namn) |
| --- | --- |
| Urberg | Hårdgjort |
| Svallsediment, grus | Fingrus |
| Postglacial sand | Grovsand |
| Postglacial finsand | Grovsand |
| Sandig morän | Morän |
| Postglacial finlera | Lera |
| Glacial lera | Lera |
| Vatten | Vattenyta |

<!-- sida 25 -->

Tabell 5 Mannings tal för olika markanvändning.
Markanvändning         Underlag     Mannings tal (M)
[m1/3/s]
Takytor                  Fastighetskarta 60
Vägar                    Från IR-analys 50

Hårdgjorda ytor (utöver tak och vägar) Från IR-analys 50
Markytor                 Fastighetskarta
BEBLÅG        20
ÖPMARK        20
ODLÅKER       10
SKOGBARR      10
SKOGLÖV       10

5.6  Randvillkor

5.6.1 Inflöden från uppströms avrinningsområden

Modellområdet har upprättats utifrån avrinningsområdet. Inga inflöden till
modellområdet från uppströms avrinningsområden ska ske och har där av inte
behövts beskrivas i modellen.

5.6.2 Vattennivå i Skörvallabäcken
I modellen har den initiala vattennivån i Skörvallabäcken satts till +1,8 m
(RH2000), vilket motsvarar Kungsbackafjordens prognostiserade
medelhögvattennivån vid seklets slut enligt MSB:s kartering av Kungsbackaån
(2019)4.

5.6.3 Utflöden

Modellen har definierats med en stängd rand, det vill säga inget vatten
transporteras ut ytledes från modellen. Modellområdet är väl tilltaget och
analyserat utifrån höjddata för att uppdämningar mot modellranden inte ska
påverka resultatet inom det aktuella området av intresse att studera. Felaktiga
resultat maskas bort vid resultatbearbetning.

4 Översvämningskartering utmed Kungsbackaån, Med detaljerad översvämningskartering för det
identifierade området med betydande översvämningsrisk, Kungsbackaområdet, Sträckan från
Östra Ingsjön till mynningen i havet, MSB, Rapport nr 13, 2013-06-14, reviderad 2019-10-24.
Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 25/26

<!-- sida 26 -->

Togethe r with our clients
and the collective
knowledge of our 22,000
architects, engineers and
other specialists, we co-
create solutions that
address urbanisation,
capture the power of
digitalisation, and make our
societies more sustainable.
Sweco – Transforming
society together

Sweco | Skyfallsmodellering Detaljplan Nötegången 2:207,
Kungsbacka kommun
Uppdragsnummer 30044464
Datum 2024-03-13 Ver 001, Granskningshandling
D okumentreferens Rapport_Skyfallsmodell DP Nötegången 2_207_Sluthandling_240313 26/26
