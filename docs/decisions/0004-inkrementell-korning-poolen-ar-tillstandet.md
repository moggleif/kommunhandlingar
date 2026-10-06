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

* **Artig hämtning** (K10). En körning ska inte ladda ned tusentals filer,
  eller ens fråga om dem, när ingenting har ändrats.
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
det enda alternativet där en körning utan ändringar inte gör ett enda
anrop per dokument, och det klarar sig med det som front matter redan
innehåller.

Beslutet i detalj:

* **Poolen är tillståndet.** Ingen separat tillståndsfil. Körningen läser
  front matter i `data/<kommun>/` och slår upp varje kandidat på
  `kallnyckel`.
* **Samma källnyckel och samma `kalla_url` hämtas inte.** En ny
  källnyckel, en ny adress eller ett dokument med kvalitet `ej-hamtad`
  hämtas och konverteras. Därefter avgör sha256 enligt ADR-0003 om det är
  en ny version eller bara en ny adress.
* **En fil som byts ut under samma adress upptäcks inte.** Sitevision ger
  en ny tidsstämpel i adressen när filen byts ut, och en Wayback-kopia
  ändras aldrig. K9:s fall "under samma adress" stryks.
* **Upptäckten ger högst en kandidat per källnyckel.** Finns filen på flera
  adresser väljer adaptern den som gäller; annars skulle körningarna turas
  om att hämta varandras adresser.
* **Hämta och konvertera är ett steg, ett dokument i taget.** PDF:en hämtas
  till en temporär fil utanför repot och raderas när dokumentet är
  konverterat, även om konverteringen misslyckas.
* **`.md` skrivs sist och byter namn på plats.** Tabellerna skrivs först,
  sedan `.md` till en temporär fil som byter namn till den rätta. En
  avbruten körning lämnar alltså aldrig en halvskriven `.md`, och den
  körs bara om.
* **Ett misslyckat hämtningsförsök syns.** För ett dokument som inte finns
  i poolen skrivs en `.md` med kvalitet `ej-hamtad`, försökets tid och
  orsaken i `fel` (K6); den bär också dokumentets plats. Gäller försöket en
  ny adress för ett dokument som redan finns, lämnas dess `.md` orörd.
  Nästa körning försöker igen i båda fallen.

### Consequences

* Bra, eftersom en körning utan ändringar bara läser listningssidorna och
  front matter.
* Bra, eftersom det inte finns något tillstånd utanför datat som kan
  glida isär från det, och git-historiken visar även tillståndets historik.
* Bra, eftersom en avbruten körning inte behöver städas: inga PDF:er i
  repot, inga halvskrivna filer, och det som redan är skrivet hoppas över.
* Dåligt, eftersom en fil som kommunen byter ut under samma adress inte
  upptäcks. Ingen av Kungsbackas kända källor gör så, men det är ett
  antagande om källan.
* Dåligt, eftersom varje körning läser front matter i alla dokumentfiler;
  med några tusen små filer per kommun är det försumbart, men det växer.
* Neutralt, eftersom ett dokument som aldrig går att hämta (till exempel en
  Wayback-kopia som alltid är kapad) försöks igen vid varje körning.

### Confirmation

När koden kommer:

* Ett test visar att en kandidat med känd källnyckel och samma `kalla_url`
  inte hämtas, och att en ny källnyckel, en ny adress och ett dokument med
  `ej-hamtad` hämtas.
* Ett test visar att en körning som avbryts under konverteringen inte
  lämnar någon `.md` och ingen PDF, och att nästa körning skriver den.
* Ett test visar att ett misslyckat försök på ett nytt dokument ger en
  `.md` med `ej-hamtad`, och att ett misslyckat försök på en ny adress för
  ett befintligt dokument lämnar dess `.md` orörd.
* CI kontrollerar redan att inga binärer är incheckade (ADR-0001).

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
6. **Under skrivandet (Claude)** preciserades två saker: ett misslyckat
   försök på en ny adress får inte skriva över ett dokument som redan
   finns, och upptäckten får bara ge en kandidat per källnyckel, så att
   två adresser för samma fil inte hämtas om varannan gång.

### Vad som inte avgörs här

* Hur ny data checkas in, och hur ofta – issue #5. Det här beslutet gäller
  vad en körning gör, inte hur resultatet når `main`.
* Omkonvertering när verktygen byts ut, vilket kräver ny hämtning
  (ADR-0001) – issue #4.
* Vad som händer när en källnyckel som bara finns i `tidigare_kallnycklar`
  dyker upp igen – när adaptrarna skrivs, enligt ADR-0003.
* Vilken adress adaptern väljer när filen finns både live och i Wayback –
  när adaptrarna skrivs, som ADR-0003 redan säger.

### När beslutet bör omprövas

Om en källa visar sig byta ut filer under samma adress, eller om
körningarna behöver delas upp så att hämtning och konvertering sker på
olika ställen.
