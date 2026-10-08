# Källor: Kungsbacka kommun

> Webbplatsen (avsnitt 1 och sökfunktionen i avsnitt 4) är kontrollerad mot
> den levande sidan 2026-10-07
> ([#10](https://github.com/moggleif/kommunhandlingar/issues/10)). Det
> besvarar de punkter om Sitevision som ADR-0004 och ADR-0007 lämnade till
> #10. Wayback i avsnitt 2 är kontrollerat 2026-10-08
> ([#24](https://github.com/moggleif/kommunhandlingar/issues/24)).
> Avsnitt 3 bygger på anteckningarna i `moggleif/politik`
> (`data/KALLOR.md`, `scripts/hamta_fullmaktige.py`,
> `scripts/extrahera_utbud.py`) och är inte kontrollerat än: diariet,
> anslagstavlan och e-arkivet i
> [#23](https://github.com/moggleif/kommunhandlingar/issues/23).

## 1. Kommunens webbplats – nuvarande plattform (Sitevision)

### Organen och deras sidor

Mötessidorna ligger under
`https://kungsbacka.se/kommun-och-politik/politik-och-demokrati/politiska-moten-och-sammantraden/<sida>`,
en sida per organ. Organen, deras sidor och ordningen de hämtas i står i
[`kommuner/kungsbacka.toml`](../../kommuner/kungsbacka.toml)
([ADR-0008](../decisions/0008-kommunkonfigurationen-i-toml.md),
[ADR-0010](../decisions/0010-ordningen-organ-for-organ.md)).

Sidorna hade 2026-10-07 1 671 filer (unika nod-id:n), alla PDF utom ett
protokoll i Word-format (Valnämnden 2024-02-05, `.docx`).
Sidorna sparades samma kväll, då med 1 672 filer, och ligger som
fixturer i `tests/fixtures/sitevision/`.

Utan egen mötessida:

- **Gymnasium & Arbetsmarknads individutskott** nämns med sina
  mötesdatum på `namndernas-sammantraden`, men har inga dokument.
- **Krisledningsnämnden** sammanträder bara vid extraordinära händelser
  och har ingen mötessida.
- **Överförmyndarnämnden** är gemensam med Mölndal, Härryda, Partille och
  Öckerö; handlingarna publiceras av det gemensamma kontoret i Mölndal.
- **Bolagen** (Eksta Bostads AB, Stiftelsen Tjolöholm) har inga handlingar
  på kungsbacka.se.

Inga dokument finns heller på startsidan för mötena, på
`namndernas-sammantraden` (som listar årets planerade mötesdatum per
organ) och på `prenumerera-pa-handlingar-…`, eller på de två undersidorna
till fullmäktiges sida, `besok-kommunfullmaktige` och
`webbsandningar-fran-kommunfullmaktige`.

### Hur sidorna är byggda

- **Allt står i HTML:en från servern** och inget pagineras: alla år
  ligger på samma sida.
- Varje år är en rubrik `<h2>` "Kallelser, handlingar och protokoll från
  möten ÅÅÅÅ" och varje möte en `<h3>` "D månad ÅÅÅÅ".
- **Mötets filer står i en av två former.** De flesta ligger som länkar i
  Sitevisions filportlet (`sv-file-portlet`), med filnamnet följt av typ
  och storlek som länktext ("Pdf, 4.5 MB"). En del av mötena från juni
  2026 och senare har i stället en portlet som ritas i webbläsaren, och
  filerna står bara som JSON i HTML:en, i `AppRegistry.registerInitialState('12.…', {"files": […]})`:
  17 filer under nio möten 2026-10-07. Varje post har `id` (nod-id:t),
  `name`, `uri`, `url`, `fileSize`, `lastModifiedDateTime` och
  `lastModifiedBy`. En adapter som bara läser länkarna missar dem, så
  båda formerna måste läsas för varje möte.
- **`lastModifiedBy` pekar ut den som senast ändrat filen**, som ett
  internt användar-id ("255.…") 2026-10-07, och förs inte in i poolen.
  I de sparade sidorna i `tests/fixtures/` är det utbytt mot ett
  platshållar-id.
- **Tre redan hållna möten saknade filer** 2026-10-07, alla hos Tekniks
  arbetsutskott: 6 maj 2024, 12 januari 2026 och 10 augusti 2026.
- **Sidorna visar bara möten från januari 2024.** Varje sida börjar i
  januari eller februari 2024; äldre år ligger inte kvar, och
  sökfunktionen hittar inga protokoll från 2023. Om äldre år plockas bort
  varje år reds ut i #24.
- **`sitemap.xml`** pekar på `sitemapindex.xml` → `sitemap1.xml.gz`, med
  2 665 sidor men inga `/download/`-filer. Den räcker för att hitta
  mötessidorna, inte filerna.
- **Sitevisions REST-API** är stängt (`/rest-api/1/0/…` svarar 401).
- **`robots.txt`** stänger bland annat `/*?sv*`, `/*?start*`, `/*?date*`
  och `/*91.*`. Den sista träffar i dag ett protokoll,
  "Nämnden för Vård & Omsorg protokoll 2025-05-15, §§ 74, 76-91.pdf".
  Eftersom hämtningen följer `robots.txt` (K10) kan det inte hämtas, och
  syns som ej hämtat (K6) tills regeln eller filnamnet ändras.

### Adresser och versioner

- Dokumenten serveras som
  `https://kungsbacka.se/download/18.<nod-id>/<tidsstämpel-ms>/<filnamn>`.
  Nod-id:t är dokumentets källnyckel; adressen pekar bara ut en version
  ([ADR-0003](../decisions/0003-dokumentets-identitet-och-datamodell.md)).
- **Tidsstämpeln stämmer med filens `Last-Modified`.** Befolkningsprognosen
  `18.3ae5986a198e623c951df996` har tidsstämpeln `1782303262032`
  (2026-06-24 12:14:22 UTC), och svaret har `Last-Modified: Wed, 24 Jun
  2026 12:14:22 GMT`. JSON-postens `lastModifiedDateTime` skiljer sig
  bara ett par millisekunder från adressens tidsstämpel.
- **En gammal eller påhittad tidsstämpel ger 301** till den gällande
  adressen; den äldre `…/1756727320521/` och `…/1/` leder båda dit. Ett
  borttaget nod-id ger 404.
- **En fil byts ut på två sätt.** Antingen behåller den nod-id:t och får
  ny tidsstämpel (befolkningsprognosen), eller så laddas en ny fil upp och
  den gamla tas bort: handlingarna till Gymnasium & Arbetsmarknad
  2026-09-17 låg först på `18.5689acbf1a086271040226f9`, som nu ger 404,
  och ligger nu på `18.65c780211a0adcd46dd258bb` med "(1)" i namnet. Det
  första är en känd källnyckel med ny adress, det andra en ny källnyckel
  på en upptagen plats; båda regleras i ADR-0003, och
  [ADR-0004](../decisions/0004-inkrementell-korning-poolen-ar-tillstandet.md)
  bygger på att adressen ändras.
- **Antagande:** att en fil som byts ut under samma nod-id alltid får ny
  tidsstämpel. Det går inte att belägga utifrån. Inget fall av motsatsen
  har setts, och ADR-0004:s "upptäcks inte" gäller fortfarande.

### Filnamnen

Filnamnen skrivs för hand och bär organ, typ och datum, men utan fast form.

- **Grundformen** är "`<organ>` kallelse|handlingar|protokoll
  ÅÅÅÅ-MM-DD.pdf", till exempel "Kommunfullmäktige protokoll
  2026-08-11.pdf". Gymnasium & Arbetsmarknad skriver oftast "Kallelse för
  möte Nämnden för … den ÅÅÅÅ-MM-DD", Nämnden för Teknik och dess
  arbetsutskott ibland "… - Protokoll ÅÅÅÅ-MM-DD", och revisionen har
  "sammanträdesanteckningar" utöver protokoll.
- **Avvikelser som förekommer:** stavfel i organnamnet ("Byggnadsnämdens",
  "Ftitid", "Häsloskydd", "Omsog") och i typen ("potokoll"), datum som
  `240612`, `24-11-11` eller bara en månad, inget datum alls, ändelsen
  `.pdf.pdf`, och tillägg som "(1)", "_v2", "uppdaterad" och "pub".
- **Protokollet delas ofta i flera filer** per möte, med paragraferna i
  namnet ("§§ 1-11, 13-19" och "§ 12"). Kommunstyrelsens handlingar har
  delats per ärende en gång ("(Ärende 1)", "(Ärende 2-33)").
- **Mötessidorna har också andra dokument:** kommunbudget, årsredovisning
  och delårsrapport (fullmäktige), nämndbudget, särredovisning och
  avfallsföreskrifter (Teknik), och ett enskilt ärende (Tekniks
  arbetsutskott).

### Kända fel i källan

Rubriken och filnamnet är båda skrivna för hand och säger inte alltid
samma sak.

- **Datumen skiljer sig i ett tiotal möten** (minst ett filnamn med ett
  annat datum än mötets rubrik). En del är uppenbara fel: "22 januari
  2024" under rubriken för 2025 med filer daterade 2025-01-22, och "14 maj
  2024" med "protokoll 2025-05-14". Andra kan vara avsiktliga: revisionens
  anteckningar från ett möte ligger under nästa möte.
- **Filerna har hamnat under fel möte** hos Gymnasium & Arbetsmarknad:
  filerna från 2025-05-15 ligger både under "15 maj 2025" och under "24
  april 2025", och filerna från 2025-04-24 ligger bara under "27 mars
  2025". Mötet 27 mars 2025 har därmed inga egna filer på sidan.
- **Rubriker utan år** ("16 oktober", "21 augusti") och med tillägg ("5
  april 2024 (flyttat från 4 april)", "17 och 18 augusti 2026", "27-28
  januari 2025", "Extrainsatt sammanträde …", ", extra arbetsutskott").

Hur adaptern hanterar det står i
[ADR-0011](../decisions/0011-sitevision-organ-fran-sidan-datum-och-rattelser.md):
organet tas från sidan, datumet ur filnamnet eller rubriken, och när de
avviker gäller en rättelse i kommunfilen, belagd med datumet i kallelsen
eller protokollet.

### Dokumentens innehåll

- **Handlingarna är oftast en sammanslagen PDF per möte.** Ärendena
  (tjänsteskrivelser, bilagor) ligger efter varandra i samma fil.
  Kallelsen listar ärendena och är liten.
- **Storleken varierar kraftigt.** Enligt länktexterna och JSON-postens
  `fileSize` 2026-10-07 är hälften av de omkring 490 handlingsfilerna
  under 6,7 MB, men 36 är över 100 MB
  och den största 308,8 MB (Kommunstyrelsen 2025-04-22). De stora är
  kommunstyrelsens, dess arbetsutskotts och fullmäktiges. Fördelningen per
  organ och typ, och vad den betyder för ordningen, står i
  [ADR-0010](../decisions/0010-ordningen-organ-for-organ.md).
- **PDF:ernas form** (kontrollerat 2026-10-06 för
  [ADR-0005](../decisions/0005-konvertering-verktyg-ocr-och-kvalitet.md)):
  protokoll och tjänsteskrivelser har textlager. Handlingarna innehåller
  också skannade sidor – ifyllda blanketter utan textlager och
  motioner och interpellationer som redan fått ett OCR-lager. Tjänsteskrivelsernas
  tabeller är ritade med linjer; budgetens tabeller har bara vågräta
  linjer och färgade kolumner.
- Fullmäktige sänds och arkiveras som video (YouTube 2022–2024, Screen9 2024–),
  med kapitel per ärende och inlägg. Redan hämtat i politik-repot.

### Att tänka på vid hämtning

- Servern stänger ibland anslutningen utan att svara (curl: "Empty reply
  from server"). Ett nytt försök efter fem sekunder lyckades varje gång
  2026-10-07. Det hände också mitt i en hämtning av `robots.txt`.
  HTTP-klienten försöker igen (ADR-0013).

## 2. Internet Archive (Wayback)

Kontrollerat 2026-10-08 med Internet Archives CDX-tjänst
(`https://web.archive.org/cdx/search/cdx`), körd från GitHub Actions
([#24](https://github.com/moggleif/kommunhandlingar/issues/24)). Molnmiljön
som AI-agenten arbetar i når inte `web.archive.org` (anslutningen bryts);
Actions gör det, både CDX-listorna och hela kopior.

Webbplatsen har haft tre generationer, och dokumenten från alla tre finns
bara kvar i Wayback. Alla deras adresser ger 404 live.

| Generation | År | Adress till filerna | Form |
|---|---|---|---|
| Episerver, äldre | 2013–2017 | `www.kungsbacka.se/Global/Kommun och politik/Dokument/Möten, handlingar och protokoll/<organ>/<typ>/<år>/<fil>.pdf` | Dagordning, protokoll och handlingar per möte |
| Episerver, `globalassets` | 2017–2022 | `www.kungsbacka.se/globalassets/kommun-och-politik/dokument/moten-handlingar-och-protokoll/<organ>/<typ>/<år>/[<datum>/]<fil>.pdf` | Handlingarna **en PDF per ärende** |
| Sitevision | 2021 → | `kungsbacka.se/download/18.<nod-id>/<tidsstämpel>/<filnamn>` | Som i avsnitt 1 |

Organ och typ står i sökvägen i de två Episerver-generationerna, och i
filnamnet hos Sitevision. Organen hette annorlunda förr, och några finns
inte längre: Äldreomsorg, Funktionsstöd, Gymnasie och Vuxenutbildning,
Fritid och Folkhälsa, Kultur och Turism och Kommunstyrelsens
personalutskott.

### Mötessidorna visar bara tre år

Arkiverade kopior av Sitevision-sidorna i avsnitt 1, från april 2022 och
framåt, visar högst tre år: det innevarande och de två föregående. När
ett nytt år kommer till försvinner det äldsta från sidan. Det som
publicerats 2021–2023 hittas alltså bara via Wayback, och varje år faller
ett år till ur den levande källan.

### Täckning

Antal filer med minst en kopia som Wayback sparat som PDF (status 200),
per organ och år: `p` protokoll, `k` kallelse eller dagordning, `h`
handlingar. Tom ruta: ingen fil. Organ står som i källan: mappnamnet hos
Episerver och organets `id` i
[`kommuner/kungsbacka.toml`](../../kommuner/kungsbacka.toml) hos
Sitevision. Att en fil finns betyder inte att kopian är hel (se nedan).

**Episerver, äldre (2013–2017).** 1 072 filer. Utanför matrisen: 23 filer
som inte ligger i en mapp per typ och år, de flesta från Kommunstyrelsens
personalutskott 2014.

| organ | 2013 | 2014 | 2015 | 2016 | 2017 |
|---|---|---|---|---|---|
| Byggnadsnämnden | p6 k4 | p8 k7 | p2 k3 | p5 k9 | p9 k6 |
| Byggnadsnämndens arbetsutskott | p6 k5 | p12 k10 | p3 k2 | p2 k3 |  |
| Fritid och Folkhälsa | p4 k3 h1 | p5 k5 h2 | p3 k1 h2 | p3 k4 h2 |  |
| Funktionsstöd | p5 k5 | p13 k8 | p2 k2 |  |  |
| Förskola och Grundskola | p6 k7 | p7 k6 h6 | p2 k2 h2 | p2 k7 h1 | p5 k6 h5 |
| Förskola och Grundskola arbetsutskott | p2 k4 | p11 k14 h11 | p2 k3 h3 | p2 k2 h2 |  |
| Gymnasie och Vuxenutbildning | p4 k4 | p10 k1 h1 |  |  |  |
| Individ och Familjeomsorg | p5 k6 | p7 k6 h4 | p2 k1 | p3 k3 h4 |  |
| Kommunfullmäktige | p5 k5 | p9 k9 h18 | p1 k1 h1 | p1 k3 h2 | p4 k5 h16 |
| Kommunstyrelsen | p5 k4 h1 | p5 k5 h10 | p1 k2 h2 | p2 k3 h11 |  |
| Kommunstyrelsens arbetsutskott | p5 k13 h2 | p19 k22 h18 | p15 k4 h6 | p5 k22 h9 | p20 k18 h44 |
| Kultur och Turism | p4 k4 h1 | p4 k5 | p1 k1 h5 | p2 k5 h2 | p3 k3 h3 |
| Miljö och Hälsoskydd | p4 k4 | p7 k6 | p4 k2 | p4 k3 |  |
| Service | p4 k3 h2 | p3 k3 h1 | k1 h1 | p2 k2 h2 |  |
| Teknik | p15 | p9 k2 h2 | p4 k1 h2 | p2 k8 h5 | p6 k5 h7 |
| Tekniks arbetsutskott |  | p9 k3 h6 | p1 k2 h2 | p3 k6 h2 | p6 k6 h9 |
| Valnämnd | p4 k4 | p3 k3 h1 | p2 k2 h1 | p1 k1 h1 |  |
| Äldreomsorg | p6 k5 | p17 k13 h12 | p2 k3 h3 | p3 k10 h7 | p4 k4 h4 |
| Äldreomsorgens arbetsutskott |  |  |  |  | p1 k1 h1 |

**Episerver, `globalassets` (2017–2022).** Handlingarna är en fil per
ärende, därför de stora talen hos fullmäktige och kommunstyrelsen.

| organ | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 |
|---|---|---|---|---|---|---|
| byggnadsnamnden |  | k1 | p3 k3 | p3 | p16 k11 h2 | p4 k3 h2 |
| byggnadsnamndens-arbetsutskott | p15 k16 | p23 k22 | p16 k14 | p3 k2 | p5 k2 | p5 k4 h2 |
| forskola-och-grundskola |  | p1 |  | p9 k8 h13 | p13 h16 | p2 k2 |
| forskola-och-grundskola-arbetsutskott |  |  | p12 k7 h7 | h1 |  | p3 k1 |
| fritid-och-folkhalsa |  | p11 k11 h13 |  |  |  |  |
| gymnasium--arbetsmarknad |  | p8 k5 h7 |  | p1 | p14 k13 h14 |  |
| individ-och-familjeomsorg |  |  |  | p8 k4 h7 | p16 k9 h9 | p2 k1 h2 |
| kommunfullmaktige |  |  | p1 h1 | p1 | p10 k8 h96 | p2 k1 h2 |
| kommunstyrelsen |  | p18 k11 h254 | p19 k11 h229 | h2 | p13 k11 h116 | p1 k2 h3 |
| kommunstyrelsens-arbetsutskott |  |  | h2 | h5 | p31 k28 h107 | p7 k7 h7 |
| kultur-och-fritid |  |  | p8 k10 h16 | h2 | p10 k10 h11 | p2 k2 h2 |
| kultur-och-turism |  | h1 |  |  |  |  |
| miljo-och-halsoskydd |  |  |  | k1 | p2 k1 | p4 k3 h4 |
| service |  |  | h1 |  | p11 k10 h11 | p3 k2 h3 |
| teknik |  |  | k1 h1 | p12 k11 h12 | p9 k7 h9 | p3 k2 h2 |
| tekniks-arbetsutskott |  |  |  | p9 k9 | p4 | p2 k3 |
| valnamnd |  |  |  |  | p3 k3 h5 | k1 h1 |
| vard--omsorg |  |  | p11 k8 h9 | p4 k4 h5 | p8 k9 h9 |  |

**Sitevision (2021–2023).** Åren från 2024 finns på den levande sidan
(avsnitt 1). Utanför matrisen: 36 filer vars namn saknar organ, typ eller
fullständigt datum (till exempel `Protokoll 230920.signerad.pub.pdf`).
Deras organ och datum står bara på den arkiverade mötessidan.

| organ | 2021 | 2022 | 2023 |
|---|---|---|---|
| bygg | p16 k12 h2 | p3 k2 h2 |  |
| bygg-au | p22 k19 | p6 k5 h4 | p30 k21 h13 |
| fg | p9 k11 | p12 k11 h1 | p13 k10 h8 |
| fg-au | p10 k11 | p11 k11 | p10 k9 h7 |
| ga | p11 k11 h11 | p7 k5 h5 | p4 k3 h8 |
| ifo | p14 k9 h9 | p13 k9 h10 | p14 k10 h10 |
| kf | p10 k8 h8 | p10 k9 h10 | p10 k10 h10 |
| ks | p13 k11 h10 | p13 k11 h11 | p11 k10 h11 |
| ks-au | p30 k29 h30 | p19 k20 h18 | p30 k28 h27 |
| kultur | p7 k8 h7 | p2 k1 h2 | p10 k11 h11 |
| miljo | p16 k11 | p6 k5 h5 | p15 k11 h11 |
| revision | p15 | p21 | p22 |
| service | p10 k10 h10 | p11 k11 h11 | p11 k11 h10 |
| teknik | p11 k1 h9 | p6 k6 h5 | p13 k10 h10 |
| teknik-au |  | p2 | p9 |
| val | p3 k4 h4 | p7 k6 h6 | p4 k4 h4 |
| vo | p8 k9 h9 | p9 k9 h8 | p14 k10 h11 |

Åren 2021–2022 finns alltså både hos Episerver och Sitevision;
plattformarna låg parallellt en tid.

### Att tänka på vid hämtning

- **Kopior kapas tyst.** Samma fil kan ha flera kopior av olika storlek,
  till exempel fullmäktiges handlingar 2022-06-15: 59,8 MB i en kopia och
  1,0 MB i en annan. En kopia ska sluta på `%%EOF` och gå att öppna innan
  den godtas (K3, K6).
- Några kopior är sparade som 404-sidor (`text/html`) och räknas inte.
- Hela kopian hämtas med `https://web.archive.org/web/<tidsstämpel>id_/<adress>`;
  `id_` ger filen som den var, utan Waybacks ram.
- `archive.org` svarade 429 på upprepade anrop; `web.archive.org` bröt
  ibland anslutningen även från Actions (`Connection refused`), och nya
  försök med väntetid hjälpte.

## 3. Diariet – Ciceron (CGI)

**Belagt i politik-repot:**

- Öppet webbdiarium på `https://ciceronsok.kungsbacka.se`, ärenden från
  **2019-11-27**. Anslagstavla på `ciceronanslagstavla.kungsbacka.se`, e-arkiv
  på `arkiv.kungsbacka.se`.
- Ärenden har diarienummer `<ORGAN>-<ÅR>-<NR>` (t.ex. `KS 2023-00686`,
  `GA-2024-00194`), och handlingarna i ärendet kan ibland laddas ned.

Åtkomst, API, handlingstyper, anslagstavlan och e-arkivet kontrolleras i
#23.

## 4. Övrigt

- **Begäran om allmän handling** (`kommunarkivet@kungsbacka.se`) för det som
  saknas i alla digitala källor. Manuellt, men protokoll är alltid
  arkiverade och utlämnbara.
- Kommunens sökfunktion `/om-webbplatsen/sok?query=…&startAtHit=…` är
  serverrenderad och söker i PDF:ernas text, men hittar bara det som
  ligger på webbplatsen i dag.

## Täckning

| Period | Källa | Form |
|---|---|---|
| 2024-01 → | kungsbacka.se (Sitevision), kontrollerat | Oftast en PDF per möte och typ; protokoll ibland delat |
| 2021–2023 | Wayback av Sitevision | Som live; mötessidan visar bara tre år |
| 2017–2022 | Wayback av Episerver `globalassets` | En PDF per ärende |
| 2013–2017 | Wayback av äldre Episerver (`Global`) | Per möte |
| 2019-11 → | Ciceron | Per ärende, om nedladdning är öppen (#23) |
| äldre | Begäran hos kommunarkivet | Manuellt |
