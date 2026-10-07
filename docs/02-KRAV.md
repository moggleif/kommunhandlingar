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
- **Givet** en tabell som inte går att läsa säkert
- **Så** märks den som osäker i stället för att sparas som om den vore riktig:
  den blir ingen CSV, den står i Markdown märkt som osäker tabell, och
  sidan märks `tabell-osaker`. En tabell på en sida som lästs med OCR
  blir aldrig CSV, och sidan behåller sin OCR-märkning.

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
  `kallnyckel`, med samma `kalla_url` som upptäckten anger och utan
  kvalitet `ej-hamtad`
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
- **Så** uppdateras bara `kalla_url`, och texten konverteras inte om.

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
- **Så** körs datakontrollerna först, och bara om de går igenom når
  ändringen `main`, som en commit som bara rör filer under `data/`.

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
  vid lika värden i källnyckelns ordning.

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
- **Givet** en ändring på `main`
- **När** den har checkats in
- **Så** byggs webbplatsen om och publiceras på GitHub Pages, och varje
  sida säger när den byggdes.
- **Givet** en sida på webbplatsen
- **När** den visas
- **Så** har den samma meny, med startsidan och en statussida per kommun,
  och en sidfot som länkar till repot.
