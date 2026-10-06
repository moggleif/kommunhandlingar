# ADR-0001: Var datapoolen ska bo – repo och lagring

- Status: **Accepterad** (2026-10-06)
- Datum: 2026-10-06
- Beslutsfattare: Morgan

## Sammanhang

Datapoolen ska hämta alla kallelser, handlingar och protokoll från KF, KS och
samtliga nämnder i Kungsbacka, så långt bakåt som möjligt, konvertera dem till
Markdown och CSV och bygga ett index som analyser kan stå på. Den ska gå att
återanvända för andra kommuner.

Faktorer som styr valet:

1. **Volym.** Ungefär 12 organ × 10 möten om året × (handlingar 3–33 MB +
   protokoll + kallelse) ger 1–3 GB PDF per år och kommun. Med tio års
   historik blir det 10–30 GB. Den härledda texten (Markdown, CSV, index) är
   ungefär 1–5 % av det, alltså några hundra MB.
2. **GitHubs gränser.** Max 100 MB per fil, rekommenderat under 1 GB och hård
   varning runt 5 GB per repo. Git LFS ingår med 1 GB lagring och 1 GB
   bandbredd i månaden; mer kostar.
3. **`moggleif/politik` har egna regler.** Det är en statisk webbplats som
   bara använder standardbiblioteket för hämtning och bygge, där allt i
   `data/` ska kunna byggas om av ett skript och där CI kör facit mot sidorna.
   Poolen behöver PDF-, OCR- och tabellverktyg (tunga beroenden) och
   nattliga körningar.
4. **Generalitet.** Poolen ska vara kommunoberoende; politik-repot handlar om
   Kungsbacka (och Varberg).
5. **Personuppgifter.** Fulltexten kan innehålla uppgifter om enskilda
   (en egen ADR senare). Var datat bor avgör hur lätt det är att hålla det privat.

Gemensamt för alla alternativ nedan: originalen identifieras med sin SHA-256,
och koden, konfigurationen och ADR:erna versioneras i git.

---

## Alternativ A – Nytt kodrepo, originalen i objektlagring, texten i releaser

```
github.com/<ägare>/datapool          kod, kommuner/*.yaml, docs/adr/, issues
objektlagring (R2 / B2 / S3)         ra/<sha256>.pdf
GitHub Releases i datapool           text-<datum>.tar.zst, index.sqlite, *.parquet
```

**Fördelar**
- Kodrepot är litet, går att göra publikt och klonas på sekunder.
- Originalen skalar fritt; R2 har ingen avgift för utgående trafik.
- Releaser är en tydlig "ögonblicksbild" som analyser kan peka på.

**Nackdelar**
- Texten går inte att diffa eller bläddra i på GitHub; man laddar ned
  ett paket.
- Kräver ett konto för objektlagring och hemligheter i CI.
- Release-tillgångar är max 2 GB per fil.

**Kostnad:** ~30 GB i R2 ≈ 0,45 USD/månad.

## Alternativ B – Två nya repon (kod + text), originalen i objektlagring

```
github.com/<ägare>/datapool          kod, konfiguration, ADR, issues
github.com/<ägare>/datapool-data     text/**.md, text/**.csv, index-export
objektlagring (R2 / B2 / S3)         ra/<sha256>.pdf
```

**Fördelar**
- Texten är bläddringsbar, sökbar och **diffbar** på GitHub: man ser exakt
  vad som ändrats mellan två körningar, och git-historiken blir i sig ett
  register över när kommunen ändrade en handling.
- Datarepot kan vara **privat** medan kodrepot är publikt – enkelt sätt att
  hantera personuppgiftsfrågan.
- Andra projekt (politik-repot, analyser) kan använda datarepot som
  undermodul eller bara klona det.

**Nackdelar**
- Två repon att hålla i takt; CI i kodrepot måste ha skrivrätt i datarepot.
- Datarepot växer med åren (några hundra MB, sedan mer med fler kommuner);
  hanterbart, men det får delas per kommun på sikt.
- Fortfarande ett konto för objektlagring.

**Kostnad:** som A.

## Alternativ C – Allt i politik-repot

```
github.com/moggleif/politik
  datapool/            kod och konfiguration
  datapool/text/       härledd text
  (originalen i objektlagring eller lokalt, inte i git)
```

**Fördelar**
- Inget nytt repo; nära de sidor som först ska använda datat.
- En plats för issues och historik.

**Nackdelar**
- Krockar med repots regler: beroenden, CI som kör facit och
  tillgänglighetskontroller vid varje ändring, och kravet att allt i `data/`
  ska byggas om av ett skript.
- Repot har GitHub Pages; text och index i samma repo gör kloner och
  Pages-byggen långsamma.
- Svårt att hålla fulltexten privat när webbplatsrepot är publikt.
- Säger "Kungsbacka" på varje nivå; generaliteten blir en
  intentionsförklaring snarare än en struktur.

**Kostnad:** som A för originalen.

