---
status: accepted
date: 2026-10-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Kommunkonfigurationen skrivs i TOML, en fil per kommun, och hämtningens artighet står i en gemensam fil per värd

## Context and Problem Statement

K1 lovar att en kommun läggs till med bara en konfigurationsfil, och
`AGENTS.md` sade `kommuner/<kommun>.yaml`. Men YAML kräver ett beroende,
och formatet, schemat och artighetens plats var aldrig beslutade
([#6](https://github.com/moggleif/kommunhandlingar/issues/6)). Internet
Archive delas mellan kommuner, så ett intervall per kommun räcker inte för
att hålla K10, som gäller per värd. Adresserna stod dessutom i
`docs/kallor/kungsbacka.md` och i ett utkast till konfiguration.

Vilket format har konfigurationen, vad innehåller den, var konfigureras
artigheten, och vad hör hemma i `docs/kallor/<kommun>.md`?

## Decision Drivers

* **Standardbiblioteket först** (`AGENTS.md`).
* **Inga tysta fel.** Ett värde ska läsas som det skrivits.
* **Skrivs för hand**, med kommentarer och med reguljära uttryck som går
  att läsa.
* **Ingen kod för säkerhets skull.** Schemat tar bara upp det som ett
  krav använder.
* **K10 gäller per värd**, och samma värd kan vara källa för flera
  kommuner.
* **Ett faktum på ett ställe.**

## Considered Options

* A – TOML
* B – YAML
* C – JSON

Var artighetens intervall står:

* 1 – En gemensam fil, `hamtning.toml`, med ett intervall per värd
* 2 – I varje kommunfil, per källa
* 3 – Konstanter i koden

## Decision Outcome

Valt alternativ: "A – TOML" och "1 – en gemensam fil", eftersom TOML
läses av `tomllib` i standardbiblioteket och inte gissar typer, och
eftersom bara en gemensam fil kan hålla ett intervall per värd när flera
kommuner delar värd.

* **En fil per kommun**, `kommuner/<kommun>.toml`. Filnamnet är kommunens
  id, `kommun` i front matter. Schemat står i
  [03-ARKITEKTUR.md](../03-ARKITEKTUR.md#kommunkonfigurationen).
* **Organ** har id, alla namn som källorna använt, giltighetsperiod och
  föregångare. Ett organ som byter namn får ett namn till; ett organ som
  ersätts av ett nytt blir ett nytt organ med föregångare.
* **Källor** står i prioritetsordning. Varje källa har en adapter och de
  fält adaptern behöver. De fält som är gemensamma bestäms här; varje
  adapters egna fält beskrivs i arkitekturen när adaptern skrivs.
* **Mönster** är reguljära uttryck med namngivna grupper ur en fast
  uppsättning. Ett organnamn som inte finns i konfigurationen tas inte in
  utan nämns i körningens sammanfattning.
* **Artigheten** – User-Agent och intervall per värd – står i
  `hamtning.toml` i roten. Den skrivs med den artiga HTTP-klienten.
* **`docs/kallor/<kommun>.md`** beskriver hur kommunen publicerar, vad som
  är belagt och hur, vad som är att verifiera, och kända luckor.
  Konfigurationsfilen äger organ, adresser och mönster, och
  källbeskrivningen länkar dit i stället för att upprepa dem;
  exempeladresser som belägg får stå kvar.
* **Ingen riktig kommunfil skrivs nu.** `kommuner/kungsbacka.toml`
  skrivs med den första koden som läser den, när organlistan är
  verifierad mot webbplatsen; då rättas `docs/kallor/kungsbacka.md` efter
  regeln ovan.

Front matter i `data/` är fortsatt YAML. Den skrivs av koden i en fast
form och är ett annat beslut.

### Consequences

* Bra, eftersom konfigurationen inte kräver något beroende.
* Bra, eftersom datum, tal och strängar läses som de skrivits: `1384`
  inom citattecken är en sträng, och `no` är aldrig `false`.
* Bra, eftersom reguljära uttryck står inom `'…'` utan dubbla bakstreck.
* Bra, eftersom två kommuner på samma värd inte kan hämta tätare än
  värdens intervall.
* Dåligt, eftersom listor av tabeller (`[[organ]]`) tar fler rader än i
  YAML.
* Dåligt, eftersom repot får två format för strukturerad text: TOML för
  konfiguration och YAML för front matter.

### Confirmation

När koden som läser konfigurationen skrivs testas den mot en liten
kommunfil i `tests/fixtures/`: ett okänt fält, ett organ-id som inte är
ett giltigt katalognamn, en föregångare som inte finns och en okänd grupp
i ett mönster stoppar körningen innan något hämtas. Granskaren
kontrollerar att inget om en kommun står i koden.

## Pros and Cons of the Options

### A – TOML

* Bra, eftersom `tomllib` finns i standardbiblioteket sedan Python 3.11.
* Bra, eftersom typerna är explicita, och `'…'` tar reguljära uttryck
  ordagrant.
* Bra, eftersom det är samma format som `pyproject.toml`.
* Dåligt, eftersom djupt nästlade strukturer blir klumpiga. Schemat har
  högst två nivåer.

### B – YAML

* Bra, eftersom det är kortast och mest läsbart för nästlade listor, och
  det fanns ett utkast.
* Dåligt, eftersom det kräver ett beroende (PyYAML).
* Dåligt, eftersom implicita typer ger tysta fel: `NO` blir `false`,
  `1384` blir ett tal och `2025-10-16` ett datum utan att någon bett om
  det.

### C – JSON

* Bra, eftersom det finns i standardbiblioteket och är strikt.
* Dåligt, eftersom det saknar kommentarer, och bakstreck i reguljära
  uttryck måste dubblas.

### 1 – En gemensam fil per värd

* Bra, eftersom K10 gäller per värd och filen är det enda stället som ser
  alla kommuner.
* Bra, eftersom kommunfilerna blir rena kommunfakta.
* Dåligt, eftersom det är en fil till.

### 2 – Per kommun och källa

* Bra, eftersom allt om kommunen står på ett ställe.
* Dåligt, eftersom två kommuner på samma värd kan ange olika intervall,
  och tillsammans hämtar de tätare än någon av dem.

### 3 – Konstanter i koden

* Bra, eftersom det är minst.
* Dåligt, eftersom konfiguration blandas med beteende, och User-Agentens
  kontaktväg hör inte hemma i koden.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet** pekade på motsägelsen mellan `.yaml` i `AGENTS.md` och
   regeln om standardbiblioteket.
2. **Agentens rekommendation** i fas 0 var TOML, artigheten i en gemensam
   fil per värd, ingen riktig kommunfil förrän koden som läser den finns,
   och adapterspecifika fält med varje adapter. Utkastet till
   konfiguration från förstudien gicks igenom: kommunkod, tidszon,
   diarieprefix och antal samtidiga anrop ströks, eftersom inget krav
   använder dem, och fältet för prioritet ersattes av källornas ordning.
3. **Agentens invändning mot sig själv:** konfigurationens organnamn måste
   täcka hur källorna faktiskt skriver dem, till exempel "nämnden för
   Gymnasium & Arbetsmarknad" i ett protokoll och "Nämnden för Gymnasium &
   Arbetsmarknad" i handlingarna. Därför är `namn` en lista, och
   jämförelsen bortser från versaler och sammanslagna blanksteg.
4. **Ägarens beslut** 2026-10-07: alla fyra rekommendationerna.
5. **ADR-0001** nämner `kommuner/*.yaml` i sina skisser. Den detaljen
   ersätts här; beslutet om ett repo med bara text står fast.

### När beslutet bör omprövas

Om en kommun publicerar på ett sätt som kräver djupt nästlad
konfiguration, eller om ett datumformat i filnamnen inte går att fånga
med `ÅÅÅÅ-MM-DD` i ett mönster.
