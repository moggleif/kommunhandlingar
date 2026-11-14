---
status: proposed
date: 2026-11-14
decision-makers: projektägaren
consulted: AI-agenten
---

# Protokollen delas per paragraf när webbplatsen byggs, och `arenden` fylls med paragrafernas diarienummer vid konverteringen

## Context and Problem Statement

`arenden` är `null` i alla 4 881 dokument i poolen. Diarienumren står
bara i texten, som `§ 1 Dnr GA-2024-00224`. För att en AI eller en
människa ska kunna följa ett ärende genom protokollen behöver varje
paragraf gå att nå för sig, med rubrik, diarienummer, beslut och var den
står ([#266](https://github.com/moggleif/kommunhandlingar/issues/266),
utbrutet ur #56). Hur delas protokollen, var hamnar paragraferna, och hur
fylls `arenden`?

## Decision Drivers

* **Poolen är tillståndet** (ADR-0004, ADR-0070). Det som går att räkna
  fram ur texten ska inte lagras en gång till.
* **Hellre märka än gissa.** Ett diarienummer skrivs som det står, och ett
  beslut som inte går att avgränsa blir `null`.
* **Front matter bär dokumentets härkomst** och ska gå att läsa utan att
  bygga något. `arenden` finns redan i schemat.
* **Inget hårdkodat om en kommun.** Delningen bygger på protokollens
  allmänna form, `§` och numret först på raden.

## Considered Options

* A – Paragraferna räknas fram vid bygget till en JSON Lines-fil per
  kommun; `arenden` skrivs i front matter vid konverteringen
* B – En fil med paragraferna bredvid varje protokoll i repot
* C – Paragraferna som en lista på dokumentets rad i indexet (ADR-0070)
* D – Både paragraferna och `arenden` räknas fram vid bygget, och front
  matter lämnas `null`

## Decision Outcome

Valt: A, eftersom delningen tar sekunder när bygget ändå läser varje
dokument, samma text inte står två gånger, och `arenden` ändå följer med
dokumentet för den som läser repot.

* **Delningen** (`paragrafer.py`) är en ren funktion av texten. En
  paragraf börjar på en rad med `§` och numret, ibland efter organets
  förkortning (`BN § 1`). Efter numret får bara ett diarienummer eller
  `forts` stå. Ett ensamt `§ 4` räknas bara efter en tom rad, en
  sidbrytning eller ett datum, eftersom det annars hör till närvarolistan
  eller texten. Har flera avsnitt samma nummer gäller det sista, eftersom
  innehållsförteckningen och närvarolistan kommer först, och en
  fortsättning direkt efter läggs till.
* **Diarienumret** är det som står efter `Dnr` i paragrafens huvud, eller
  ensamt på rubrikraden. Mellanslag kring bindestrecket och mellan förled
  och år blir ett bindestreck; annars skrivs numret som det står. Organets
  förled läggs inte till där det saknas.
* **Beslutet** är texten efter raden Beslut till nästa rubrik i
  paragrafen. Når det sidans slut innan dess blir det `null`, eftersom det
  kan fortsätta på nästa sida.
* **`arenden`** är paragrafernas diarienummer, sorterade och utan
  dubbletter, och skrivs när ett protokoll konverteras. `[]` när
  paragraferna saknar diarienummer, `null` när inga paragrafer hittas och
  för alla andra typer. Datakontrollen faller när fältet inte stämmer med
  texten, och `python -m kommunhandlingar.arenden data` skriver om bara
  den raden, också i granskade dokument.
* **Paragraferna** är `<kommun>/paragrafer.jsonl` på webbplatsen och länkas
  från `llms.txt`. Hela paragraftexten följer inte med: protokollen är
  67 MB, och raden länkar till dokumentet och sidan.

### Consequences

* Good, eftersom inget nytt lagras utom `arenden`, och nattkörningen inte
  får något nytt steg.
* Good, eftersom en granskad text som ändras fångas av datakontrollen.
* Good, eftersom en AI kan följa ett diarienummer genom alla organs
  protokoll med en fil.
* Bad, eftersom paragraferna bara finns där webbplatsen finns.
* Bad, eftersom diarienumren 2020–2023 saknar organets förled
  (`2020-00327`), så att samma nummer kan finnas i två organ. Organet står
  på samma rad i paragrafindexet.
* Bad, eftersom äldre protokoll har färre diarienummer: 62 % av
  paragraferna 2013–2019, 92 % 2020–2023 och 98 % 2024–2026. Äldre
  bygglov har ärendenumret utan `Dnr` i rubriken, och det läses inte.
* Bad, eftersom en hänvisning som `§ 18` på en egen rad efter ett datum
  kan dela en paragraf fel. I 74 av 1 612 protokoll kommer numren inte i
  ordning; de flesta är dokument i delar (ADR-0049) eller paragrafer som
  justerats för sig, och inte fel.
* Neutral, eftersom orden som avslutar ett beslut (Sammanfattning,
  Beslutsmotivering, …) är svenska protokollrubriker, inte Kungsbackas. En
  kommun med andra rubriker får längre beslut tills orden läggs till.

### Confirmation

`tests/test_paragrafer.py` prövar delningen på påhittade protokoll efter
mallarna i poolen, `tests/test_arenden.py` fältet, kommandot och
datakontrollen, och `tests/test_paragrafindex.py` raderna och länken i
`llms.txt`. Mot hela poolen, när beslutet togs: 1 612 hämtade protokoll
gav 21 207 paragrafer; 53 protokoll har inga, varav 32 är revisionens
sammanträdesanteckningar. 993 protokoll räknar själva upp sina paragrafer
(`Paragrafer §§ 1-10, 12-15`), och i 877 stämmer delningen exakt. De
andra är paragrafer som justerats i ett separat protokoll, sekretess, och
uppräkningar som inte stämmer med innehållet.

## Pros and Cons of the Options

### A – Vid bygget, `arenden` i front matter

* Good, eftersom paragraferna följer poolen utan att lagras.
* Good, eftersom `arenden` går att läsa i repot och i indexet.
* Bad, eftersom `arenden` är en sanning till, som datakontrollen måste
  hålla i takt med texten.

### B – En fil bredvid varje protokoll

* Good, eftersom paragraferna följer med en klon och syns på GitHub.
* Good, eftersom filen bara ändras när protokollet ändras.
* Bad, eftersom samma text står två gånger, och en granskning eller
  omkonvertering måste skriva om båda.

### C – I indexet

* Good, eftersom en fil räcker.
* Bad, eftersom indexet redan är 7,6 MB, och en rad per dokument med
  hundratals paragrafer blir svår att läsa för ett verktyg som kapar.

### D – Allt vid bygget

* Good, eftersom inget alls lagras.
* Bad, eftersom `arenden` då står `null` i front matter, fast schemat har
  fältet och värdet går att räkna fram.

## More Information

Fas 0 mätte strukturen i alla organs protokoll 2013–2026 och föreslog A,
med fyra frågor: paragraferna vid bygget, `arenden` bara i protokollen,
diarienumret som det står, och beslutet med. Kallelser och handlingar har
andra mallar och kan bli ett eget issue.

Projektägaren frågade varför paragraferna inte skulle sparas i repot, och
om det inte vore snabbare att göra det en gång. Agenten svarade att
tiden inte avgör: en första version delade alla protokoll på ungefär elva
sekunder. Det som talar för repot är att paragraferna följer med en klon;
det som talar emot är att samma text står två gånger och måste hållas i
takt vid varje granskning och omkonvertering. Agenten erbjöd B som ett
rimligt alternativ men stod kvar vid A. Projektägaren valde A och sade ja
till de tre andra frågorna.

Att lägga till organets förled på 2020–2023 avvisades, eftersom ett ärende
från kommunstyrelsen behåller sitt nummer i nämndens protokoll och
förledet då vore en gissning.

Under bygget visade mätningen att beslutet ofta fortsätter förbi
sidfoten. Agenten valde att låta ett sådant beslut bli `null` hellre än
att klistra ihop det över sidhuvudet, som är kommunens egen mall. Det
gäller färre än två av hundra beslut.

Poolens version höjs inte. `arenden` räknas fram ur texten, som inte
ändras, och kommandot ger hela poolen fältet. En höjning skulle med
`omkonvertera = true` hämta och konvertera om varje dokument utan att
något i texten blev annorlunda (ADR-0019).
