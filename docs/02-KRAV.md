# Krav (beteenden)

Kraven beskriver hur det färdiga systemet fungerar, som Given/When/Then.
Varje krav får ett GitHub-issue när arbetet på det börjar.

## Syfte

Samla **alla** politiska handlingar och protokoll från kommunfullmäktige,
kommunstyrelsen och samtliga nämnder, så långt bakåt som möjligt, som text
och tabeller att bygga dataanalyser på. Kungsbacka först; fler kommuner ska
kunna läggas till utan kodändring.

## K1 — En kommun läggs till med konfiguration

- **Givet** att en kommun publicerar via en plattform som redan har en adapter
- **När** någon skriver `kommuner/<kommun>.toml` med organ, startadresser och
  filnamnsmönster
- **Så** hämtas och konverteras kommunens handlingar utan att någon kod ändras.
- **Givet** en konfiguration som inte följer schemat
- **När** körningen startar
- **Så** stoppas den innan något hämtas, med felet i sammanfattningen.

## K2 — Alla organ och dokumenttyper hittas

- **Givet** en kommuns konfiguration
- **När** upptäckten körs
- **Så** listas varje sammanträde för varje organ i konfigurationen, med
  kallelse, handlingar, protokoll och bilagor som separata dokument, var
  och ett med organ, datum, typ och källnyckel.
- **Givet** en rubrik, ett filnamn eller en sökväg som konfigurationen inte
  översätter till organ, datum och typ
- **När** upptäckten körs
- **Så** blir det ingen kandidat, och det nämns i körningens sammanfattning.
- **Givet** en fil som står på flera ställen i källan, till exempel under
  två sammanträden
- **När** upptäckten körs
- **Så** blir den en enda kandidat.
- **Givet** en källa som anger sammanträdets datum på två ställen, och de
  inte stämmer överens
- **När** upptäckten körs
- **Så** blir det ingen kandidat, och det nämns i körningens
  sammanfattning – om inte kommunens konfiguration har en rättelse för
  filens källnyckel. Då gäller rättelsens datum.

- **Givet** en kommunfil
- **När** upptäckten körs
- **Så** skrivs kandidatlistan till en arbetskatalog utanför repot, i den
  ordning K13 anger, och sammanfattningen visar antalet kandidater per
  organ och varje fil som inte blev kandidat, med orsak.
- **Givet** en källsida som inte går att hämta, eller en arbetskatalog i
  repot
- **När** upptäckten körs
- **Så** stoppas körningen med adressen och orsaken, och ingen
  kandidatlista skrivs. För arkivet gäller K16.

## K3 — Historiken hämtas så långt bakåt den finns

- **Givet** att kommunens webbplats bara visar de senaste åren
- **När** upptäckten körs
- **Så** prövas också de äldre källor konfigurationen anger (t.ex. Internet
  Archive och kommunens diarium), och varje dokument registreras med den
  källa det hittades i. Hur Internet Archive tas in står i K16.

## K4 — Varje dokument blir en Markdown-fil med härkomst

