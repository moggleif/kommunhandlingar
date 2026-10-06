---
status: accepted
date: 2026-10-06
decision-makers: Morgan
consulted: Claude
---

# Inkrementell körning: poolen är tillståndet och adressen är signalen

## Context and Problem Statement

K8 säger att en körning bara ska hämta och konvertera det som är nytt eller
ändrat, och att en avbruten körning ska fortsätta där den slutade
([#3](https://github.com/moggleif/kommunhandlingar/issues/3)). Men PDF:en
raderas efter konvertering (ADR-0001), så en ändring kan inte upptäckas
genom att jämföra sha256 utan att allt laddas ned igen – 10–30 GB per
körning och kommun.

Vad signalerar att ett dokument är nytt eller ändrat, var finns tillståndet
mellan körningarna, och var finns PDF:en mellan hämtning och konvertering
när den bara får vara tillfällig?

## Decision Drivers

* **Artig hämtning** (K10). En körning ska inte ladda ned tusentals filer
  när ingenting har ändrats.
* **Bara text** (ADR-0001). Inga PDF:er får ligga kvar i repot, inte ens
  efter en avbruten körning.
* **Identitet** (ADR-0003). Front matter bär redan `kallnyckel`,
  `kalla_url` och `sha256` för varje dokument.
* **Enkelhet.** Så få ställen som möjligt att hålla i takt.
* **Avbrytbarhet.** En körning som avbryts ska kunna startas om utan
  städning för hand.

## Considered Options

* A – Adressen per källnyckel är signalen, poolen är tillståndet, hämta
  och konvertera i ett steg per dokument
* B – Villkorade anrop (`ETag`/`Last-Modified`) för varje dokument
* C – Ladda ned allt varje körning och jämför sha256
* D – En separat tillståndsfil med en kö mellan stegen
* E – Listningssidornas innehåll som signal

## Decision Outcome

Valt alternativ: "A – Adressen per källnyckel är signalen", eftersom det är
det enda alternativet där en körning utan ändringar inte gör något anrop
per dokument, utom för det som misslyckats tidigare, och det klarar sig
med det som front matter redan innehåller.

Beslutet i detalj (kraven står i K6, K8 och K9):

* **Poolen är tillståndet.** Ingen separat tillståndsfil. Körningen läser
  front matter i `data/<kommun>/` och slår upp varje kandidat på
  `kallnyckel` och `tidigare_kallnycklar`.
* **Samma källnyckel och samma `kalla_url` hämtas inte.** En ny
  källnyckel, en ny adress eller ett dokument med kvalitet `ej-hamtad`
  hämtas och konverteras. Därefter avgör sha256 enligt ADR-0003 om det är
  en ny version eller bara en ny adress.
* **Det som ADR-0003 redan avgjort hämtas inte.** En källnyckel i
  `tidigare_kallnycklar` är samma dokument och ersätter inte den nyare
  nyckeln. En kopia från en ögonblicksbild tagen före `hamtad` kan inte
  vara en nyare version, utom när dokumentet har `ej-hamtad` och alltså
  ingen version alls.
* **En fil som byts ut under samma adress upptäcks inte.** Sitevision ger
  en ny tidsstämpel i adressen när filen byts ut, och en Wayback-kopia
  ändras aldrig. Att det alltid är så för Sitevision, och hur övriga
  källor beter sig, är inte kontrollerat än (#10). K9:s fall "under samma
  adress" stryks.
* **Upptäckten ger högst en kandidat per källnyckel,** i samma form varje
  gång. Finns filen på flera adresser väljer adaptern den som gäller;
  annars skulle körningarna turas om att hämta varandras adresser.
* **Hämta och konvertera är ett steg, ett dokument i taget.** PDF:en hämtas
  till en temporär fil utanför repot och raderas när dokumentet är
  konverterat, även om konverteringen misslyckas.
* **Tabellerna först, `.md` sist.** Tabellkatalogen ersätts som helhet och
  `.md` skrivs till en temporär fil som byter namn till den rätta. En
  avbruten körning kan lämna nya tabeller bredvid en gammal `.md`, men
  aldrig en halvskriven `.md`; eftersom `kalla_url` i den gamla `.md` inte
  ändrats gör nästa körning om dokumentet.
* **Ett misslyckat hämtningsförsök syns, men tar aldrig bort text.** Har
  dokumentet ingen `.md` skrivs en med kvalitet `ej-hamtad`, tid för
  försöket och orsaken i `fel` (K6); den bär också dokumentets plats. Finns
  en `.md` lämnas den orörd. Nästa körning försöker igen, och misslyckas
  den av samma orsak skrivs ingenting.
* **Härkomsten för ett dokument som inte gick att hämta** är källänken,
  källnyckeln, tiden för försöket och orsaken. Det finns ingen sha256 att
  ange. Det smalnar av ADR-0001:s Confirmation ("varje `.md` har sha256"),
  och regeln i AGENTS.md säger nu detsamma.
* **En ny version som inte går att konvertera** skriver ändå över den
  gamla (K9). Den nya sha256 och `kalla_url` står i filen, så den hämtas
  inte om i onödan, och git-historiken behåller den gamla texten.

### Consequences

* Bra, eftersom en körning utan ändringar bara läser listningssidorna och
  front matter, och inte ger några diffar.
* Bra, eftersom det inte finns något tillstånd utanför datat som kan
  glida isär från det, och git-historiken visar även tillståndets historik.
* Bra, eftersom en avbruten körning inte behöver städas: inga PDF:er i
  repot, ingen halvskriven `.md`, och nästa körning gör färdigt.
* Dåligt, eftersom en fil som kommunen byter ut under samma adress inte
  upptäcks. Det är ett antagande om källorna som ska kontrolleras (#10).
* Dåligt, eftersom en avbruten körning kan lämna nya tabeller bredvid en
  gammal `.md` tills nästa körning är klar; att bara checka in färdiga
  körningar hör till #5.
* Dåligt, eftersom ett byte av adress utan ändrat innehåll, till exempel
  när adaptern går över från den levande sidan till Wayback, ger en ny
  hämtning och en ändrad `kalla_url`.
* Dåligt, eftersom varje körning läser front matter i alla dokumentfiler;
  med några tusen små filer per kommun är det försumbart, men det växer.
* Neutralt, eftersom ett dokument som aldrig går att hämta (till exempel en
  Wayback-kopia som alltid är kapad) försöks igen vid varje körning.

### Confirmation

När koden kommer, ett test för varje fall i K8 och för:

* att en kandidat med känd källnyckel och samma `kalla_url` inte hämtas,
  och att en ny källnyckel, en ny adress och ett dokument med `ej-hamtad`
  hämtas,
* att en källnyckel i `tidigare_kallnycklar` och en äldre ögonblicksbild
  inte hämtas,
* att upptäckten ger högst en kandidat per källnyckel,
* att en körning som avbryts under konverteringen, eller mellan
  tabellerna och `.md`, inte lämnar någon PDF och ingen halvskriven `.md`,
  och att nästa körning gör färdigt dokumentet utan kvarlämnade tabeller,
* att ett misslyckat försök på ett nytt dokument ger en `.md` med
  `ej-hamtad`, att ett misslyckat försök aldrig skriver över en befintlig
  `.md`, och att ett nytt försök med samma orsak inte ändrar något,
* att ett dokument med `ej-hamtad` som nu går att hämta blir en
  fullständig `.md` på samma sökväg.

CI kontrollerar redan att inga binärer är incheckade (ADR-0001). När
härkomstkontrollen kommer undantar den `sha256` och `konverterad` för
`ej-hamtad`.

## Pros and Cons of the Options

### A – Adressen per källnyckel är signalen, poolen är tillståndet, hämta och konvertera i ett steg per dokument

* Bra, eftersom ingenting hämtas när ingenting ändrats.
* Bra, eftersom tillståndet redan finns i front matter (ADR-0003).
* Bra, eftersom PDF:en finns kvar så kort tid som möjligt.
* Dåligt, eftersom en fil som byts ut under samma adress inte upptäcks.
* Dåligt, eftersom hämtning och konvertering inte kan köras var för sig,
  till exempel på olika maskiner.

### B – Villkorade anrop (`ETag`/`Last-Modified`) för varje dokument

`ETag` och `Last-Modified` sparas i front matter och skickas tillbaka som
`If-None-Match`/`If-Modified-Since`.

* Bra, eftersom även en fil som byts ut under samma adress upptäcks.
* Dåligt, eftersom varje körning gör ett anrop per dokument; med det
  konfigurerade avståndet mellan anropen tar tusentals dokument timmar,
  även när ingenting ändrats.
* Dåligt, eftersom det beror på att servern skickar validerare, vilket
  inte är kontrollerat för någon av Kungsbackas källor.

### C – Ladda ned allt varje körning och jämför sha256

* Bra, eftersom varje ändring upptäcks, oavsett adress.
* Dåligt, eftersom det är 10–30 GB per körning och kommun – det motsatta
  av artig hämtning.

### D – En separat tillståndsfil med en kö mellan stegen

En JSON- eller SQLite-fil i repot med vad som hämtats, när och svaret, och
en kö med hämtade PDF:er som väntar på konvertering.

* Bra, eftersom hämtning och konvertering kan köras som separata
  kommandon, och svaren från servern sparas.
* Dåligt, eftersom tillståndet då finns på två ställen, i filen och i
  front matter, som kan glida isär.
* Dåligt, eftersom en kö med PDF:er mellan stegen gör att PDF:er kan ligga
  kvar efter en avbruten körning.

### E – Listningssidornas innehåll som signal

En hash av varje listningssida sparas; bara sidor som ändrats läses vidare.

* Bra, eftersom oförändrade organ hoppas över helt.
* Dåligt, eftersom sidorna ändras av annat än dokumenten (menyer,
  nyheter), så signalen blir brusig.
* Dåligt, eftersom det inte säger vilket dokument som ändrats; jämförelsen
  per källnyckel behövs ändå.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Problemet (issue #3).** K8 gick inte att uppfylla som det stod, eftersom
   PDF:en raderas och sha256 inte kan jämföras utan ny nedladdning.
2. **Iakttagelsen (Claude).** Efter ADR-0003 bär front matter redan
   `kallnyckel`, `kalla_url` och `sha256`. Poolen kan då vara sitt eget
   tillstånd, och en körning jämför det upptäckten hittar med det som står
   i filerna.
3. **Tre frågor till Morgan, med Claudes rekommendation:**
   * Vad räknas som en ändring: adressen per källnyckel (Claude
     rekommenderade det), villkorade anrop (B) eller allt nedladdat (C).
     Claude pekade på att Sitevision ger ny tidsstämpel när en fil byts ut
     och att Wayback-kopior aldrig ändras.
   * Ska en fil som byts ut under samma adress upptäckas: nej för nu
     (Claude), eftersom ingen av Kungsbackas kända källor gör så. Frågan
     tas upp igen om kartläggningen av källorna
     ([#10](https://github.com/moggleif/kommunhandlingar/issues/10)) visar
     en källa som beter sig så.
   * Var finns PDF:en mellan stegen: hämta och konvertera som ett steg per
     dokument (Claude), en gemensam temporär katalog för körningen, eller
     en tillståndsfil med kö (D).
4. **En följd som Claude lade till:** ett dokument som inte gick att
   hämta behöver också en `.md`, annars minns ingenting försöket.
5. **Morgan sa ja** till alla rekommendationerna 2026-10-06.
6. **Under skrivandet (Claude)** preciserades att ett misslyckat försök
   på en ny adress inte får skriva över ett dokument som redan finns, och
   att upptäckten bara får ge en kandidat per källnyckel, så att två
   adresser för samma fil inte hämtas om varannan gång.
7. **Granskningen (fas 6)** visade att reglerna inte täckte allt som
   ADR-0003 redan bestämt. Claude lade till att en källnyckel i
   `tidigare_kallnycklar` och en äldre Wayback-kopia inte hämtas, vad som
   händer när ett dokument med `ej-hamtad` till sist går att hämta och när
   en ny version inte går att konvertera, att tabellkatalogen ersätts som
   helhet, att ett misslyckat försök aldrig skriver över en befintlig
   `.md` och inte skriver om sig själv, och att härkomsten för ett
   dokument utan original är försöket – vilket AGENTS.md nu säger.

### Vad som inte avgörs här

* Hur ny data checkas in, och hur ofta – issue #5. Det här beslutet gäller
  vad en körning gör, inte hur resultatet når `main`.
* Omkonvertering när verktygen byts ut, vilket kräver ny hämtning
  (ADR-0001) – issue #4.
* Vilken adress adaptern väljer när filen finns både live och i Wayback –
  när adaptrarna skrivs, som ADR-0003 redan säger.
* En fil som länkas från flera sammanträden är ett dokument på en plats
  (ADR-0003). Om det andra sammanträdet ska visa att dokumentet finns
  avgörs när adaptrarna och luckorna (K7) skrivs.

### När beslutet bör omprövas

Om en källa visar sig byta ut filer under samma adress, eller om
körningarna behöver delas upp så att hämtning och konvertering sker på
olika ställen.
