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
  sökfunktionen hittar inga protokoll från 2023. Att sidorna bara visar
  tre år står i [avsnitt 2](#mötessidorna-visar-bara-tre-år).
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
- **I arkivets kopior 2021–2023 står filer ofta under ett annat möte**
  samma år, en månad eller mer bort: 141 filer i upptäckten 2026-11-04,
  till exempel byggnadsnämndens arbetsutskotts filer från 2021-09-16 till
  2021-11-11 under "2 december 2021". Där gäller filnamnets datum
  ([ADR-0062](../decisions/0062-arkivets-datum-och-ar-utan-dokument.md)).
  Några filnamn har troligen fel år: "2121-02-08" under "8 februari
  2021", och kommunstyrelsens arbetsutskotts "2022-02-07" och "2022-03-07"
  under samma dagar 2023.
- **Rubriker utan år** ("16 oktober", "21 augusti") och med tillägg ("5
  april 2024 (flyttat från 4 april)", "17 och 18 augusti 2026", "27-28
  januari 2025", "Extrainsatt sammanträde …", ", extra arbetsutskott").

Hur adaptern hanterar det står i
[ADR-0011](../decisions/0011-sitevision-organ-fran-sidan-datum-och-rattelser.md):
organet tas från sidan, datumet ur filnamnet eller rubriken, och när de
avviker gäller en rättelse i kommunfilen, belagd med datumet i kallelsen
eller protokollet.

Avvikelser som hittas från och med 2026-10 får ett eget issue med
etiketten
[`avvikelse`](https://github.com/moggleif/kommunhandlingar/issues?q=label%3Aavvikelse),
med status och belägg (se [Bidra](../01-BIDRA.md#avvikelser-i-källan)).

**Personnummer i publicerade handlingar.** Flera ärenden har fullständiga
personnummer, ibland med hemadress, oftast i bilagor som kommit utifrån.
Poolen maskar dem, och felen rapporteras till kommunen utanför repot
([ADR-0022](../decisions/0022-personuppgifter-maskas-vid-konverteringen.md)).

### Sammanträdesdagarna

Kalendern (K22,
[ADR-0032](../decisions/0032-kalendern-las-ur-besluten-och-skrivs-for-hand.md))
läses ur två källor. **Varje mötessida** inleds med årets datum, "…
har sammanträden under följande datum 2026:", en rad per månad, med
ändringar i fri text: "10 och 31 mars (mötet 10 mars är inställt)", "1
och 24 september (ombokat från 23 september)", "8 september - inställt".
Kommande år står inte där förrän året börjat närma sig. **Nästa års
datum** beslutar varje organ under våren eller hösten, och besluten står
i protokollen, i olika form: löptext, två spalter, en punktlista, en
tabell. Teknik har datumen bara i förslaget i handlingarna, och Förskola
& Grundskolas beslut finns bara inskannat, med ett OCR-fel i datumen.
Bygg och KS beslutar sina utskotts datum i utskottet; Förskola &
Grundskolas utskott har sina datum bara i förslagets tabell, "för att få
en förståelse för helheten", och ingen i poolen beslutar dem. Kända fel och osäkerheter 2026-10-12:

- KS förslag gav kommunfullmäktige den 6 mars 2027, en lördag;
  fullmäktige beslutade 9 mars (KF 2026-06-09 § 110). KF:s protokoll
  finns inte i poolen, så kalendern länkar till det på kungsbacka.se.
- Förskola & Grundskola flyttade januarimötet 2027 från 27 till 20
  januari (FG 2026-09-16), och utskottets januarimöte utgår.
- Individ & Familjeomsorgs tabell skriver några dagar med siffrorna isär
  ("1 5 april"); första mötet 2027 är uttryckligen en måndag.

Sammanträdena 2024–2025 är poolens mappar (K32,
[ADR-0053](../decisions/0053-tidigare-sammantraden-las-ur-poolens-mappar.md)).
Alla har protokoll utom kommunstyrelsens arbetsutskott 2025-09-09, som
bara har kallelsen. Två protokoll är källa utan text: Valnämnden
2024-02-05 (en Word-fil, inte konverterad) och Vård & Omsorg 2025-05-15
(inte hämtad); protokollet finns ändå hos kommunen, så sammanträdet hölls.

### Nämndernas mål och direktiv

Målfilen (K26,
[ADR-0044](../decisions/0044-namndens-mal-och-direktiv-las-ur-dokumenten-och-skrivs-for-hand.md))
har Gymnasium & Arbetsmarknad och Förskola & Grundskola. Målen står i nämndbudgeten,
som nämnden beslutar på hösten året före, och statusen i delårsrapporten
i september och årsredovisningen i februari året efter; alla tre ligger
i handlingarna. Formen 2013–2026 (kontrollerat 2026-10-13 i poolen):

- **Sedan 2018** står vid varje mål och direktiv "Beslutats av Nämnd"
  eller "Beslutats av Kommunfullmäktige", med "Nämndens formulering"
  under. Årsredovisningen 2017 saknar märkningen; där skiljer
  "Nämndens formulering" och "Nämndens bedömning" nämndens egna mål från
  fullmäktiges.
- **Statusen** är för direktiven "Uppnått" eller "Delvis uppnått", för
  nämndmålen 2017–2021 en mening som "Vi har inte nått målet men är på
  rätt väg", och i delårsrapporten 2018 en prognos ("Kommer att
  uppnås"). Från 2023 har nämndmålen bara kommentarer, och revisorerna
  noterar 2026 att nämnden inte gjort någon bedömning av måluppfyllelsen.
- **Statusraden avbryter ibland rubriken** i textlagret ("Status
  direktiv Nya målgrupper långt ifrån Delvis uppnått arbetsmarknaden"),
  och uppföljningen kortar ibland rubriken ("IM organisation",
  "Kollegialt lärande"). Statusen står ofta på sidan efter rubriken;
  målfilen har då båda sidorna som källa.
- **Handlingarna 2014** är PDF-portföljer; texten är bara "Bästa
  resultat får du om du öppnar den här PDF-portföljen", så nämndbudget
  2014 och årsredovisning 2013 finns inte i poolen. Handlingarna april
  2022 till 2023 är till största delen `ej-hamtad`.
- **Handlingarna 2025-10-16** har nämndbudget 2026 två gånger, ett
  utkast och den slutliga; målfilen citerar den senare. Nämnden döpte
  samtidigt om "Hälsofrämjande livsstil" till "Hälsofrämjande och fysisk
  aktiv livsstil" (protokollet, sida 14), så målfilen har protokollets
  namn (K27). Inga andra protokoll i poolen skiljer sig från handlingarna
  i målen; budgetmötena för 2019, 2020, 2022 och 2023 saknar protokoll.
- **Mål byter rubrik** utan att budgeten säger det. Bara protokollet
  2025-10-16 säger uttryckligen att ett mål ändrats. Flera mål har ändå
  samma formulering under nya rubriker, till exempel Trelleborgsmodellen
  (2018–2019) och Kungsbackas unika arbetsmarknadsprocess (2020–2025).
  Målfilen grupperar dem, och märker som tolkade de kopplingar där
  formuleringen också är ny.
- **Protokollen** visar nämndens egen behandling av målen. Nämnden
  godkänner årsredovisningen, delårsrapporten och uppföljningen per april,
  och noterar till protokollet dragningar om ekonomi och måluppföljning
  (två extra tillfällen per år sedan 2024), måldagar, budgetarbete,
  genomförandeplaner och enskilda mål. GA:s protokoll saknas i poolen för
  2015–2017 och 2019, och 2020, 2022 och 2023 har bara några få. Ärenden
  som justeras direkt, som årsredovisningen 2023 och delårsrapporterna
  2024 och 2025, står i ett separat protokoll från mötet.
  Paragraferna står i `uppfoljningar/kungsbacka.csv` (K28). Uppföljningar
  av verksamheten, som kvartalsuppföljningen av arbetsmarknaden, står inte
  med.
- **Andra rapporter under året** finns: uppföljningen av den digitala
  transformationsplanen (handlingarna 2021-06-23) nämner direktivet
  Digital mognad och står i målfilen som `rapport`.

Förskola & Grundskola har samma form 2019–2026 (kontrollerat 2026-11-06
i poolen), med de här skillnaderna:

- **Alliansens måldokument** ligger efter förvaltningens förslag i
  handlingarna till budgetmötena 2024-11-13 och 2025-11-12, och
  protokollet säger att nämnden godkände budgeten med Alliansens mål.
  Målfilen citerar då måldokumentet. Delårsrapporten och årsredovisningen
  2025 återger ändå förvaltningens formulering av två av målen.
- **Nämndbudget 2024** beslutades med Alliansens förslag (protokollet
  2023-10-18), men förslaget finns inte i poolen; handlingarna har bara
  förvaltningens budget. Målfilen har därför 2024 bara ur
  delårsrapporten och årsredovisningen.
- **Direktiven 2020–2023** är många uppdrag att redovisa något ("Redovisning
  av situationen för nyanlända elever"). De står bland redovisningarna
  (se nedan). Budgetarna skriver direktiven i löptext, så filerna tar dem
  ur delårsrapporten och årsredovisningen, där de har "Beslutats av
  Nämnd" och en kommentar men ingen status.
- **Statusen** är meningen under "Nämndens bedömning". Årsredovisningarna
  2019, 2020 och 2023 och delårsrapporten 2023 har ingen bedömning i
  texten.
- **Saknas i poolen:** delårsrapporterna 2021 och 2022, nämndbudget 2020
  och nämndbudget 2022 i en form med mål (Alliansens måldokument 2022 är
  löptext).

Vård & Omsorg har samma form 2018–2026 (kontrollerat 2026-11-07 i
poolen), med de här skillnaderna:

- **Få mål och nästan inga direktiv.** Tre nämndmål om året 2018–2020
  och två 2021, tre mätbara mål 2022–2024 (personalkontinuitet,
  genomförandeplaner och personalomsättning) och fyra mål från 2025,
  där personalkontinuiteten finns kvar och tre är nya.
  Avsnittet om direktiv är tomt 2019–2024; 2025 och 2026 har ett eller
  två. Budgeten 2022 ger målen korta rubriker ("Personalkontinuitet
  inom hemtjänsten") med målet som formulering; målfilen grupperar dem
  med målets text. Delårsrapporten 2022 har tappat procenttecknet i ett
  mål ("minst 95 20"); målfilen citerar texten fram till 95.
- **Statusen** är meningen under "Nämndens bedömning". Delårsrapporterna
  2019, 2023 och 2024, ett av målen i delårsrapporten 2021, tre av fyra i
  delårsrapporten 2026 och årsredovisningarna 2021, 2024 och 2025 har
  ingen bedömning i texten.
- **Saknas i poolen:** nämndens möten hösten 2020 (delårsrapporten 2020
  och nämndbudget 2021), årsredovisningen 2019 i handlingarna,
  delårsrapporten 2025 och nämndbudget 2026 i den form nämnden beslutade
  den, med Alliansens ändringsyrkande. Förvaltningens förslag står i
  handlingarna 2025-11-13, men målfilen har 2026 bara ur
  delårsrapporten. Dokumenten före 2018 är inte lästa.
- **Protokollen** har årsredovisningen, delårsrapporten och "Ekonomisk
  uppföljning och prognos" per april (2026 också per augusti, i stället
  för delårsrapporten). Måldagar har nämnden inga. Uppföljningarna per
  april 2019, 2020 och 2025 saknas i poolen.

Kultur & Fritid (kontrollerat 2026-11-09 i poolen) har samma form
2019–2023, med de här skillnaderna:

- **Målbild 2030 i stället för nämndmål.** Nämnden antog Målbild 2030
  hösten 2023 (protokollet 2023-10-18). Nämndbudgetarna från 2025 har
  "Nämndens målbild" och inga egna nämndmål, och uppföljningen heter
  "Uppföljning målbild". Målfilen har målbilden som nämndmål, grupperad
  under "Målbild 2030", utan bedömning, eftersom uppföljningen inte
  bedömer den.
- **Direktiven** är få. Alliansens direktiv om aktiviteter på särskilda
  boenden (2025 och 2026) ges till både Kultur & Fritid och Vård &
  Omsorg.
- **Saknas i poolen:** dokumenten 2018 hör till Fritid & Folkhälsa, som
  nämnden ersatte 2019; bara nämndbudget 2019 (handlingarna 2018-10-18)
  är läst. Årsredovisningen 2018 (protokollet 2019-02-28) gäller de
  nämnder som föregick Kultur & Fritid men står på 2019. Nämndbudget 2020
  och 2022–2024, delårsrapporten 2022 och nämndens möten april–december
  2022 saknas. 2023 har inga handlingar, och fem av elva protokoll är
  inte hämtade. Flera protokoll 2021–2022 är skannade.

Individ & Familjeomsorg (kontrollerat 2026-11-09 i poolen) har samma form
2020–2027, med de här skillnaderna:

- **Poolen börjar 2020.** Nämndens dokument 2013–2016 står i arkivets
  mappar men är inte hämtade, och webbplatsen har inget från nämnden
  2017–2019.
- **Fokusområden som nämndmål.** Nämndbudgetarna från 2024 skriver
  "Fokusområde: …" och "Direktiv: …" före rubriken; målfilen har
  fokusområdena som nämndmål utan ordet framför. Direktiven känns igen
  på rubrikens första ord (Förvaltningen, Tillsammans, Medarbetare,
  Digitalt först, Förebygg). Budget i balans, attraktiv arbetsgivare,
  digitaliseringen och direktivet om hedersrelaterat våld (sedan våld i
  nära relation) har bytt rubrik över åren och är grupperade som
  tolkade.
- **Statusen** tas ur delårsrapporten
  (prognos) och årsredovisningen (utfall).
- **Saknas i poolen:** protokollen 2020-02-20 och 2020-03-19 är inte
  hämtade, handlingarna februari–maj 2020, april–maj 2022 och
  september–november 2022 är kapade, så nämndbudget 2023 och delårsrapporten 2022 finns bara
  som beslut i protokollet. Tretton dokument är skannade.
- **Protokollen** har aprilrapporten (från 2023 "Apriluppföljning" eller
  "Uppföljning och prognos"), delårsrapporten och årsredovisningen. Den
  månatliga "Månadsuppföljning till nämnd" står inte med.

Teknik (kontrollerat 2026-11-09 i poolen) har samma form 2020–2026,
med de här skillnaderna:

- **Poolen börjar 2019.** Arkivmappen för nämnden står i konfigurationen
  men inget från 2015–2018 är hämtat; 2019 har två möten med kallelse
  och en handling. Arbetsutskottet har dokument 2014–2017, som inte är
  lästa, och protokoll från 2020, handlingar från 2024; dess ärenden
  räknas till nämnden.
- **Nämndmål och fokusområden.** Nämndmålen 2020–2023 (till exempel
  Kretslopp) har bytt rubrik över åren och är grupperade under den
  senaste rubriken; två grupperingar, om investeringstakten och om att
  vara möjliggörare, är tolkade. Från 2024 är målen nämndens
  formuleringar efter planeringsdagen 2023. Nämndens direktiv står från
  2025, ur delårsrapporten och årsredovisningen, eftersom avsnittet om
  direktiv i nämndbudget 2025 är tomt i poolen.
- **Statusen** tas ur delårsrapporten (prognos) och årsredovisningen
  (utfall).
- **Saknas i poolen:** nämndens möten efter 2022-06-22, så
  delårsrapporten 2022 och nämndbudget 2023 saknas helt. Handlingarna
  2020 finns bara till januarimötet (de övriga är inte hämtade eller
  saknas), och handlingarna till sju av tio möten 2023 är inte hämtade, så
  nämndbudget 2024 finns bara som dragning i protokollet. Ett tjugotal
  handlingar är skannade.
- **Protokollen** har aprilrapporten, delårsrapporten, årsredovisningen
  och 2020 "Uppföljning av aktiviteter och måluppfyllnad". Dragningar är
  förvaltningsbudget och genomförandeplan, nämndbudgeten och
  bearbetningen av målformuleringen 2023.

Service (kontrollerat 2026-11-10 i poolen) har en annan form:

- **Poolen har 2013–2016 och 2021–2026.** 2017–2020 är inte hämtat
  (utom en handling 2019), och handlingarna till fem möten 2022 är inte
  hämtade. Nämnden har inget arbetsutskott.
- **Målbild i stället för nämndmål.** Nämndbudgeten 2022 har nämndens
  målbild med åtta rubriker; från 2024 står Målbild 2027 med fem
  rubriker. Formuleringen är rubrikens första mening. Rubriken om
  arbetsplatsen är grupperad som tolkad. Nämndbudget 2023 finns inte i
  poolen.
- **Ingen status.** Nämnden följer upp fullmäktiges mål, inte målbilden,
  så raderna har ingen bedömning.
- **Protokollen** har årsredovisningen, aprilrapporten och
  delårsrapporten. Dragningar är förvaltningsbudget och verksamhetsplan,
  nämndbudgeten, arbetet med Målbild 2027 och utvecklingsportföljen.
  Månadsrapporterna (projektinformation, delegeringsbeslut) står inte
  med.

### Kommunfullmäktiges mål och direktiv

Fullmäktiges egen sida (K35,
[ADR-0056](../decisions/0056-kommunfullmaktiges-mal-med-fokusomraden-och-farg.md))
läser målen ur fullmäktiges handlingar (kontrollerat 2026-10-22 i
poolen):

- **Kommunstyrelsen har inga egna mål.** Revisionen skriver i granskningen
  av årsredovisningarna 2024 och 2025 att styrelsen arbetar direkt med
  fullmäktiges mål (KF 2025-04-08 och 2026-04-14, Bilaga 4).
- **Fem kommunövergripande mål** gäller 2022–2027, med två till fyra
  fokusområden var. Budgeten (KF juni) sätter målen i versaler och
  fokusområdena i punktlistor, och har direktiven till alla nämnder.
- **Bedömningen står i färg.** Årsredovisningen (KF april) och
  delårsrapporten (KF november) visar varje fokusområde i grönt ("I mål
  eller nära målet"), gult ("På väg mot målet") eller rött ("Långt kvar
  till målet") med en trendpil i en tabell. Pilen kommer med i texten,
  färgen gör det inte. Målfilen skriver grönt som `uppnatt`, gult som
  `delvis` och rött som `ej` (ADR-0056); inget fokusområde 2023–2025 är
  rött. Målens samlade bedömning är en mening i löptexten,
  som konverteringen före 0.10.0 ofta blandade med den andra spalten;
  i poolen står den så tills dokumenten konverteras om (K41).
- **Budgeten och uppföljningen skriver ibland samma fokusområde olika**,
  till exempel "god vård och omsorg" i budgeten och "god omsorg" i
  uppföljningen.
- **Årsredovisningen 2022 och delårsrapporten 2023** (KF 2023-04-04 och
  2023-11-07) finns som text i poolen, men PDF:erna bara i webbarkivet,
  så deras fokusområden står inte med än.
- **Protokollens** paragrafer om årsredovisningen, delårsrapporten och
  uppföljningen per april står i `uppfoljningar/kungsbacka.csv`.

### Nämndernas lokalbehov

Lokalbehovsfilen (K36,
[ADR-0057](../decisions/0057-lokalbehoven-foljs-steg-for-steg-ur-alla-organs-dokument.md))
har Gymnasium & Arbetsmarknad, 2023–2026 (kontrollerat
2026-10-22 i poolen), och Förskola & Grundskola, 2021–2026 (kontrollerat
2026-11-06). Stegen står i fyra organs dokument:

- **Nämndens lokalbehov** för de kommande fem åren beslutas i oktober,
  med behovsbeskrivningarna som bilagor i handlingarna och en
  prioritering i protokollet, ibland efter ett yrkande. Handlingarna
  2023 är inte hämtade och protokollen från oktober och november 2023
  saknas i poolen, så det året syns bara genom senare hänvisningar.
  Lokalbehov 2028–2032 godkändes på mötet 2026-10-22; tills protokollet
  finns i poolen är handlingarna källan.
- **Lokalplanen** står i kommunbudgeten som fullmäktige beslutar i juni,
  med ett löpnummer per projekt (1412–1415 för GA 2026). Samma tabell
  återges i kommunstyrelsens handlingar.
- **Startbeslutet** fattar kommunstyrelsen som "Uppstart av projekt i
  lokalplan".
- **Det som är på gång och utfört** står i servicenämndens protokoll och
  bokslut, under servicenämndens egna projektnamn och projektnummer, som
  inte är lokalplanens löpnummer. Kopplingen till nämndens behov är då en
  bedömning (`tolkad = ja`). Nämndens delårsrapport och årsredovisning
  nämner ibland arbete som pågår.

Nämnden får ingen återrapport om förra årets lokalbehov; ett behov som
inte står med ett år syns som ett spår som tar slut.

Förskola & Grundskolas protokoll räknar upp behovsbeskrivningarna som
bilagor, utan prioritering; 2026 står de bara i handlingarna. Lokalplanens
löpnummer för förskolor och skolor ligger mellan 227 och 364. Lokalfilen
har nämndens steg 2021–2026, lokalplanen 2025 och 2026 och
startbesluten; servicenämndens projekt för FG är inte lästa än.
Lokalplanens avvecklingsposter (paviljonger, Tingbergsskolan, Fjordskolan,
Åsa Gårdsskola) står inte med, och inte heller poster med en bokstav i
löpnumret (227a, 236b), eftersom filen bara tar siffror.

Vård & Omsorgs protokoll räknar upp behovsbeskrivningarna som bilagor
2022–2026; lokalbehovsplanen 2021 står i handlingarna och har inga
bilagor. Lokalbehovsplanen 2024–2028 bordlades 2022-10-19 och beslutades
2022-11-16. Lokalbehovet 2027–2031 (hösten 2025) saknas i poolen.
Lokalfilen har nämndens steg 2021–2026 och lokalplanen 2021–2026
(löpnummer 803–826). Behov som är teknik eller utrustning i befintliga
lokaler (laddstolpar, nödvatten, låssystem, trygghetslarm, wifi,
hörslingor, komfortkyla, skugga och möbler utomhus, fastigheternas
status) och flytten av arkivet står inte med, utom reservkraften som har
ett eget löpnummer i lokalplanen. Åtgärdsvalet för Ekhaga 2022 står på
samma sida som avvecklingen och är ett steg med den. Lokalplanens poster 827 och 828 ("Avveckling
lokal hemtjänst", "Anpassning lokal hemtjänst") säger inte vilken lokal
och står inte med.

Projekten följs genom alla organs handlingar på samma sätt som för GA:
kommunstyrelsens startbeslut (Anneberg 2021, Signeshus 2024), servicenämndens
"Projektinformation" och bokslut, och Vård & Omsorgs egna rapporter om när
ett boende öppnade (Särö 2021, Björkris mars 2023, Signeshus april 2026).
Servicenämndens bokslut anger dess egna projektnummer; där löpnumret inte
står med (Hede i driftprojekten, Pölagården bland de vakanta lokalerna)
eller där statusen läses ur en sifferkolumn (Vallda) är steget tolkat.
Särö står inte i lokalplanen 2021 eller senare men har fått ett eget behov,
eftersom boendet ersatte Bukärrsgården. Ekhagas startbeslut 2022 står bara
som förslag (arbetsutskottet och kommunstyrelsens handlingar), eftersom
kommunstyrelsens protokoll 2022-02-22 saknas i poolen. Bukärrsgården
tömdes 2021 men hyrs vidare som tillfälligt boende och har inget utfört
steg.

Kultur & Fritids protokoll räknar upp behovsbeskrivningarna som bilagor
2023 och 2024; 2025 och 2026 står behoven bara i handlingarnas tabell,
som protokollet säger att nämnden biföll. Lokalbehovet 2021–2025 (2019)
finns som beslut utan bilaga, 2023–2027 (2021) bara som kallelse, och
2022–2026 (2020) inte alls. 2022 års lokalbehov syns genom
kommunstyrelsens protokoll om isytan 2023-03-21.
Lokalplanens löpnummer under "Fritidsanläggningar och kulturlokaler" är
114, 128 och 136–148, och arenan har 131 bland kommunens övriga lokaler;
löpnummer 136 användes först för Björkris idrottshall och sedan för
Skårby. Avvecklingen av Elektronen (137) står inte med, och inte heller
löpnummer 130, fullmåttshallen i Åsa som nämnden strök ur lokalbehovet
2019. Folkbiblioteket i Åsa står i lokalplanen ihop med
skolan (337). Servicenämndens bokslut anger ofta lokalplanens löpnummer
bredvid projektnamnet (138 Frillesås ridklubb, 142 Naturum). Behov som
bytt namn med samma löpnummer (Iserås och Onsala fullmåttshall,
Ölmevalla och Åsa fullmåttshall, kulturskolelokaler och KFT-hubb i Åsa)
är samma behov; utan löpnummer är ett namnbyte tolkat. Detaljplanen för
Skårby 3:4 gäller en tennishall för en förening och står inte med.

Individ & Familjeomsorgs tabeller i lokalbehovet 2021 har löpnummer.
Från 2023 saknar tabellerna löpnummer för nya platser, och 2025 har bara
SBF kvar sitt (505). Lokalplanens löpnummer för nämnden är 405 (Vallda),
413, 414, 502–505, 507, 508, 510–517, 519 och 520; servicenämndens bokslut
ger också 415 (Kolla). 508 a–j är en pool av framtida boenden, där 508 b
(Anneberg) och 508 j (Pölagården) fick egna startbeslut 2021. De övriga
bokstäverna står inte med, inte heller 508 e som nämndens tabeller har
kvar 2021–2024, eftersom ingen plats eller inget projekt knyts till dem. 504 Björkris
ersattes 2024 av 515 Åsaberg (kommunstyrelsen 2024-01-23); de står som
två behov. Det årliga behovet om tolv nya platser utan namn är ett eget
behov, och kommunstyrelsens startbeslut 2025-12-16 för en lokal i
Kullavik hör dit, eftersom beslutet hänvisar till just det behovet.
Arbetsutskottets förslag 2026-11-03 för 514 står inte med, eftersom
kommunstyrelsens beslut inte finns i poolen än. Servicenämndens bokslut
har en kolumn för avslutade projekt; ett boende som står som avslutat där
(Kolla 2022, Söderstaden 2024, Kommunvägen 2024, Pölagården 2025) är
utfört, och kopplingen är direkt eftersom raden har löpnumret. Högarydsvägens gruppbostad, som invigdes i januari 2026, är
tolkad som Vallda. Detaljplanen för Bukärr 1:30 i Särö följs genom
fastighetsbeteckningen.

Byggnämndens och fullmäktiges detaljplaner står som steg på gång. Nyckeln
är fastighetsbeteckningen eller kvarteret: Kolla 5:6 är Gräskärrs förskola
(nämnden för Förskola & Grundskola 2022-12-15), Iserås 19:1 är Iseråsskolan,
Åsa 5:246 är Ölmevallaskolan (kommunstyrelsens handlingar 2023-10-24) och
kvarteren Gjutaren och Liljan är skolan i kvarteret Liljan. Planer som inte går att knyta till ett visst behov
står inte med: Annebergs centrum (planen nämner varken förskola eller
boende) och Aranäs etapp 4 (utbildningslokaler utan nämnd).
Byggloven för kommunens egna lokaler beslutas på delegation och syns inte i
protokollen.

Teknik äger själv de flesta av sina lokaler (reningsverk, vattenverk,
pumpstationer och återvinningscentraler) och har därför bara ett
löpnummer i lokalplanen, 1406 Duveheds omlastningscentral (lokalplanerna
2021–2023).
Behoven är nämndens anläggningar och de lokaler nämnden hyr:
omlastningen i Duvehed, som servicenämnden byggde och slutredovisade
2025, och dess utbyggnad, lagringsytorna på Teknikens hus,
återvinningscentralerna och Framtidens avloppsrening vid Hammargård, som
fullmäktige godkände som projekt 2024 (startbeslut) och vars detaljplan
för Kungsbacka 6:27 och Hammargård 1:7 följs genom fastighetsbeteckningen.
Återvinningscentralen syd följs från planen i Frillesås-Rya 3:77 till
lokaliseringen i Kläppa 2:2. Parkeringshuset Linden står med som utfört
2021. Gator, VA-ledningar och cykelvägar är investeringar men inte
lokaler och står inte med.

Service bygger och hyr lokaler åt alla nämnder. De projekten står på
beställarens sida, där servicens projektinformation och slutredovisning är
steg. Servicenämndens egen sida har bara nämndens egna behov ur beslutet
"Service Lokalbehov" (2021–2026) och löpnumren i lokalplanen
(1405, 1407, 1500–1520 och 238): tillagningskök, valförråd, yta för civil
beredskap, administrativa lokaler, förråd och verkstäder. Pågår och utfört
tas ur projektinformationen och investeringstabellerna i
årsredovisningen; en koppling bara på namnet är tolkad. Tre projekt som
lades ned (köket i Kapareskolan, Fjordskolan 2023 och Gårda) står inte med,
eftersom sidan saknar ett steg för det.

### Nämndernas initiativärenden

Initiativfilen (K37,
[ADR-0058](../decisions/0058-initiativarenden-foljs-som-lokalbehoven.md))
har Gymnasium & Arbetsmarknad, 2021–2026 (kontrollerat
2026-10-22 i poolen), och Förskola & Grundskola, 2020–2026 (kontrollerat
2026-11-06):

- **Initiativen** väcks på sammanträdet, ofta som en ny punkt på
  ärendelistan, och står som egna paragrafer i protokollet med
  "Initiativärende" eller "Initiativ" i rubriken. Nämnden remitterar dem
  oftast till förvaltningen och beslutar på ett senare möte.
- **Avsändaren** står i rubriken som en partiförkortning, som `(S)`, eller
  i texten som Alliansen eller med partiernas namn.
- **Protokollen ligger ibland i flera filer** för samma möte, med
  paragrafernas nummer i filnamnet (`protokoll-…-14-17-26.md`). Ett
  initiativ kan stå i den andra filen.
- **Det som följer** står i nämndens protokoll och handlingar, och ibland
  i kommunstyrelsens protokoll när nämnden ber om pengar ur en central
  pott.
- **Luckor:** nämndens protokoll från april till december 2023 och mötet
  2025-03-27 saknas i poolen, liksom det mesta före 2021. Initiativ som
  väcktes då syns bara genom senare protokoll, eller inte alls.
- **Förskola & Grundskola** skriver avsändaren på samma sätt, men också
  "allianspartierna" (2021); filen har då `Alliansen`. Protokollet 2023-05-17 saknas i poolen, så
  bifallet till initiativet om mobilfria skolor står bara i handlingarna
  2024-03-13. Initiativet om HLR i förskolan (2026-09-16) har ingen
  avsändare i protokollet och står utan steget `vackt`.

- **Vård & Omsorg** (2021–2026, kontrollerat 2026-11-07) skriver
  rubriken "Initiativ från" eller "Initiativärende från" med ledamotens
  namn och partiets förkortning. Fyra partier med namn och förkortning,
  (M), (L), (C) och (KD), är `Alliansen`. En senare paragraf med samma
  diarienummer är ett steg i samma ärende. När nämnden ger förvaltningen
  ett uppdrag utan att säga att den bifaller initiativet står steget som
  `bifall` med `tolkad = ja`.

- **Kultur & Fritid** (2021–2026, kontrollerat 2026-11-09) skriver
  "Initiativ" eller "Initiativärende" och partiet med namn eller
  förkortning. Nämnden har sedan 2025 en egen punkt, "Återrapportering
  av initiativ", som ger utfallet. Protokollen 2023 saknas till stor del
  i poolen; initiativ som behandlades då står med kallelsen som källa.
  2019–2020 hette initiativen "väckt fråga"; de flesta protokoll från de
  åren saknas, så besluten tas ur nämndens sammanställning av väckta
  frågor (handlingarna 2021-08-26), som också har förslag från Fritid &
  Folkhälsa 2018 som nämnden tog över. När nämnden fått pengar ur
  kommunstyrelsens potter står kommunstyrelsens beslut som uppföljning.
  "Ledamöterna" är avsändaren när alla partier står bakom initiativet
  (2025-02-19). Två ärenden saknar steget `vackt`: rullstolar för
  paraidrott (2023), där avsändaren inte står i poolen, och Friluftsåret
  2021, där sammanställningen skriver partiet "( c )".
  Nämndens egna uppdrag till förvaltningen (bidragssystemet,
  ridanläggningarna, studieförbunden, konsten i det offentliga rummet,
  det kulturpolitiska programmet med flera) följs som initiativ med
  avsändaren `Nämnden`, eller partiet när uppdraget kom ur ett yrkande.
  Ett beslut som bara ändrar en enhets uppdrag, som Hållbar hälsa 2025,
  står inte med.

- **Individ & Familjeomsorg** (2020–2026, kontrollerat 2026-11-09)
  skriver "Initiativ" eller "Initiativärende" och partiet med
  förkortning. Gemensamma initiativ har alla partiernas förkortningar som
  avsändare, så som protokollet skriver dem. Nämndens egna uppdrag till
  förvaltningen (gränsdragningen mot Vård & Omsorg, den nya
  socialtjänstlagen, riktlinjerna för civilsamhället, Bostad först med
  flera) följs som initiativ med avsändaren `Nämnden`. Redovisningarna
  nämnden beställt om personligt ombud, Bostad först och utsatta kvinnor
  står som steg i de ärendena. Kommunstyrelsens beslut om pengar till
  nämndens satsningar står som uppföljning.

- **Teknik** (2020–2026, kontrollerat 2026-11-09) skriver
  "Initiativyrkande" (2020), "Initiativärende" eller bara "Yrkande"
  (2026-05-13), och partiet med förkortning eller utskrivet.
  Gemensamma initiativ har partierna som avsändare så som protokollet
  skriver dem, och `Alliansen` när alla fyra allianspartierna står
  bakom. Arbetsutskottets initiativ räknas till nämnden, och en begäran
  om svar som nämnden ger förvaltningen i uppdrag att besvara följs som
  initiativ. Nämndens
  egna uppdrag till förvaltningen (Kyrkogatan, en offentlig toalett,
  dricksvattenavtalet, gatubelysning längs statlig väg med flera) följs
  som initiativ med avsändaren `Nämnden`.

- **Service** (2020–2026, kontrollerat 2026-11-10) har få initiativ:
  partiernas initiativ (2024 och 2025) och nämndens uppdrag till
  förvaltningen (delning av personalbil, Löftagården, måltiderna vid Kolla,
  gröna hyresavtal, Prova på skollunchen, laddstationer, lokalvården vid
  Elof Lindälvs gymnasium), som följs med avsändaren `Nämnden`.
  Kommunstyrelsens initiativ som nämnden yttrar sig över står inte med.

### Nämndernas redovisningar

Redovisningssidan (K42,
[ADR-0065](../decisions/0065-redovisningarna-foljs-som-handlingsplanerna.md))
har Förskola & Grundskola 2020–2026 (kontrollerat 2026-11-07 i poolen):

- **Beställda redovisningar** kommer tillbaka som egna paragrafer i
  protokollet. 2020 säger rubriken det ("Redovisningar i nämndbudget 2020
  – …"), senare ibland texten ("Enligt direktiv i nämndbudget 2022 …"),
  och oftast har paragrafen direktivets rubrik. Direktiven står i
  årsredovisningen 2019, 2020, 2021, 2022 och 2023 och i
  delårsrapporten 2020; filen tar dem ur årsredovisningen när den finns,
  ett steg per år. Av 41 direktiv har 36 en redovisning i poolen. De fem
  utan är från 2019, och poolen har inga protokoll från nämnden före
  2020.
- **Gränsen mot målen** är rubrikens första ord. Två direktiv 2022 som
  årsredovisningen säger redovisades på ett möte står ändå kvar bland
  målen, eftersom rubriken säger något annat: tyska och franska och
  skollokaler utanför skoltid. Direktiven 2024 som börjar med "Utreda"
  står också kvar; de har formulering och status.
- **Återkommande redovisningar** är patientsäkerhetsberättelsen,
  tillsynen av fristående verksamheter, dataskyddet, olycksfall och
  tillbud, kränkningsärendena, klagomålen, huvudmannens systematiska
  kvalitetsarbete, betygsresultaten, enkäterna, intraprenaderna, God och
  nära vård, samverkan för ökad rörelse, skolvalet, närvaron, skolplikten
  och barn- och elevhälsan. Sedan 2025 har
  nämnden ett eget årshjul för dem (protokollet 2025-05-14).
- **Inte med:** den stående paragrafen "Information – Förskola &
  Grundskola arbetsutskott och nämnd", som finns på nästan varje möte,
  enstaka informationspunkter och kommunrevisionens rapporter.

Vård & Omsorg (kontrollerat 2026-11-07) har inga direktiv som börjar
med Redovisning, Utredning eller Information. Nämnden gav i stället fyra
*utredningsuppdrag* i beslutet om nämndbudget 2022; filen har dem i fasen
`direktiv` (protokollet 2021-09-15), och de kommer tillbaka som
paragrafer med rubriken "Uppdrag: …" 2022–2023. Återkommande är
berättelserna (patientsäkerhet, kvalitet, säkerhet och
informationssäkerhet och dataskydd), God och nära vård, båda vid delåret
och helåret, och Qvalifys kvalitetskontroller. Kvartalsrapporterna om ej
verkställda beslut, de enskilda anmälningarna enligt lex Maria och lex
Sarah, informationspunkterna (också Qvalifys halvår 2026), uppföljningen
av arbetsmiljön och den interna kontrollen står inte med.

Kultur & Fritid (kontrollerat 2026-11-09) har inga direktiv som börjar
med Redovisning, Utredning eller Information. Återkommande är
dataskyddet, God och nära vård och lokala BRÅ:s lägesrapporter.
Nämndens "Uppdrag till förvaltningen" står bland initiativärendena
(se ovan).

Individ & Familjeomsorg (kontrollerat 2026-11-09) har inga direktiv som
börjar med Redovisning, Utredning eller Information. Återkommande är
kvalitetsberättelsen, patientsäkerhetsberättelsen, dataskyddet, God och
nära vård och årsrapporten om det systematiska arbetsmiljöarbetet.
Kvartalsrapporterna om ej verkställda beslut och informationspunkterna,
också personalchefens genomgångar av tillbud och arbetsskador 2023, står
inte med. Handlingsplanerna
(åtgärdsplanen för budget i balans 2020–2021 med sina uppföljningar,
psykisk hälsa, suicidprevention, konkurrensutsättning, digitalplanen och
planen för höjd kvalitet i bemötande) står på handlingsplanssidan.

Teknik (kontrollerat 2026-11-09) har återrapporter som nämnden beställt
(uppdragen till förvaltningen 2021, parkeringshuset Linden,
färdtjänstarbetet, förstudierna om vatten och avlopp och om de digitala
vattenmätarna, säkerhetsarbetet och de löpande projektkostnaderna).
Återkommande är dataskyddet, det systematiska arbetsmiljöarbetet,
kvalitetsrapporten för färdtjänst och miljörapporterna. Nämndens egna
planer (vattentjänstplanen, dagvattenplanen, trafikstrategin, gång- och
cykelplanen, lekplatserna, återvinningscentralerna, slamstrategin,
trafikförsörjningsprogrammen och budget i balans) står på
handlingsplanssidan; remisser av andras planer står inte med.

Service (kontrollerat 2026-11-10) har slutredovisningarna av byggprojekten,
också de som byggts åt andra nämnder, den månatliga avstämningen av
Kungsbacka Arena som kommunstyrelsen beställt, dataskyddet,
inköpsrapporten, utvecklingsportföljen och det systematiska
arbetsmiljöarbetet. Nämndens styrdokument (koncepten för boende,
idrottshall, kök och utemiljö, principerna för lokalplanering och
livsmedelsinköp, riktlinjerna för direktupphandling, fordonspolicyn och
fastighetsstrategin) står på handlingsplanssidan. Yttranden över andras
detaljplaner står inte med.

### Dokumentens innehåll

- **Handlingarna är oftast en sammanslagen PDF per möte.** Ärendena
  (tjänsteskrivelser, bilagor) ligger efter varandra i samma fil.
  Kallelsen listar ärendena och är liten.
- **Kallelsen står ibland först i handlingarna.** Filer med rubriken
  "Handlingar för möte …" börjar med kallelsen, och "Kallelse och
  handlingar för möte …" är båda (kontrollerat 2026-10-09 i poolen, till
  exempel Gymnasium & Arbetsmarknad 2024-01-24 och Förskola & Grundskola
  2024-08-21). Därför räknas de som en grupp i luckorna
  ([ADR-0020](../decisions/0020-luckor-raknas-fram-lagras-inte.md)).
- **Revisionen publicerar bara protokoll**, inga kallelser.
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
som AI-agenten arbetar i nådde inte `web.archive.org` 2026-10-08 på
dagen (anslutningen bröts), men gjorde det ibland samma kväll; Actions
når både CDX-listorna och hela kopior.

Webbplatsen har haft tre generationer. Dokumenten från de två
Episerver-generationerna och Sitevisions år 2021–2023 hittas inte från den
levande webbplatsen. Om deras adresser svarar live är inte prövat här;
politik-repot fick 404 på `globalassets`-adresserna.

| Generation | År | Adress till filerna | Form |
|---|---|---|---|
| Episerver, äldre | 2013–2017 | `www.kungsbacka.se/Global/Kommun och politik/Dokument/Möten, handlingar och protokoll/<organ>/<typ>/<år>/<fil>.pdf` | Dagordning, protokoll och handlingar; ibland flera handlingar per möte |
| Episerver, `globalassets` | 2017–2022 | `www.kungsbacka.se/globalassets/kommun-och-politik/dokument/moten-handlingar-och-protokoll/<organ>/<typ>/<år>/[<datum>/]<fil>.pdf` | Handlingarna **en PDF per ärende** |
| Sitevision | 2021 → | `kungsbacka.se/download/18.<nod-id>/<tidsstämpel>/<filnamn>` | Som i avsnitt 1 |

Sitevision-generationen kan hämtas i nattkörningen, sist och nyast först
([ADR-0018](../decisions/0018-wayback-sist-nyast-forst-och-bara-luckor.md)),
och slås på per organ i kommunfilens `wayback`
([ADR-0027](../decisions/0027-arkivet-slas-pa-per-organ.md)); vilka organ
som är påslagna står i kommunfilen
([ADR-0047](../decisions/0047-alla-organ-lases-ur-arkivet.md)). De två
Episerver-generationerna läses med adaptern `episerver` ur organets mappar
i kommunfilen
([ADR-0039](../decisions/0039-episerver-ur-arkivet-med-mappar-och-monster.md));
bara de organ som har mappar där hämtas. Ett mötes filer av samma typ, som
handlingarna per ärende, blir ett dokument
([ADR-0049](../decisions/0049-ett-motes-filer-slas-ihop-till-ett-dokument.md)).
En nedlagd nämnds mapp ligger under den nämnd som tog över; vilken står i
kommunfilen.

Organ och typ står i sökvägen i de två Episerver-generationerna, och i
filnamnet hos Sitevision. Organen hette annorlunda förr, och några finns
inte längre: Äldreomsorg och dess arbetsutskott, Funktionsstöd, Gymnasie
och Vuxenutbildning, Fritid och Folkhälsa, Kultur och Turism och Kommunstyrelsens
personalutskott.

### Mötessidorna visar bara tre år

69 arkiverade kopior av sex av Sitevision-sidorna i avsnitt 1, från april
2022 till maj 2026, visar aldrig fler än tre årsrubriker. Byggnadsnämndens
sida visade till exempel 2021–2023 i november 2023 och 2022–2024 i mars
2024. Det äldsta året försvinner alltså från sidan någon gång efter att ett
nytt år kommit till; exakt när visar kopiorna inte. Det som publicerats
2021–2023 hittas därför inte från den levande sidan, bara via Wayback och
möjligen diariet (avsnitt 3).

### Täckning

Antal filer med minst en kopia som Wayback sparat som PDF (status 200),
per organ och år: `p` protokoll, `k` kallelse eller dagordning, `h`
handlingar. Tom ruta: ingen fil. Organ står som i källan: mappnamnet hos
Episerver och organets `id` i
[`kommuner/kungsbacka.toml`](../../kommuner/kungsbacka.toml) hos
Sitevision. Att en fil finns betyder inte att kopian är hel (se nedan).

**Episerver, äldre (2013–2017).** 1 072 PDF-filer, 1 049 i matrisen.
Utanför matrisen: 23 filer som inte ligger i en mapp per typ och år, de
flesta från Kommunstyrelsens personalutskott 2014.

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

**Episerver, `globalassets` (2017–2022).** 1 795 PDF-filer, 1 781 i
matrisen; filer med samma namn under `http`, `https` och med eller utan
`www` räknas en gång. Handlingarna är en fil per ärende, därför de stora
talen hos fullmäktige och kommunstyrelsen. Kommunrevisionen har ingen mapp
per typ; dess filer är protokoll och sammanträdesanteckningar. Utanför
matrisen: 14 filer som inte ligger i en mapp per organ och år, bland dem
fyra protokoll (till exempel `kft-protokoll-2019-01-31.pdf`), två
kungörelser och en lista med sammanträdesdagar.

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
| kommunrevisionen |  |  | p15 | p6 | p17 | p4 |
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

**Sitevision (2021–2023).** 1 384 nod-id:n i matrisen; ett nod-id räknas
en gång även när det förekommer med flera tidsstämplar (versioner). Åren
från 2024 finns på den levande sidan (avsnitt 1). Utanför matrisen: 36
filer, från alla år, vars namn saknar organ, typ eller fullständigt datum (till exempel `Protokoll 230920.signerad.pub.pdf`).
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
  till exempel fullmäktiges handlingar 2022-06-15, där CDX anger 59,8 MB
  för en kopia och 1,0 MB för en annan. Den största kopian av den nyaste
  versionen väljs, och en kopia utan `%%EOF` i slutet blir `ej-hamtad` med
  `fel: kapad`
  ([ADR-0018](../decisions/0018-wayback-sist-nyast-forst-och-bara-luckor.md)).
- Några kopior är sparade som 404-sidor (`text/html`) och räknas inte.
- CDX-fältet `length` är den komprimerade postens längd i arkivet, inte
  filens. Tre av 7 137 filrader hade 2026-10-08 ett negativt värde och
  rangordnas därför som minst.
- CDX svarar ibland med en HTML-sida, "Internet Archive: Temporarily
  Offline", i stället för listan.
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

Åtkomst, API, handlingstyper, anslagstavlan och e-arkivet kontrolleras
i #23.

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
| 2013–2017 | Wayback av äldre Episerver (`Global`) | Dagordning, protokoll och handlingar |
| 2019-11 → | Ciceron | Per ärende, om nedladdning är öppen (#23) |
| äldre | Begäran hos kommunarkivet | Manuellt |