## Alternativ D – Nytt kodrepo + Hugging Face-dataset för allt data

```
github.com/<ägare>/datapool                     kod, konfiguration, ADR, issues
huggingface.co/datasets/<ägare>/kommunhandlingar   ra/, text/, index/*.parquet
```

**Fördelar**
- Ett ställe för originalen **och** texten, gjort för stora dataset:
  git-baserat med inbyggd stor-fil-lagring, gratis för publika dataset och
  privata upp till en kvot.
- Parquet-filerna får automatiskt en förhandsvisning och kan läsas direkt
  av DuckDB, pandas och `datasets` via `hf://`.
- Inget separat konto för objektlagring.

**Nackdelar**
- Ytterligare en plattform med egna villkor; privata dataset har en
  lagringsgräns.
- Mer sårbart om plattformens villkor eller prissättning ändras.
- Publiceringsmiljön är gjord för ML-dataset; personuppgiftsfrågan måste
  vara löst innan något görs publikt där.

**Kostnad:** 0 kr för publikt; privat inom gratiskvoten eller med
Pro-konto.

## Alternativ E – Allt i ett nytt repo med Git LFS

```
github.com/<ägare>/datapool          kod + text i git, originalen i LFS
```

**Fördelar**
- Ett repo, en klon, inget externt konto.

**Nackdelar**
- 30 GB i LFS kostar och varje CI-körning som checkar ut LFS-filer äter
  bandbredd; kvoten tar slut snabbt.
- Svårt att bli av med LFS senare.

Med som jämförelse; rekommenderas inte.

---

## Alternativ F – Ett repo, bara text: PDF:en raderas efter konvertering

```
github.com/<ägare>/datapool
  src/, kommuner/*.yaml, docs/adr/          kod och konfiguration
  text/<kommun>/<organ>/<år>/<datum>/<typ>.md   + tabeller som .csv
  index/                                     liten SQLite eller JSONL
```

PDF:en hämtas till en tillfällig katalog, konverteras och raderas. Överst i
varje Markdown-fil står en front matter med allt som behövs för att hitta
tillbaka till originalet:

```yaml
---
kalla_url: https://kungsbacka.se/download/18.4ac81f…/1761285111298/Protokoll….pdf
arkiv_url: https://web.archive.org/web/20261006…/https://kungsbacka.se/download/…
sha256: 3f9a…            # originalets fingeravtryck
bytes: 812345
sidor: 14
hamtad: 2026-10-06T15:40:12+02:00
konverterad: 2026-10-06T15:40:31+02:00
pipeline: datapool 0.3 / docling 2.x / tesseract 5.x
ocr: false
kvalitet: full          # full | text-utan-tabeller | ocr | delvis | ej-konverterad
kvalitet_per_sida: [ok, ok, ok, ocr, ok, tabell-osaker, …]
kommun: kungsbacka
organ: ga
datum: 2025-10-16
typ: protokoll
---
```

**Fördelar**
- **Ett repo och inget externt konto.** Texten är några hundra MB för tio
  års historik, väl inom GitHubs gränser.
- Allt är diffbart och sökbart på GitHub, och git-historiken blir ett
  register över vad kommunen ändrat.
- Enklast att förstå, köra och bidra till.

**Nackdelar och risker**
- **Konverteringen kan inte göras om utan att hämta igen.** Blir
  PDF-verktygen bättre (de blir det, särskilt för tabeller och inskannat)
  måste originalen hämtas på nytt – och kommunen visar bara ~2 år bakåt.
  Det gamla materialet kommer från Wayback, som är ostadigt.
- **Ett fel i konverteringen upptäcks kanske först senare**, när originalet
  inte längre finns hos kommunen.
- Kod och text i samma repo: antingen är båda publika eller båda privata
  (personuppgiftsfrågan får en egen ADR senare).
- Repot växer för varje kommun; vid fler kommuner kan texten behöva brytas
  ut till ett eget repo per kommun (det är en enkel flytt senare).

**Skydd som gör F hållbart**
1. **Källänk och sha256 i varje fil**, så att originalet går att leta upp
   igen. Som extra hjälp (inget krav) arkiveras originalet i Internet
   Archive vid hämtning: "Save Page Now"
   anropas för PDF-adressen och `arkiv_url` skrivs in i front matter. Då
   finns originalet kvar hos en tredje part när kommunen tar bort det, och
   `sha256` visar att det är samma fil. Det räcker för de två saker
   originalet behövs till: konvertera om när verktygen blivit bättre, och
   belägga en siffra som ifrågasätts.
2. **Kvalitet i varje fil.** Front matter anger konverteringens nivå
   (`full`, `text-utan-tabeller`, `ocr`, `delvis`, `ej-konverterad`) och en
   bedömning per sida. Även ett dokument som inte gick att konvertera får en
   Markdown-fil med metadata och status, så att luckan syns i datat i
   stället för att bara saknas.
