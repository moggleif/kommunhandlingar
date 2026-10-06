# Källor: Kungsbacka kommun

> Sammanställt 2026-10-06 ur anteckningarna i `moggleif/politik`
> (`data/KALLOR.md`, `scripts/hamta_fullmaktige.py`, `scripts/extrahera_utbud.py`)
> och de faktiska adresser repot redan hämtat från. Allt märkt *att verifiera*
> är inte kontrollerat mot den levande webbplatsen och ska kontrolleras innan
> adaptrarna skrivs.

## 1. Kommunens webbplats – nuvarande plattform (Sitevision)

**Belagt i repot:**

- Mötessidorna ligger under
  `https://kungsbacka.se/kommun-och-politik/politik-och-demokrati/politiska-moten-och-sammantraden/…`
  med en undersida per organ (t.ex. `kommunfullmaktiges-sammantraden/`).
- Dokumenten serveras som Sitevision-noder:
  `https://kungsbacka.se/download/18.<nod-id>/<tidsstämpel-ms>/<filnamn>.pdf`
  - Exempel: `…/download/18.4ac81f8819a0f459fef1dd70/1761285111298/Protokoll för nämnden för Gymnasium & Arbetsmarknad  2025-10-16.pdf`
  - Exempel: `…/download/18.5689acbf1a086271040226f9/1789034138535/Handlingar för möte Nämnden för Gymnasium & Arbetsmarknad den 2026-09-17.pdf`
- **Samma nod-id kan få ny tidsstämpel** när filen byts ut
  (befolkningsprognosen 2025: `…/1756727320521/` och `…/1782303262032/`). Hur det
  påverkar ett dokuments identitet är en öppen fråga i `docs/03-ARKITEKTUR.md`.
- Filnamnen bär organ och datum i klartext: "Protokoll för …", "Handlingar
  för/till möte … den ÅÅÅÅ-MM-DD", och (enligt KALLOR.md) en separat kallelse.
- **Handlingarna är en sammanslagen PDF per möte**, 3–33 MB för en nämnd.
  Ärendena (tjänsteskrivelser, bilagor) ligger efter varandra i samma fil.
  Kallelsen listar ärendena och är liten.
- Nämndsidorna listar **ungefär två år bakåt** (för GA: från 2024).
- Fullmäktige sänds och arkiveras som video (YouTube 2022–2024, Screen9 2024–),
  med kapitel per ärende och inlägg. Redan hämtat i politik-repot.

**Att verifiera live:**

- Fullständig lista över organ och deras sidadresser (KF, KS, ~10 nämnder,
  ev. utskott, valnämnd, krisledningsnämnd, revision, bolagsstyrelser).
- Om listorna pagineras eller laddas med JavaScript (Sitevision kan rendera
  serverside; i så fall räcker HTML-tolkning).
- Om sidan exponerar ett `sitemap.xml` som täcker `/download/`-noderna.
- Om Sitevisions REST-API (`/rest-api/…`) är öppet – det är det sällan.

## 2. Kommunens webbplats – äldre plattform (Episerver), bara via Wayback

**Belagt:**

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

**Att verifiera:** full CDX-dump per organ och år, för att få en
täckningsmatris.

## 3. Diariet – Ciceron (CGI)

**Belagt:**

- Öppet webbdiarium på `https://ciceronsok.kungsbacka.se`, ärenden från
  **2019-11-27**. Anslagstavla på `ciceronanslagstavla.kungsbacka.se`, e-arkiv
  på `arkiv.kungsbacka.se`.
- Ärenden har diarienummer `<ORGAN>-<ÅR>-<NR>` (t.ex. `KS 2023-00686`,
  `GA-2024-00194`), och handlingarna i ärendet kan ibland laddas ned.

**Att verifiera:**

- Om sökningen och nedladdningen är åtkomliga utan inloggning och utan
  JavaScript, eller om det är en SPA med ett internt JSON-API.
- Vilka handlingstyper som publiceras (allt, eller bara protokoll och beslut).
- Om **anslagstavlan** listar justerade protokoll med datum – den är i så fall
  den bästa källan för "när blev protokollet officiellt".
- Om `arkiv.kungsbacka.se` (e-arkivet) har äldre protokoll än webbplatsen.

## 4. Övrigt

- **Begäran om allmän handling** (`kommunarkivet@kungsbacka.se`) för det som
  saknas i alla digitala källor. Manuellt, men protokoll är alltid
  arkiverade och utlämnbara.
- Kommunens sökfunktion `/om-webbplatsen/sok?query=…&startAtHit=…` är
  serverrenderad och kan användas för att hitta dokument som inte länkas från
  mötessidorna.

## Täckning – första gissning

| Period | Källa | Form |
|---|---|---|
| ~2024 → | kungsbacka.se (Sitevision) | En PDF per möte och typ |
| ~2022–2024 | Wayback av Sitevision-sidor + diariet | Luckor väntas |
| ~2015–2022 | Wayback av Episerver `globalassets` | En PDF per ärende; luckor |
| 2019-11 → | Ciceron | Per ärende, om nedladdning är öppen |
| äldre | Begäran hos kommunarkivet | Manuellt |