- **Givet** ett hämtat PDF-dokument
- **När** det konverteras
- **Så** skrivs en `.md` vars front matter anger varifrån originalet
  kom, vilket original det var, när det hämtades och konverterades, med
  vilka verktyg och med vilken kvalitet – och PDF:en raderas. Fälten står
  i [Front matter](03-ARKITEKTUR.md#front-matter).
- **Givet** text i PDF:en som Markdown annars läser som struktur, till
  exempel en rad som börjar med `1.`, `#` eller ett
  bindestreck och ett mellanslag, eller en adress
  inom `<…>`
- **När** dokumentet konverteras
- **Så** visar en Markdown-läsare (CommonMark med GFM:s tabeller) texten
  som den stod, utan listor, rubriker, länkar eller HTML som inte kommer
  från konverteringen, och varje `.md` som når `main` klarar
  Markdown-lint ([#65](https://github.com/moggleif/kommunhandlingar/issues/65)).
- **Givet** ett tal i textlagret med ett mellanslag som ligger över en av
  dess siffror, som i en PDF ur ett kalkylark
  (issue [#91](https://github.com/moggleif/kommunhandlingar/issues/91))
- **När** dokumentet konverteras
- **Så** står talet i texten och tabellerna som på sidan, `476,7` och inte
  `4 76,7`.

## K5 — Tabeller blir CSV

- **Givet** ett dokument med tabeller
- **När** det konverteras
- **Så** skrivs varje tabell som går att läsa säkert som en CSV-fil
  bredvid dokumentets `.md`, med sidnummer, och tabellen syns också i
  Markdown-texten. Varje CSV går att föra tillbaka till sitt dokument,
  och därmed till dokumentets härkomst.
- **Givet** en tabell utan lodräta linjer, där varje rad är en etikett
  följd av tal, talen står i linje i kolumner och ingen etikett
  fortsätter på en rad som också har tal
- **Så** går den att läsa säkert och blir CSV som en tabell med linjer.
  Rubrikraderna ovanför följer med när varje rubrik står i linje med sin
  kolumn; annars står de kvar i texten.
- **Givet** en sådan tabell med en eller två rader med bara en etikett
  mellan talraderna, som en avsnittsrubrik eller en etikett som fortsätter
  på nästa rad, med en etikett som fortsätter under den sista raden,
  eller med en rubrikrad med bara årtal
  (issue [#93](https://github.com/moggleif/kommunhandlingar/issues/93))
- **Så** blir den en CSV, inte flera: en avsnittsrubrik blir en rad med
  tomma celler, en fortsättning fogas till etiketten ovanför, och årtalen
  blir tabellens rubrikrad.
- **Givet** en tabell med linjer där en cell rymmer mer än ett tal,
  därför att en rad saknar de lodräta linjer som tabellens andra rader
  har, därför att en vågrät linje saknas mellan rader vars text står på
  samma höjd i varje cell, eller därför att tal står i linje rad efter
  rad utan lodrät linje emellan
  ([#95](https://github.com/moggleif/kommunhandlingar/issues/95))
- **Så** delas den efter linjerna i de andra raderna, efter talen i
  linje och efter textraderna (issue [#60](https://github.com/moggleif/kommunhandlingar/issues/60)),
  och blir CSV med varje tal i en egen cell. En rubrik och ett värde i
  samma cell blir en rubrikrad och en värderad.
- **Givet** en tabell med linjer där en cell rymmer mer än ett tal och
  inte går att dela så, till exempel för att etiketten står mitt emellan
  två tal, en text går över en linje eller en etikett fortsätter på
  nästa rad (issue [#97](https://github.com/moggleif/kommunhandlingar/issues/97))
- **Så** går den inte att läsa säkert med linjerna som cellgränser. Det
  som inte går att läsa som en tabell utan lodräta linjer står kvar i
  sidans text, och står en siffra ur tabellen där märks sidan
  `tabell-osaker`.
- **Givet** ett rutnät av linjer utan text, som stödlinjerna i ett
  diagram
- **Så** blir det ingen tabell och ingen CSV
  (issue [#100](https://github.com/moggleif/kommunhandlingar/issues/100)).
- **Givet** en tabell som inte går att läsa säkert
- **Så** märks den som osäker i stället för att sparas som om den vore riktig:
  den blir ingen CSV, och sidan märks `tabell-osaker`. Står den i texten
  som rader med flera tal står den i Markdown märkt som osäker tabell.
  En tabell på en sida som lästs med OCR blir aldrig CSV, och sidan
  behåller sin OCR-märkning.
- **Givet** en tabell med linjer där linjerna bara ramar in en del av
  tabellen, så att tal i den står utanför dem på samma höjd
  (issue [#90](https://github.com/moggleif/kommunhandlingar/issues/90))
- **Så** blir delen ingen CSV med tal utan etiketter, utan tabellen
  prövas som en tabell utan lodräta linjer, och blir den ingen tabell
  märks sidan `tabell-osaker`.
- **Givet** minst tre rader utanför de tabeller som lästs säkert, var och
  en med minst två tal som inte är årtal, där en rad står i linje med
  minst två av de andra, till exempel en tabell i en spalt bredvid löptext
  (issue [#92](https://github.com/moggleif/kommunhandlingar/issues/92))
- **Så** märks sidan `tabell-osaker`, också när raderna inte står som en
  osäker tabell i texten.

## K6 — Det som inte gick att hämta eller konvertera syns

- **Givet** ett dokument som inte gick att konvertera, helt eller delvis
- **När** konverteringen är klar
- **Så** finns ändå en `.md` med metadata, kvalitetsnivå per dokument och
  per sida, och status – dokumentet utelämnas aldrig.

- **Givet** en sida som behöver OCR – en skanning, en sida med grafik men
  utan tecken, eller en sida där textlagret är oläsligt
- **När** dokumentet konverteras
- **Så** läses sidan med OCR och märks `ocr`. Når OCR inte
  säkerhetströskeln märks sidan `ej-konverterad`, och ingen text från den
  skrivs.

- **Givet** en sida vars tal inte är bekräftade – en sida som lästs med
  OCR, en sida som inte gick att konvertera, eller ett textlager med
  oläsliga tecken
- **När** dokumentet konverteras
- **Så** listas sidan bland dokumentets sidor med obekräftade tal. Text
  och tal märks var för sig: talen på en sida går att använda som data
  när sidan inte står i listan, oavsett textens kvalitet, och alla
  dokumentets tal när listan är tom.

- **Givet** en fil som inte går att öppna som PDF – lösenordsskyddad,
  trasig eller inte en PDF alls
- **När** konverteringen försöker
- **Så** skrivs en `.md` med kvalitet `ej-konverterad` och orsaken i `fel`.

- **Givet** ett dokument där sidorna fått olika kvalitet
- **När** konverteringen är klar
- **Så** är dokumentets kvalitet den som den sämsta sidan ger.

- **Givet** ett dokument som upptäckten hittat men som inte gick att hämta
  (till exempel 404, avbruten anslutning eller en kapad Wayback-kopia)
- **När** försöket är gjort
- **Så** skrivs en `.md` med metadata, kvalitet `ej-hamtad`, tid för
  försöket och orsaken – om dokumentet inte redan har en fullständig
  `.md`. En fullständig `.md` lämnas orörd. Nästa körning försöker igen;
  misslyckas den med samma orsak och samma adress ändras ingenting, annars
  skrivs `ej-hamtad`-filen om.

## K7 — Luckor redovisas

Luckorna räknas fram ur poolen när webbplatsen byggs och lagras inte
([ADR-0020](decisions/0020-luckor-raknas-fram-lagras-inte.md)).

- **Givet** ett sammanträde med minst ett dokument i poolen, vars datum
  har passerat när webbplatsen byggs
- **När** det saknar både kallelse och handlingar, eller protokoll, och
  organet har den typen vid något annat sammanträde
- **Så** redovisas sammanträdet som en lucka på statussidan, med det som
  saknas, organets källor i kommunfilen och när sidan byggdes.

- **Givet** ett sammanträde med en kallelse men inga handlingar, eller
  tvärtom
- **När** webbplatsen byggs
- **Så** är det ingen lucka: kallelsen och handlingarna publiceras ofta
  som en fil, under endera namnet.

- **Givet** ett sammanträde som hölls för färre än 21 dagar sedan
- **När** dess protokoll saknas
- **Så** är det ingen lucka: protokollet kan vänta på justering.

- **Givet** ett sammanträde utan något dokument i poolen, eller ett
  dokument som är `ej-hamtad`
- **När** webbplatsen byggs
- **Så** är det ingen lucka. Mötet går inte att skilja från ett inställt,
  och ett `ej-hamtad` finns och syns under kvalitet (K6).

- **Givet** en bilaga som bara finns vid vissa sammanträden
- **När** webbplatsen byggs
- **Så** är dess frånvaro ingen lucka.

## K8 — Körningen är inkrementell och kan avbrytas

- **Givet** att en källnyckel redan finns i poolen som ett dokuments
  `kallnyckel`, med samma `kalla_url` som upptäckten anger och utan
  kvalitet `ej-hamtad`, och, när kommunfilen har `omkonvertera = true`,
  med den version av poolen som körs i `pipeline`
- **När** en ny körning startas
- **Så** hämtas filen inte, och dokumentets `.md` lämnas orörd.

- **Givet** att en källnyckel finns i ett dokuments `tidigare_kallnycklar`
- **När** en ny körning hittar den
- **Så** känns den igen som samma dokument, hämtas inte, och ersätter inte
  den nyare källnyckeln.

- **Givet** en kandidat som är en kopia från en ögonblicksbild tagen före
  versionen som står i poolen för samma källnyckel – före ögonblicksbilden
  i `kalla_url` när den är en arkivkopia, annars före `hamtad` – och
  dokumentet inte har kvalitet `ej-hamtad`
- **När** en ny körning hittar den
- **Så** hämtas den inte; en äldre kopia ersätter aldrig en nyare version.

- **Givet** en källnyckel som inte finns i poolen, eller en ny `kalla_url`
  för en källnyckel som finns, eller ett dokument med kvalitet `ej-hamtad`
- **När** körningen når det
- **Så** hämtas och konverteras filen. Ett nytt dokument skrivs enligt K4
  och K6, en ny adress för ett befintligt dokument enligt K9, och ett
  dokument med `ej-hamtad` som nu går att hämta skrivs som en fullständig
  `.md` på samma sökväg.

- **Givet** en kommunfil med `omkonvertera = true`, ett fullständigt
  dokument vars `pipeline` har en annan version av poolen än den som
  körs, och en kandidat med samma källnyckel och samma `kalla_url`
- **När** körningen når kandidaten
- **Så** hämtas filen och konverteras om. Är sha256 densamma skrivs
  dokumentet om på samma sökväg med den nya versionens text, tabeller och
  fält, och sammanfattningen räknar det som "konverterad om". Är sha256
  en annan blir det en ny version enligt K9. Går filen inte att hämta står
  den gamla `.md` orörd, och nästa körning försöker igen.

- **Givet** att en körning avbryts mitt i
- **När** nästa körning startas
- **Så** finns ingen PDF i repot och ingen halvskriven `.md`, och nästa
  körning gör färdigt det som återstår.

## K9 — Ändrade dokument blir nya versioner

- **Givet** att kommunen byter ut en fil som redan finns i poolen, under
  ny adress eller nytt filnamn med samma källnyckel
- **När** nästa körning hittar den nya filen
- **Så** konverteras den nya versionen och skrivs över den gamla på samma
  sökväg, och git-historiken visar vad som ändrats.

- **Givet** att den nya versionen inte går att konvertera
- **När** konverteringen är klar
- **Så** skrivs den ändå över den gamla, med ny `kalla_url`, ny sha256 och
  kvaliteten den fick (K6), och git-historiken behåller den gamla texten.

- **Givet** att filen under en ny adress har samma källnyckel och samma
  sha256 som den som redan finns
- **När** nästa körning hittar den
- **Så** uppdateras bara `kalla_url`, och texten konverteras inte om, om
  inte kommunfilen har `omkonvertera = true` och dokumentets `pipeline`
  har en annan version av poolen än den som körs; då konverteras det om
  som i K8.

- **Givet** att kommunen publicerar en fil under en ny källnyckel på ett
  dokuments plats, och den gamla källnyckeln inte längre finns i källan
- **När** nästa körning hittar den
- **Så** blir den en ny version av samma dokument på samma sökväg, och den
  gamla källnyckeln sparas i front matter.

## K10 — Hämtningen är artig

- **Givet** vilken källa som helst
- **När** något hämtas
- **Så** följs `robots.txt`, User-Agent anger vem vi är och hur vi nås,
  anropen till samma värd ligger minst det konfigurerade intervallet isär,
  och 429/5xx leder till att körningen väntar och backar.
- **Givet** en adress som `robots.txt` stänger, för vår User-Agent eller
  för alla
- **När** den ska hämtas
- **Så** hämtas den inte, och orsaken är `robots`.
- **Givet** en värd vars `robots.txt` svarar 4xx, utom 429
- **När** något ska hämtas från den
- **Så** gäller inga begränsningar utöver intervallet.
- **Givet** en värd vars `robots.txt` inte går att hämta, efter de nya
  försöken
- **När** något ska hämtas från den
- **Så** hämtas ingenting från värden.
- **Givet** ett anrop som får 429 eller 5xx, som inte får något svar
  inom tidsgränsen, eller där servern stänger anslutningen eller bryter av
  svaret
- **När** det sker
- **Så** görs ett nytt försök efter en väntan som fördubblas för varje
  försök, eller efter den tid `Retry-After` anger, högst fem minuter, och
  efter det sista försöket är orsaken svaret eller felet.
- **Givet** ett anrop som får en annan 4xx än 429, eller en omdirigering
- **När** det sker
- **Så** görs inget nytt försök, omdirigeringen följs inte, och orsaken är
  `http-` och statuskoden.
- **Givet** en server som inte går att nå, eller en sida i en teckenkodning
  som inte går att läsa
- **När** något hämtas
- **Så** görs inget nytt försök, och orsaken är `anslutning` respektive
  `teckenkodning`.

## K11 — Bara färdiga och kontrollerade körningar når poolen

- **Givet** en körning, schemalagd eller startad för hand
- **När** dess tidsbudget är slut
- **Så** startar den inget nytt dokument, gör färdigt det den håller på
  med om det hinner bli klart före budgetens hårda gräns och lägger det
  annars åt sidan utan att något av det blir kvar, och checkar in det som
  är klart; nästa körning fortsätter med resten, och ett dokument som
  lagts åt sidan syns i körningens sammanfattning.

- **Givet** en körning som har ändrat något
- **När** den ska checka in
- **Så** körs datakontrollerna först, och bara om de går igenom checkas
  ändringen in, på en egen gren som en commit som bara rör filer under
  `data/`; den når `main` genom en PR där samma kontroller körs igen
  (ADR-0015).

- **Givet** en körning vars resultat inte klarar datakontrollerna, som
  stoppas av ett oväntat fel, eller som avbryts innan den checkat in
- **När** den slutar
- **Så** ändras ingenting i poolen, körningen syns som misslyckad, och
  nästa körning börjar från `main` som den är.

- **Givet** att en körning redan pågår
- **När** en till startas, schemalagd eller för hand
- **Så** körs de aldrig samtidigt: den nya väntar tills den första är
  klar, och en start som väntar ersätts av en senare start.

## K12 — Det som en gång tagits in tas inte bort

- **Givet** ett dokument i poolen vars källnyckel och plats ingen kandidat
  har, för att kommunen tagit bort det eller för att källan inte visar så
  långt bakåt
- **När** en ny körning är klar
- **Så** står dokumentets `.md` och tabeller kvar, också när dokumentet
  har kvalitet `ej-hamtad`, och de ändras bara när personuppgifter i dem
  maskas (K17).

## K13 — Kandidaterna hämtas i en bestämd ordning

- **Givet** en kandidatlista för en kommun
- **När** hämtningen börjar
- **Så** tas kandidaterna organ för organ, i den ordning organen står i
  kommunens konfiguration; inom ett organ protokoll, kallelser, bilagor
  och sist handlingar; inom varje typ det äldsta sammanträdet först; och
  vid lika värden i källnyckelns ordning. Kandidater som bara ska
  konverteras om (K8) tas efter alla andra i samma kandidatlista, i samma
  ordning sinsemellan.

- **Givet** samma kandidatlista i en annan upptäcktsordning
- **När** hämtningen börjar
- **Så** tas kandidaterna i samma ordning.

- **Givet** en kandidatlista ur ett arkiv (K16)
- **När** hämtningen börjar
- **Så** tas det nyaste sammanträdet först, för alla organ samtidigt; vid
  samma datum organ och typ som ovan, och sist i källnyckelns ordning.

## K14 — Webbplatsen visar vad poolen innehåller

- **Givet** en kommunfil och poolens dokument under `data/<kommun>/`
- **När** webbplatsen byggs
- **Så** har kommunen en statussida med en rad per organ, i den ordning
  organen står i kommunfilen, med antal sammanträden och antal dokument
  av varje typ.
- **Givet** ett organ i kommunfilen som inte har något dokument i poolen
- **När** webbplatsen byggs
- **Så** står organet med på statussidan, märkt "inget hämtat än".
- **Givet** dokument med olika kvalitet
- **När** webbplatsen byggs
- **Så** visar statussidan för varje organ antal dokument på varje
  kvalitetsnivå och antal sidor med obekräftade tal.
- **Givet** ett dokument vars organ inte står i kommunfilen, eller vars typ
  eller kvalitet inte finns i schemat
- **När** webbplatsen byggs
- **Så** stoppas bygget med dokumentets filnamn, i stället för att
  dokumentet utelämnas tyst ur tabellerna.
- **Givet** en ändring på `main`
- **När** den har checkats in
- **Så** byggs webbplatsen om och publiceras på GitHub Pages, och varje
  sida säger när den byggdes.
- **Givet** en sida på webbplatsen
- **När** den visas
- **Så** har den samma meny, med startsidan och en statussida per kommun,
  och en sidfot som länkar till repot.

## K15 — Figurer märks och kan tolkas

- **Givet** en sida som kan ha ett diagram, en karta, ett schema eller
  en bild
- **När** dokumentet konverteras
- **Så** står sidan i dokumentets `figurer`. En liten logotyp eller ett
  vapen räknas inte, och en sida för mycket är bättre än en för lite.
- **Givet** poolen
- **När** arbetslistan tas fram
- **Så** står varje dokument med sidor i `figurer` som inte står i
  `tolkade`, med de sidorna.
- **Givet** ett dokument i arbetslistan
- **När** dess sidor ska tolkas
- **Så** hämtas originalet på nytt, och sidorna renderas bara om
  originalet har samma sha256 som när det konverterades. PDF:en raderas
  efteråt.
- **Givet** ett diagram vars tal står utskrivna
- **När** sidan tolkas
- **Så** blir talen en tolkad CSV, `<sida>-<nr>.tolkad.csv`. Varje tal i
  den står också i sidans text; ett tal som bara går att läsa av mot en
  axel tas inte med.
- **Givet** ett schema eller ett flöde
- **När** sidan tolkas
- **Så** blir det ett Mermaid-diagram sist på sidan.
- **Givet** en karta, ett foto eller ett diagram utan utskrivna tal
- **När** sidan tolkas
- **Så** blir det en kort beskrivning sist på sidan.
- **Givet** en tolkad sida
- **När** tolkningen är klar
- **Så** står sidan i `tolkade`, och tolkningen står sist på sidan, märkt
  som tolkad, med vem som tolkade och när.
- **Givet** ett tolkat dokument
- **När** det konverteras om
- **Så** försvinner tolkningarna, och sidorna står i arbetslistan igen.
- **Givet** en tolkad CSV med ett tal som inte står i sidans text, eller
  siffror som inte är ett helt tal och inte står ordagrant i sidans
  text, eller på en sida som inte står i `tolkade`; eller en sida i
  `tolkade` utan precis en tolkning med modell och datum, en tolkning
  på en sida som inte står där, eller ett tolkat dokument där en sida
  står två gånger; eller `tolkade` som inte är sidor ur `figurer`, i
  ordning, `figurer` med en sida som inte finns, eller det ena av dem
  `null` men inte det andra
- **När** datakontrollen körs
- **Så** faller den.

## K16 — Internet Archive fyller luckor, sist i körningen

Issues: [#51](https://github.com/moggleif/kommunhandlingar/issues/51) och
[#87](https://github.com/moggleif/kommunhandlingar/issues/87), som slår på
arkivet per organ.

- **Givet** en källa vars konfiguration anger arkivet för ett eller flera
  organ
- **När** körningen har försökt varje kandidat ur de levande källorna, i
  alla kommuner, inom tidsbudgeten
- **Så** upptäcks och hämtas arkivets kopior av de organens filer. Ett
  `ej-hamtad` räknas som försökt.
- **Givet** ett organ i källan som konfigurationen inte anger för arkivet
- **När** arkivet upptäcks
- **Så** läses organets mötessida inte ur arkivet.
- **Givet** att den levande hämtningen har nått tidsbudgetens mjuka gräns
- **När** arkivet står på tur
- **Så** frågas arkivet inte, och nästa körning försöker igen.
- **Givet** att tidsbudgetens hårda gräns nås medan arkivet upptäcks
- **När** gränsen nås
- **Så** avbryts upptäckten, arkivets lista blir tom, och det som hämtats
  från de levande källorna checkas in.
- **Givet** en fråga till arkivet som inte besvaras, efter de nya försöken
  i K10
- **När** arkivet upptäcks
- **Så** hoppas frågan över och nämns i sammanfattningen; körningen går
  vidare, och det som hämtats checkas in.
- **Givet** en mötessida som arkivet inte har någon kopia av
- **När** arkivet upptäcks
- **Så** nämns den i sammanfattningen.
- **Givet** en källnyckel som finns i poolen utan kvalitet `ej-hamtad`, en
  plats som har ett dokument från en levande källa, eller en plats vars
  dokument ur arkivet har en källnyckel som inte finns i arkivets
  kandidatlista
- **När** en kandidat ur arkivet för den källnyckeln eller platsen tas
- **Så** hämtas den inte, och dokumentet i poolen lämnas orört.
- **Givet** flera versioner och kopior av samma fil i arkivet
- **När** arkivet upptäcks
- **Så** blir den nyaste versionen kandidat, med den största kopian och vid
  lika storlek den äldsta; samma arkiv ger samma val varje gång.
- **Givet** en fil på en arkiverad mötessida som arkivet inte har någon
  kopia av
- **När** arkivet upptäcks
- **Så** blir det ingen kandidat, och det nämns i sammanfattningen.
- **Givet** en hämtad kopia ur arkivet som saknar `%%EOF` bland sina sista
  1 024 byte
- **När** den har hämtats
- **Så** blir dokumentet `ej-hamtad` med `fel: kapad` (K6).
- **Givet** ett `ej-hamtad` från en levande källa
- **När** arkivets kopia av samma källnyckel inte heller går att hämta
- **Så** lämnas dokumentets `.md` orörd.

## K17 — Personuppgifter maskas

Issue: [#63](https://github.com/moggleif/kommunhandlingar/issues/63).
Vilka mönster som räknas står i
[Personuppgifter](03-ARKITEKTUR.md#personuppgifter).

- **Givet** ett personnummer, ett mobilnummer, en e-postadress eller en
  gatuadress med postnummer i ett dokuments text eller tabeller
- **När** dokumentet konverteras
- **Så** står en markör i dess ställe, till exempel
  `(personnummer borttaget)`, i både `.md` och CSV, och resten av raden
  och cellen står som förut.
- **Givet** ett tal i en tabell eller i löptext som inte är någon av
  uppgifterna ovan, till exempel ett belopp, ett diarienummer, ett datum
  eller ett organisationsnummer
- **När** dokumentet konverteras
- **Så** står talet kvar som det stod.
- **Givet** förtroendevaldas, tjänstepersoners och enskildas namn, och
  fasta telefonnummer
- **När** dokumentet konverteras
- **Så** står de kvar.
- **Givet** ett dokument i poolen som skrivits av en äldre version
- **När** maskningen körs på poolen
- **Så** maskas texten och tabellerna på samma sätt utan att PDF:en
  hämtas, och en andra körning ändrar ingenting.
- **Givet** en fil i `data/` som innehåller en uppgift som skulle ha
  maskats
- **När** datakontrollen körs (K11)
- **Så** faller den och anger filen, så att uppgiften inte når `main`.

## K18 — Poolens dokument går att läsa på webbplatsen

- **Givet** ett organ i kommunfilen
- **När** webbplatsen byggs
- **Så** har organet en sida som listar dess sammanträden per år, med det
  nyaste först, och varje sammanträdes dokument med typ och kvalitet.
  Statussidan länkar till organets sida.
- **Givet** ett sammanträde med en lucka (K7)
- **När** webbplatsen byggs
- **Så** står det som saknas vid sammanträdet på organets sida.
- **Givet** ett dokument i poolen
- **När** webbplatsen byggs
- **Så** har det en sida som visar härkomsten ur front matter, med källan
  som länk och en länk till `.md` i repot, och sedan texten sida för sida.
- **Givet** en sida i dokumentet
- **När** dokumentets sida visas
- **Så** har den en egen rubrik med sin kvalitet, och en sida i
  `tal_obekraftade` märks i text vid rubriken.
- **Givet** en säker tabell
- **När** dokumentets sida visas
- **Så** står den som tabell med en länk till sin CSV, och CSV:n går att
  hämta från webbplatsen.
- **Givet** en osäker tabell
- **När** dokumentets sida visas
- **Så** står den med uppställningen kvar, märkt i text som osäker.
- **Givet** ett dokument som inte gick att hämta (`ej-hamtad`)
- **När** webbplatsen byggs
- **Så** har det en sida och en rad på organets sida som visar felet och
  källan, så att det inte döljs (K6).
- **Givet** text ur poolen som ser ut som HTML
- **När** webbplatsen byggs
- **Så** visas den som text och blir aldrig markup.

## K19 — En tabell som fortsätter på nästa sida blir en tabell

Issue: [#62](https://github.com/moggleif/kommunhandlingar/issues/62).
Vad som räknas som en fortsättning står i
[Tabeller över flera sidor](03-ARKITEKTUR.md#tabeller-över-flera-sidor).

- **Givet** en säker tabell sist på en sida, som slutar längst ner och
  fortsätter först på nästa sida, med samma kolumner och bara sidhuvud,
  sidfot eller sidnummer emellan
- **När** dokumentet konverteras
- **Så** blir delarna en CSV, vars namn anger första och sista sidan, och
  tabellen står en gång i Markdown-texten, efter första sidans text.
- **Givet** en fortsättning vars första rad är exakt lika med tabellens
  första rad
- **När** delarna slås ihop
- **Så** står raden bara en gång, överst.
- **Givet** en rad som brutits vid sidslutet, så att en del står på
  vardera sidan
- **När** delarna slås ihop
- **Så** står delarna kvar som två rader; inga celler slås ihop.
- **Givet** två tabeller på varsin sida med löptext, en rubrik, en
  fotnot eller en summa emellan i sidans text, med olika kolumner, där
  den första slutar mitt på sidan, där någon av sidorna är läst med OCR,
  eller där bara den ena sidans tal är obekräftade
- **När** dokumentet konverteras
- **Så** förblir de två tabeller, som förut.
- **Givet** en rad i sidans översta eller nedersta tiondel som står på
  samma höjd på minst tre sidor, med samma text när siffrorna inte
  räknas
- **När** dokumentet konverteras
- **Så** räknas den som sidhuvud eller sidfot och skiljer inte två
  tabeller åt, också när den är en rubrik, en summa eller en fotnot.
- **Givet** en tabell som slagits ihop
- **När** datakontrollen körs (K11)
- **Så** prövas att varje sida i spannet finns och är läst ur textlagret,
  och att ingen annan tabell börjar inne i spannet eller har samma
  första sida och nummer.

## K20 — Konverteringen mäts mot ett facit

Issue: [#61](https://github.com/moggleif/kommunhandlingar/issues/61).
Urvalet, facits format och måtten står i
[Facit för konverteringen](03-ARKITEKTUR.md#facit-för-konverteringen).

- **Givet** ett urval av sidor ur riktiga handlingar med budget, bokslut,
  protokoll, en sida som bara är en bild, tabeller med och utan linjer och
  en tabell över två sidor, och ett facit för varje sida där tabellerna och
  talen är kontrollerade mot sidbilden
- **När** `python -m kommunhandlingar.facit` körs
- **Så** konverteras urvalet utan nät, och för varje dokument och totalt
  redovisas hur många tabeller som blev rätt, ofullständiga, märkta osäkra
  eller saknas utan märkning, hur många rader i CSV:erna som har tal som
  inte stämmer, hur många tabeller som inte finns i facit, hur många tal i
  text och tabeller som avviker på sidor med bekräftade tal, och hur många
  bildsidor som inte märkts.
- **Givet** en ändring av konverteringen
- **När** testerna körs
- **Så** stämmer måtten för poolens version med raden för den versionen i
  `matt.csv`. Ändrar en ändring måtten skrivs de om med `--spara` i samma
  ändring, och höjs versionen får den en egen rad, så att det syns om
  ändringen gjorde konverteringen bättre eller sämre.
- **Givet** urvalet
- **När** testerna körs
- **Så** prövas att varje tal i facits tabeller står bland sidans tal, att
  varje rad i en facittabell har lika många fält, och att utdragens
  textlager inte innehåller något som maskas enligt K17.

## K22 — Kommande sammanträden står i en kalender

Issue: [#106](https://github.com/moggleif/kommunhandlingar/issues/106).
Hur och varför står i
[ADR-0032](decisions/0032-kalendern-las-ur-besluten-och-skrivs-for-hand.md)
och [Kalendern](03-ARKITEKTUR.md#kalendern).

- **Givet** en kommun med en kalenderfil, där varje sammanträde har organ,
  datum och källa
- **När** webbplatsen byggs
- **Så** har kommunen en kalendersida, länkad från statussidan, med
  sammanträdena både som en månadsvy, där varje sammanträde är en ruta på
  sin dag, och som en lista för hela året.
- **Givet** kalendersidan
- **När** den visas
- **Så** öppnar månadsvyn på innevarande månad, listan börjar på dagens
  datum, och sammanträden före dagens datum går att se genom att bläddra
  bakåt i månadsvyn.
- **Givet** kalendersidan
- **När** besökaren väljer bort ett organ
- **Så** försvinner organets sammanträden ur båda vyerna. Från början visas
  alla organ.
- **Givet** ett sammanträde på kalendersidan
- **När** det visas
- **Så** står organets förkortning i rutan, med organets färg, där ett
  organ och organet det hör till har nyanser av samma färg; listan visar
  organets namn och tiden när källan anger den, och rutan platsen när
  källan anger den.
- **Givet** ett sammanträde vars datum är osäkert inläst
- **När** det visas
- **Så** är det märkt som osäkert i text i båda vyerna.
- **Givet** kalendersidan
- **När** den visas
- **Så** står överst en kort inledning och under den en hopfälld del om
  kvaliteten: hur många datum som är osäkra av alla, hur datumen tagits
  fram, varje osäkert sammanträde med skäl och källa, och källorna som
  länkar per organ och år.
- **Givet** en kalenderfil med ett organ som inte står i kommunfilen, ett
  datum som inte är ÅÅÅÅ-MM-DD eller inte finns, ett sammanträde två
  gånger, en källa som varken är en adress eller ett dokument i poolen,
  eller ett datum på en lördag eller söndag som inte är märkt osäkert,
  eller en kalenderfil utan kommunfil
- **När** webbplatsen byggs
- **Så** stoppas bygget med raden i felet.
- **Givet** en sida utan JavaScript
- **När** kalendersidan visas
- **Så** står alla sammanträden i båda vyerna, utan urval.
