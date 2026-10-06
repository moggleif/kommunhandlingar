---
status: accepted
date: 2026-10-06
decision-makers: Morgan
consulted: Claude
---

# Dokumentet identifieras av sin plats i modellen och en källnyckel; sha256 är versionen

## Context and Problem Statement

Datamodellen i `docs/03-ARKITEKTUR.md` är Kommun → Organ → Sammanträde →
Dokument → Version, och sökvägen `data/<kommun>/<organ>/<år>/<datum>/<typ>.md`.
Granskningen av grunden visade att det inte räcker
([#2](https://github.com/moggleif/kommunhandlingar/issues/2)):

* Ett sammanträde kan ha flera bilagor, och två sammanträden kan hållas
  samma dag. Båda krockar i sökvägen.
* De äldre handlingarna (Episerver, via Wayback) är en PDF per ärende, och
  diariet (Ciceron) är ordnat per diarienummer. Ärendet saknas i modellen.
* Sitevision ger en ny adress (ny tidsstämpel) när en fil byts ut under
  samma nod-id. Adressen kan alltså inte vara identiteten.

Vad identifierar ett dokument, vad är en version, och hur byggs sökvägen?

## Decision Drivers

* **Stabil plats.** Samma dokument ska hamna i samma fil körning efter
  körning, så att git-historiken visar vad kommunen ändrat (K9).
* **Inga krockar.** Två olika dokument får aldrig dela sökväg.
* **Läsbart utan index.** Den som bläddrar i repot ska förstå var ett
  dokument hör hemma utifrån sökvägen.
* **Kommunoberoende.** Ingenting i regeln får förutsätta Kungsbackas
  plattformar; det plattformsspecifika ligger i adaptrarna.
* **Bara text** (ADR-0001). Originalen finns inte kvar att jämföra mot,
  så identiteten måste gå att avgöra ur källan och front matter.

## Considered Options

* A – Platsen i modellen: organ, datum och typ, med löpnummer vid krock
* B – Platsen i modellen plus en källnyckel från adaptern
* C – Innehållet (sha256) är identiteten
* D – Ärendet (diarienummer) är grundenheten

## Decision Outcome

Valt alternativ: "B – Platsen i modellen plus en källnyckel från adaptern",
eftersom det ger läsbara, stabila sökvägar och ändå känner igen en utbytt fil
när kommunen ger den ny adress eller nytt filnamn.

Beslutet i detalj:

* **Källnyckeln** är adapterns stabila id för filen, på formen
  `<plattform>:<id>` – för Sitevision nod-id:t, för Episerver den
  ursprungliga adressen. För en kopia i Internet Archive är det
  originalets nyckel, inte arkivets adress. Den är unik inom kommunen och
  står i front matter.
* **Dokumentet placeras en gång.** Första gången en källnyckel hittas får
  dokumentet en plats i modellen: sammanträde, typ (`kallelse`,
  `handlingar`, `protokoll`, `bilaga`) och, vid behov, ett namn. Platsen
  skrivs i front matter och ändras inte därefter. Hittas samma källnyckel
  igen är det samma dokument på samma sökväg, även om adressen, filnamnet
  eller rubriken har ändrats.
* **Sammanträdet** är kommun, organ och datum. Hålls två sammanträden
  samma dag får det som kommer senare i källans lista ett löpnummer:
  `<datum>-2`.
* **Namnet** behövs när en plats redan är upptagen: bilagor och
  handlingar uppdelade per ärende har alltid ett namn, och ett dokument
  som kommer till en upptagen plats får ett namn ur källans rubrik eller
  filnamn. Det första dokumentet behåller sin plats utan namn.
* **En ny källnyckel på en upptagen plats** är en ny version av det
  dokument som står där om den gamla källnyckeln inte längre finns i
  källan – så blir ett justerat protokoll som publiceras som en ny nod en
  ny version av det ojusterade. Finns båda kvar i källan är det två
  dokument, och det nya får ett namn.
* **Versionen** är originalets sha256. En ny sha256 för samma dokument
  skrivs över den gamla filen; git-historiken är versionshistoriken. En
  kopia från en äldre ögonblicksbild ersätter aldrig en nyare version.
  Samma sha256 under ny adress ändrar bara `kalla_url`.
* **Ärendet** är ett attribut, inte en nivå i sökvägen: `arenden` i front
  matter listar diarienumren, är tom när dokumentet inte rör något ärende
  och `null` när det inte är känt.
* **Diariet** är en källa till mötesdokument. Diarieärenden utan
  sammanträde ingår inte i poolen.

Sökvägen blir

```
data/<kommun>/<organ>/<år>/<datum>[-<lopnr>]/<typ>[-<namn>].md
```

till exempel
`data/kungsbacka/ks/2019/2019-05-28/handlingar-arende-4-kommunbudget-2020-plan-2021-2022.md`.
Hur `<namn>` bildas ur rubriken, och var tabellerna läggs, står i
[`docs/03-ARKITEKTUR.md`](../03-ARKITEKTUR.md). Sökvägen förfinar den i
ADR-0001, alternativ F.

### Consequences

* Bra, eftersom sökvägen går att läsa och förutsäga, och samma dokument
  hamnar i samma fil från körning till körning.
* Bra, eftersom git-historiken blir versionshistoriken utan att något
  extra lagras – i linje med ADR-0001.
* Bra, eftersom de äldre per-ärende-filerna och dagens sammanslagna PDF:er
  ryms i samma modell.
* Dåligt, eftersom vem som får platsen utan namn beror på vad som hittades
  först; samma källa kan ge olika sökvägar i två pooler som byggts i olika
  ordning.
* Dåligt, eftersom en fil som kommunen lägger upp under en helt ny
  källnyckel, medan den gamla ligger kvar, blir ett nytt dokument.
* Neutralt, eftersom ärendenivån i datat får vänta på ett eget steg som
  läser ut paragrafer och diarienummer ur texten.

### Confirmation

När koden kommer:

* Ett test visar att sökvägen byggs ur organ, datum, löpnummer, typ och
  namn enligt regeln ovan, och att två bilagor eller två sammanträden
  samma dag ger olika sökvägar.
* Ett test visar att en fil med känd källnyckel men ny adress eller ny
  rubrik skriver över det befintliga dokumentet, att samma sha256 bara
  ändrar `kalla_url`, och att en ny källnyckel på en upptagen plats följer
  regeln ovan.
* CI kontrollerar att varje `.md` under `data/` ligger på den sökväg som
  `organ`, `datum`, `lopnr`, `typ` och `namn` i dess front matter ger.

## Pros and Cons of the Options

### A – Platsen i modellen: organ, datum och typ, med löpnummer vid krock

```
data/kungsbacka/ga/2025/2025-10-16/protokoll.md
data/kungsbacka/ga/2025/2025-10-16/bilaga-1.md
```

* Bra, eftersom det är enklast och sökvägen är läsbar.
* Dåligt, eftersom en utbytt fil med nytt filnamn inte går att skilja från
  ett nytt dokument; löpnummer kan då hamna på fel fil.
* Dåligt, eftersom löpnummer i stället för namn säger ingenting om vad en
  bilaga är.

### B – Platsen i modellen plus en källnyckel från adaptern

* Bra, eftersom sökvägen är läsbar och stabil.
* Bra, eftersom källnyckeln känner igen en utbytt fil hos Sitevision, där
  adressen ändras men nod-id:t består.
* Dåligt, eftersom varje adapter måste kunna ange en källnyckel, och för
  källor utan stabilt id blir den bara adressen.

### C – Innehållet (sha256) är identiteten

```
data/kungsbacka/3f9a….md      + ett index som kopplar till sammanträdet
```

* Bra, eftersom identiteten är entydig och dubbletter från olika källor
  slås ihop av sig själva.
* Dåligt, eftersom varje ändring blir ett nytt dokument; git-historiken
  visar inte vad kommunen ändrat i en fil.
* Dåligt, eftersom repot inte går att läsa utan ett index.

### D – Ärendet (diarienummer) är grundenheten

```
data/kungsbacka/arenden/KS-2019-00123/tjansteskrivelse.md
```

* Bra, eftersom ett ärende kan följas genom flera sammanträden.
* Dåligt, eftersom dagens handlingar är en sammanslagen PDF för många
  ärenden; den måste delas upp innan den kan placeras.
* Dåligt, eftersom kallelser och protokoll hör till ett sammanträde, inte
  till ett ärende.
* Dåligt, eftersom diarienummer inte alltid finns i källan.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Problemet (granskningen av grunden).** Fas 6 i PR #1 påpekade att
   organ, datum och typ inte räcker som identitet och att sökvägen krockar.
   Det blev issue #2.
2. **Förslaget (Claude).** Claude tog fram A–D och rekommenderade B:
   platsen i modellen ger läsbara sökvägar, och källnyckeln löser
   Sitevisions nya adresser. C förkastades eftersom git-historiken då inte
   visar vad som ändrats, och D eftersom dagens handlingar inte är
   uppdelade per ärende.
3. **Fyra frågor till Morgan, med Claudes rekommendation:**
   * Identitet: B (Claude rekommenderade B).
   * Ärendet som attribut i front matter eller som katalognivå: attribut
     (Claude), eftersom en ärendenivå i sökvägen bara passar de äldre
     filerna.
   * Versioner som överskrivning med git-historiken som versioner, eller
     gamla versioner som egna filer: överskrivning (Claude), som K9 redan
     säger.
   * Diarieärenden utan sammanträde i poolen eller utanför: utanför
     (Claude); diariet blir bara en källa till mötesdokument.
4. **Morgan sa ja** till alla fyra rekommendationerna 2026-10-06.
5. **Granskningen (fas 6)** visade att plats och källnyckel kunde säga
   olika saker: ett nytt filnamn gav ett nytt namn och en ny sökväg, och
   ett justerat protokoll som ny nod krockade med det ojusterade. Claude
   lade till att platsen bestäms en gång och sedan följer källnyckeln,
   och regeln för en ny källnyckel på en upptagen plats. Samtidigt
   preciserades källnyckelns form och räckvidd, att `arenden` skiljer
   tomt från okänt, och att en äldre Wayback-kopia aldrig ersätter en
   nyare version.

### Vad som inte avgörs här

* Hur front matter-schemat hålls på ett ställe – issue #9.
* Hur körningen vet vad som redan hämtats, och om det behövs ett index –
  issue #3.
* Vilken källa som går före när samma dokument finns både live och i
  Wayback – när adaptrarna skrivs.
* Hur diarienummer normaliseras (`KS 2023-00686` mot `GA-2024-00194`) –
  när ärendena läses ut.

### När beslutet bör omprövas

Om ärendenivån visar sig vara det analyserna oftast frågar efter, eller om
en plattform saknar varje form av stabil källnyckel och utbytta filer
därför ofta blir nya dokument.
