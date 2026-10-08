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
  kandidatlista skrivs.

## K3 — Historiken hämtas så långt bakåt den finns

- **Givet** att kommunens webbplats bara visar de senaste åren
- **När** upptäckten körs
- **Så** prövas också de äldre källor konfigurationen anger (t.ex. Internet
  Archive och kommunens diarium), och varje dokument registreras med den
  källa det hittades i.

## K4 — Varje dokument blir en Markdown-fil med härkomst

- **Givet** ett hämtat PDF-dokument
- **När** det konverteras
- **Så** skrivs en `.md` vars front matter anger varifrån originalet
  kom, vilket original det var, när det hämtades och konverterades, med
  vilka verktyg och med vilken kvalitet – och PDF:en raderas. Fälten står
  i [Front matter](03-ARKITEKTUR.md#front-matter).

## K5 — Tabeller blir CSV

- **Givet** ett dokument med tabeller
- **När** det konverteras
- **Så** skrivs varje tabell som går att läsa säkert som en CSV-fil
  bredvid dokumentets `.md`, med sidnummer, och tabellen syns också i
  Markdown-texten. Varje CSV går att föra tillbaka till sitt dokument,
  och därmed till dokumentets härkomst.
- **Givet** en tabell utan lodräta linjer, där varje rad är en etikett
  följd av tal och talen står i linje i kolumner
- **Så** går den att läsa säkert och blir CSV som en tabell med linjer.
  Rubrikraderna ovanför följer med när varje rubrik står i linje med sin
  kolumn; annars står de kvar i texten.
- **Givet** en tabell med linjer där en cell rymmer mer än ett tal
- **Så** går den inte att läsa säkert med linjerna som cellgränser. Det
  som inte går att läsa som en tabell utan lodräta linjer står kvar i
  sidans text, och står en siffra ur tabellen där märks sidan
  `tabell-osaker`.
- **Givet** en tabell som inte går att läsa säkert
- **Så** märks den som osäker i stället för att sparas som om den vore riktig:
  den blir ingen CSV, och sidan märks `tabell-osaker`. Står den i texten
  som rader med flera tal står den i Markdown märkt som osäker tabell.
  En tabell på en sida som lästs med OCR blir aldrig CSV, och sidan
  behåller sin OCR-märkning.

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

- **Givet** ett sammanträde som vi vet har hållits
- **När** ett av dess dokument inte hittas i någon källa
- **Så** registreras det som saknat, med vilka källor som prövats och när.

## K8 — Körningen är inkrementell och kan avbrytas

- **Givet** att en källnyckel redan finns i poolen som ett dokuments
  `kallnyckel`, med samma `kalla_url` som upptäckten anger, utan
  kvalitet `ej-hamtad` och med den version av poolen som körs i
  `pipeline`
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

- **Givet** ett fullständigt dokument vars `pipeline` har en annan version
  av poolen än den som körs, och en kandidat med samma källnyckel och
  samma `kalla_url`
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
  inte dokumentets `pipeline` har en annan version av poolen än den som
  körs; då konverteras det om som i K8.

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
- **Så** står dokumentets `.md` och tabeller kvar orörda, också när
  dokumentet har kvalitet `ej-hamtad`.

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