3. **Konvertera strikt** – osäkra tabeller märks som osäkra i stället för
   att sparas som om de vore riktiga, i linje med politik-repots regel
   "hellre stanna än spara siffror som inte går ihop".

Inga PDF:er lagras av projektet självt.

**Kostnad:** 0 kr.

## Jämförelse

| | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| Texten diffbar på GitHub | – | ✔ | ✔ | delvis | ✔ | ✔ |
| Text privat, kod publik | ✔ | ✔ | – | ✔ | – | – |
| Kommunoberoende struktur | ✔ | ✔ | – | ✔ | ✔ | ✔ |
| Antal ställen att sköta | 2 | 3 | 1–2 | 2 | 1 | 1 |
| Skalar till fler kommuner | ✔ | ✔ (dela per kommun) | – | ✔ | – | ✔ (bryt ut text senare) |
| Externt konto behövs | ja | ja | ja | HF | nej | nej |
| Konvertera om utan ny hämtning | ✔ | ✔ | ✔ | ✔ | ✔ | bara via Wayback-kopian |

## Diskussion

Hur resonemanget gick, i ordning, så att valet går att förstå i efterhand.

**1. Första förslaget: kod och data isär.** Utgångspunkten var att poolen
blir 10–30 GB PDF med tio års historik, vilket inte ryms i git. Därför togs
alternativ A–E fram, som alla sparar originalen någonstans: objektlagring,
Hugging Face eller Git LFS. Claude rekommenderade B (ett kodrepo, ett textrepo,
PDF:er i objektlagring).

**2. Morgan: varför spara PDF:erna alls?** Hämta PDF:en tillfälligt,
konvertera, skriv källänk och datum för hämtning och konvertering överst i
Markdown-filen och radera PDF:en. Då återstår bara text, och ett enda repo
räcker. Det blev alternativ F.

**3. Invändning: konvertering kan behöva göras om.** OCR och
tabelltolkning blir bättre, och kommunen visar bara ~2 år bakåt. Först
föreslogs att osäkra PDF:er (inskannat, trasiga tabeller) skulle sparas
tills vidare, och att varje original skulle arkiveras i Internet Archive.

**4. Morgan: det som inte går att konvertera går inte att använda som
data.** Det som behövs är att varje Markdown-fil anger *hur väl*
konverteringen lyckades. Vad ska originalet då vara till?

**5. Svar: originalet har två användningar.** Att konvertera om när
verktygen blivit bättre, och att kunna belägga en siffra som ifrågasätts.
Båda klaras med en länk till originalet och dess sha256 – vi behöver inte
lagra filen själva. Skyddet "spara osäkra PDF:er" ströks. Kvalitetsnivån
(per dokument och per sida) lades in i front matter, och även dokument som
inte gick att konvertera får en Markdown-fil så att luckan syns.

**6. Överenskommet: konvertera om senare = leta upp filen igen senare.**
Behöver ett dokument konverteras om, hämtas originalet på nytt där det då
går att hitta – kommunens webbplats, Internet Archive, diariet eller genom
en begäran om allmän handling. Projektet lagrar inga PDF:er. Att be
Internet Archive spara filen vid hämtning är ett billigt sätt att göra det
troligare att den går att hitta, men det är inget krav för att F ska
fungera.

**Vad diskussionen avgjorde och inte avgjorde**
- Avgjort: datat är texten, inte PDF:erna. Det gör att alternativen som
  finns till för att lagra originalen (A, B, D, E) löser ett problem som vi
  har valt att inte ha.
- Inte avgjort: om kod och text ska vara publika eller privata. Kräver texten att vara privat medan koden är öppen talar det
  för två repon, men det är en fråga om synlighet, inte om lagring.

## Rekommendation (från Claude)

*Rekommendationen är skriven av Claude, inte av beslutsfattaren.*

**F.** Datat är texten, och ett repo utan externa konton är det enklaste
som håller. Kvalitetsnivån i varje fil gör det tydligt vad som går att
använda, och källänk plus sha256 räcker för att leta upp originalet igen
när något behöver konverteras om eller beläggas.

**B** är bara aktuellt om fulltexten måste vara privat medan koden är
öppen. Den frågan får en egen ADR senare.

## Beslut

Morgan valde **alternativ F** 2026-10-06: ett nytt, eget repo med kod,
konfiguration, ADR:er och den konverterade texten. PDF:erna hämtas
tillfälligt, konverteras och raderas. Varje Markdown-fil bär källänk,
sha256, tidpunkter för hämtning och konvertering samt konverteringens
kvalitet.

## Konsekvenser

- Ett repo, inga externa konton.
- Behöver ett dokument konverteras om, hämtas originalet på nytt där det
  då går att hitta.
- Kod och text har samma synlighet (publikt eller privat); det avgörs i en
  senare ADR om personuppgifter.
- `moggleif/politik` byggs inte vidare för poolen. Det som går att
  återanvända därifrån kopieras in och anpassas (se README för vad).
