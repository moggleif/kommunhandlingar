# Källor: Kungsbacka kommun

> Webbplatsen (avsnitt 1) är kontrollerad mot den levande sidan 2026-10-07
> ([#10](https://github.com/moggleif/kommunhandlingar/issues/10)). Övrigt
> bygger på anteckningarna i `moggleif/politik` (`data/KALLOR.md`,
> `scripts/hamta_fullmaktige.py`, `scripts/extrahera_utbud.py`) och är inte
> kontrollerat än: diariet, anslagstavlan och e-arkivet i
> [#23](https://github.com/moggleif/kommunhandlingar/issues/23), Wayback i
> [#24](https://github.com/moggleif/kommunhandlingar/issues/24).

## 1. Kommunens webbplats – nuvarande plattform (Sitevision)

### Organen och deras sidor

Mötessidorna ligger under
`https://kungsbacka.se/kommun-och-politik/politik-och-demokrati/politiska-moten-och-sammantraden/<sida>`.
Listan flyttas till `kommuner/kungsbacka.toml` när den skrivs
([ADR-0008](../decisions/0008-kommunkonfigurationen-i-toml.md),
[#25](https://github.com/moggleif/kommunhandlingar/issues/25)).

| Organ | `<sida>` | Filer | Första möte |
|---|---|---:|---|
| Kommunfullmäktige | `kommunfullmaktiges-sammantraden` | 81 | 2024-02-06 |
| Kommunstyrelsen | `kommunstyrelsens-sammantraden` | 92 | 2024-01-23 |
| Kommunstyrelsens arbetsutskott | `kommunstyrelsens-arbetsutskotts-sammantraden` | 233 | 2024-01-09 |
| Byggnadsnämnden | `byggnadsnamndens-sammantraden` | 107 | 2024-01-18 |
| Byggnadsnämndens arbetsutskott | `byggnadsnamndens-arbetsutskotts-sammantraden` | 121 | 2024-02-01 |
| Nämnden för Förskola & Grundskola | `forskola--grundskolas-sammantraden` | 94 | 2024-01-17 |
| Förskola & Grundskolas arbetsutskott | `forskola--grundskolas-arbetsutskotts-sammantraden` | 90 | 2024-01-10 |
| Nämnden för Gymnasium & Arbetsmarknad | `gymnasium--arbetsmarknads-sammantraden` | 98 | 2024-01-24 |
| Nämnden för Individ & Familjeomsorg | `individ--familjeomsorgs-sammantraden` | 83 | 2024-02-22 |
| Nämnden för Kultur & Fritid | `kultur--fritids-sammantraden` | 90 | 2024-01-24 |
| Nämnden för Miljö & Hälsoskydd | `miljo--halsoskydds-sammantraden` | 102 | 2024-01-25 |
| Nämnden för Service | `services-sammantraden` | 90 | 2024-01-18 |
| Nämnden för Teknik | `tekniks-sammantraden` | 103 | 2024-01-17 |
| Tekniks arbetsutskott | `tekniks-arbetsutskotts-sammantraden` | 70 | 2024-02-05 |
| Nämnden för Vård & Omsorg | `vard--omsorgs-sammantraden` | 101 | 2024-01-25 |
| Valnämnden | `valnamndens-sammantraden` | 38 | 2024-02-05 |
| Kommunrevisionen | `kommunrevisionens-sammantraden` | 60 | 2024-02-19 |

Filer = unika nod-id:n på sidan 2026-10-07, sammanlagt 1 653. Senaste möte
på varje sida är från augusti eller september 2026.

Utan egen mötessida:

- **Krisledningsnämnden** sammanträder bara vid extraordinära händelser
  och har ingen mötessida.
- **Överförmyndarnämnden** är gemensam med Mölndal, Härryda, Partille och
  Öckerö; handlingarna publiceras av det gemensamma kontoret i Mölndal.
- **Bolagen** (Eksta Bostads AB, Stiftelsen Tjolöholm) har inga handlingar
  på kungsbacka.se.

Sidorna `politiska-moten-och-sammantraden`, `namndernas-sammantraden`,
`besok-kommunfullmaktige`, `webbsandningar-fran-kommunfullmaktige` och
`prenumerera-pa-handlingar-…` har inga dokument.

### Hur sidorna är byggda

- **Allt står i HTML:en från servern**, inget laddas med JavaScript och
  inget pagineras: alla år ligger på samma sida.
- Varje år är en rubrik `<h2>` "Kallelser, handlingar och protokoll från
  möten ÅÅÅÅ", varje möte en `<h3>` "D månad ÅÅÅÅ", och mötets filer en
  lista i Sitevisions filportlet (`sv-file-portlet`). Länktexten är
  filnamnet följt av typ och storlek ("Pdf, 4.5 MB").
- **Sidorna visar bara möten från januari 2024.** Äldre år ligger inte
  kvar, och sökfunktionen hittar inga protokoll från 2023. Om äldre år
  plockas bort varje år reds ut i #24.
- **`sitemap.xml`** pekar på `sitemapindex.xml` → `sitemap1.xml.gz`, med
  2 665 sidor men inga `/download/`-filer. Den räcker för att hitta
  mötessidorna, inte filerna.
- **Sitevisions REST-API** är stängt (`/rest-api/1/0/…` svarar 401).
- **`robots.txt`** stänger bland annat `/*?sv*`, `/*?start*`, `/*?date*`
  och `/*91.*`. Den sista träffar i dag ett protokoll,
  "Nämnden för Vård & Omsorg protokoll 2025-05-15, §§ 74, 76-91.pdf".

### Adresser och versioner

- Dokumenten serveras som
  `https://kungsbacka.se/download/18.<nod-id>/<tidsstämpel-ms>/<filnamn>.pdf`.
  Nod-id:t är dokumentets källnyckel; adressen pekar bara ut en version
  ([ADR-0003](../decisions/0003-dokumentets-identitet-och-datamodell.md)).
- **Tidsstämpeln är filens ändringstid.** Befolkningsprognosen
  `18.3ae5986a198e623c951df996` har tidsstämpeln `1782303262032`
  (2026-06-24 12:14:22 UTC), och svaret har `Last-Modified: Wed, 24 Jun
  2026 12:14:22 GMT`.
- **En gammal eller påhittad tidsstämpel ger 301** till den gällande
  adressen; den äldre `…/1756727320521/` och `…/1/` leder båda dit. Ett
  borttaget nod-id ger 404.
- **En fil byts ut på två sätt.** Antingen behåller den nod-id:t och får
  ny tidsstämpel (befolkningsprognosen), eller så laddas en ny fil upp och
  den gamla tas bort: handlingarna till Gymnasium & Arbetsmarknad
  2026-09-17 låg först på `18.5689acbf1a086271040226f9`, som nu ger 404,
  och ligger nu på `18.65c780211a0adcd46dd258bb` med "(1)" i namnet. Båda
  fallen täcks av ADR-0003 (ny källnyckel på en upptagen plats) och
  [ADR-0004](../decisions/0004-inkrementell-korning-poolen-ar-tillstandet.md).
- **Antagande:** att en fil som byts ut under samma nod-id alltid får ny
  tidsstämpel. Det kan inte bevisas utifrån, men tidsstämpeln är filens
  ändringstid, så en ändrad fil utan ny tidsstämpel har inte setts.

### Filnamnen

Filnamnen skrivs för hand och bär organ, typ och datum, men utan fast form.

- **Grundformen** är "`<organ>` kallelse|handlingar|protokoll
  ÅÅÅÅ-MM-DD.pdf", till exempel "Kommunfullmäktige protokoll
  2026-08-11.pdf". Gymnasium & Arbetsmarknad skriver oftast "Kallelse för
  möte Nämnden för … den ÅÅÅÅ-MM-DD", Tekniks arbetsutskott "… arbetsutskott
  - Protokoll ÅÅÅÅ-MM-DD", och revisionen har "sammanträdesanteckningar"
  utöver protokoll.
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

- **Datumen skiljer sig i 13 möten.** En del är uppenbara fel: "22 januari
  2024" under rubriken för 2025 med filer daterade 2025-01-22, och "14 maj
  2024" med "protokoll 2025-05-14". Andra kan vara avsiktliga: revisionens
  anteckningar från ett möte ligger under nästa möte.
- **Samma filer ligger under två möten.** Hos Gymnasium & Arbetsmarknad
  ligger filerna från 2025-05-15 både under "15 maj 2025" och under "24
  april 2025", och filerna från 2025-04-24 under "27 mars 2025".
- **Rubriker utan år** ("16 oktober") och med tillägg ("5 april 2024
  (flyttat från 4 april)", "17 och 18 augusti 2026", "Extrainsatt
  sammanträde …", ", extra arbetsutskott").

Hur adaptern hanterar det avgörs när den skrivs (#25).

### Dokumentens innehåll

- **Handlingarna är en sammanslagen PDF per möte**, 3–33 MB för en nämnd
  och 46 MB för kommunfullmäktige 2026-08-11 (228 sidor).
  Ärendena (tjänsteskrivelser, bilagor) ligger efter varandra i samma fil.
  Kallelsen listar ärendena och är liten.
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

- Servern svarar ibland med ett tomt svar; ett nytt försök efter några
  sekunder brukar lyckas.

## 2. Kommunens webbplats – äldre plattform (Episerver), bara via Wayback

**Belagt i politik-repot:**

- Före plattformsbytet (≈2022) låg dokumenten under
  `https://www.kungsbacka.se/globalassets/kommun-och-politik/dokument/moten-handlingar-och-protokoll/<organ>/<typ>/<år>/<datum>/<fil>.pdf`
  - Exempel: `…/moten-handlingar-och-protokoll/kommunstyrelsen/handlingar/2019/2019-05-28/arende-4---kommunbudget-2020-plan-2021-2022.pdf`
  - Här var handlingarna **uppdelade per ärende**, inte sammanslagna.
- Alla dessa adresser ger 404 live. Internet Archive har **1 886 filer** under
  `moten-handlingar-och-protokoll` (CDX-sökning gjord i politik-repot).
- Wayback är ostadigt: anslutningar bryts, och kopior **kapas tyst vid 1 MiB**.
  Varje fil måste kontrolleras (slutar på `%%EOF`, går att öppna) innan den
  godtas.
- Kända luckor för GA-nämnden: 2019–2020 och 2022–2023 saknas i Wayback;
  2018 och 2021 finns.

Täckningsmatrisen per organ och år tas fram i #24.

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
| 2024-01 → | kungsbacka.se (Sitevision), kontrollerat | En PDF per möte och typ, protokoll ibland delat |
| ~2022–2023 | Wayback av Sitevision-sidor + diariet | Luckor väntas (#24) |
| ~2015–2022 | Wayback av Episerver `globalassets` | En PDF per ärende; luckor (#24) |
| 2019-11 → | Ciceron | Per ärende, om nedladdning är öppen (#23) |
| äldre | Begäran hos kommunarkivet | Manuellt |
