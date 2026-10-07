---
status: accepted
date: 2026-10-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Hämtningen görs med standardbiblioteket och en egen läsning av robots.txt, och kandidatlistan skrivs som JSON

## Context and Problem Statement

Upptäckten (steg 1) har en adapter men ingen hämtning
([#29](https://github.com/moggleif/kommunhandlingar/issues/29),
[ADR-0011](0011-sitevision-organ-fran-sidan-datum-och-rattelser.md)).
Hämtningen ska vara artig (K10): följa `robots.txt`, säga vem vi är,
hålla avstånd till varje värd och backa vid 429 och 5xx. Fälten i
`hamtning.toml` skulle bestämmas när klienten skrevs
([ADR-0008](0008-kommunkonfigurationen-i-toml.md)). Kungsbackas server
stänger dessutom ibland anslutningen utan att svara
([docs/kallor/kungsbacka.md](../kallor/kungsbacka.md)), och dess
`robots.txt` använder jokertecken (`Disallow: /*91.*`).

Hur hämtar vi, hur läser vi `robots.txt`, och i vilket format lämnar
upptäckten kandidatlistan till steg 2?

## Decision Drivers

* **Standardbiblioteket först** (AGENTS.md).
* **Artig hämtning** är en regel som inte förhandlas, och den ska gälla
  `robots.txt` som kommunerna faktiskt skriver den.
* **Hellre stanna än gissa:** en halv kandidatlista får inte se hel ut.
* **Ingen kod för säkerhets skull.** Upptäckten hämtar bara HTML-sidor.

## Considered Options

För `robots.txt`:

* `urllib.robotparser` ur standardbiblioteket
* En egen läsning enligt RFC 9309
* Ett bibliotek, till exempel Protego

För kandidatlistan:

* JSON
* CSV
* Ingen fil: steg 1 och 2 körs i samma process

## Decision Outcome

Valt: hämtning med `urllib.request`, **en egen läsning av `robots.txt`
enligt [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309)**, och
**kandidatlistan som JSON**. Det enda som standardbiblioteket inte klarar
är jokertecknen i `robots.txt`, och de ryms i ett fyrtiotal rader.

* **`hamtning.toml`** har två fält: `user_agent`, som anger vem vi är och
  hur vi nås, och `intervall`, det minsta antalet sekunder mellan anrop
  till samma värd, räknat från slutet av det förra anropet. Intervallet
  är 5 sekunder.
* **`robots.txt`** hämtas en gång per värd och körning. Gruppen för vår
  produkt (User-Agent fram till första `/` eller mellanslag) gäller,
  annars gruppen `*`. Den längsta regel som träffar avgör, och `Allow`
  vinner vid lika längd. `*` och `$` stöds. Svarar `robots.txt` 4xx
  finns inga begränsningar. Går den inte att hämta efter de nya försöken
  hämtas ingenting från värden.
* **Nya försök:** vid 429, 5xx, en anslutning som stängs utan svar och en
  tidsgräns. Väntan är 5 sekunder och fördubblas, eller så lång som
  `Retry-After` anger i sekunder. Efter fyra försök är orsaken
  `http-<kod>`, `tomt-svar` eller `tidsgrans`. Andra 4xx försöks inte
  igen. En stängd adress ger orsaken `robots`. Antalet försök och
  väntetiderna står i koden: de är beteende, inte artighet.
* **Kandidatlistan** skrivs till `<arbetskatalog>/<kommun>.kandidater.json`
  som en lista i ordningen från K13, med kandidatens fält och datumet som
  `ÅÅÅÅ-MM-DD`. Sammanfattningen skrivs ut: kandidater per organ och
  varje fil som inte blev kandidat, med orsak (K2).
* **En källsida som inte går att hämta stoppar upptäckten** innan
  listan skrivs.

### Consequences

* Bra, eftersom `Disallow: /*91.*` stänger det protokoll den träffar,
  också i Python 3.12, där `urllib.robotparser` läser `*` som ett vanligt
  tecken och släpper igenom det.
* Bra, eftersom inget nytt beroende behövs.
* Bra, eftersom steg 2 läser listan utan att tolka datum eller ordning
  på nytt, och listan kan sparas som underlag efter en körning.
* Dåligt, eftersom läsningen av `robots.txt` är vår egen och måste
  testas mot RFC:ns regler.
* Dåligt, eftersom en omdirigering följs av `urllib` utan att målet
  prövas mot `robots.txt` eller intervallet. Kungsbackas sidor och filer
  omdirigeras inte i dag.

### Confirmation

`tests/test_robots.py` prövar grupperna, jokertecknen, den längsta
regeln och Kungsbackas `robots.txt`. `tests/test_klient.py` prövar
intervallet, de nya försöken och `robots.txt` mot en lokal server, med
en låtsasklocka. En körning mot kungsbacka.se redovisas i pull requesten.

## Pros and Cons of the Options

### `urllib.robotparser`

* Bra, eftersom den finns i standardbiblioteket.
* Dåligt, eftersom den i Python 3.12, som CI kör, inte förstår `*` och
  `$`. Kontrollerat 2026-10-07: `/x91.pdf` släpps igenom av 3.12 men
  stängs av 3.13.16. Beteendet beror alltså på patchversionen.

### En egen läsning enligt RFC 9309

* Bra, eftersom beteendet är detsamma i varje Python-version och följer
  standarden.
* Dåligt, eftersom det är kod vi själva måste underhålla.

### Protego

* Bra, eftersom det är vältestat och följer RFC 9309.
* Dåligt, eftersom det är ett beroende för ett fyrtiotal rader.

### JSON

* Bra, eftersom datum, ordning och tecken följer med utan tolkning, och
  `json` finns i standardbiblioteket.
* Dåligt, eftersom den inte öppnas i ett kalkylark.

### CSV

* Bra, eftersom den går att öppna i ett kalkylark.
* Dåligt, eftersom allt läses tillbaka som text.

### Ingen fil

* Bra, eftersom det blir ett steg mindre.
* Dåligt, eftersom stegen enligt arkitekturen är egna kommandon som
  läser föregående stegs utdata, och listan inte kan granskas i
  efterhand.

## More Information

I fas 0 föreslog AI-agenten `urllib` med `urllib.robotparser`, JSON och
intervallet 5 sekunder, och att stora filer strömmas till disk först i
steg 2, eftersom upptäckten bara hämtar HTML. Projektägaren svarade
"kör" på rekommendationerna.

När klienten skrevs visade det sig att `urllib.robotparser` i Python
3.12 inte förstår jokertecken, medan 3.13.16 gör det. Kungsbackas regel
`/*91.*` skulle alltså släppas igenom i CI men inte i molnmiljön. Det
bryter mot K10 på ett sätt som inte syns. Projektägaren hade gett
klartecken att arbetet går vidare under natten enligt agentens
rekommendationer, och agenten valde den egna läsningen framför ett
beroende. Beslutet bör omprövas om projektet ändå tar in ett bibliotek
för hämtning.

Fem sekunder valdes eftersom upptäckten bara gör 18 anrop (17 sidor och
`robots.txt`) och servern redan är långsam. I steg 2, med över tusen
filer, är det tiden för själva överföringen som dominerar.
