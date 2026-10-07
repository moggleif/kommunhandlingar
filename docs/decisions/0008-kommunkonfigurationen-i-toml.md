---
status: accepted
date: 2026-10-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Kommunkonfigurationen skrivs i TOML, en fil per kommun, och artigheten per värd står i en gemensam fil

## Context and Problem Statement

K1 lovar att en kommun läggs till med bara en konfigurationsfil, och
`AGENTS.md` sade `kommuner/<kommun>.yaml`. Men YAML kräver ett beroende,
och formatet, schemat och artighetens plats var aldrig beslutade
([#6](https://github.com/moggleif/kommunhandlingar/issues/6)). Internet
Archive delas mellan kommuner, så ett intervall per kommun räcker inte för
att hålla K10, som gäller per värd. Adresserna stod dessutom i
`docs/kallor/kungsbacka.md` och i ett äldre utkast till konfiguration
utanför repot.

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

* 1 – Artigheten per värd i en gemensam fil, `hamtning.toml`
* 2 – I varje kommunfil, per källa
* 3 – Konstanter i koden

## Decision Outcome

Valt alternativ: "A – TOML" och "1 – Artigheten per värd i en gemensam
fil", eftersom TOML läses av `tomllib` i standardbiblioteket och inte
gissar typer, och
eftersom bara en gemensam fil kan hålla ett intervall per värd när flera
kommuner delar värd.

* **En fil per kommun**, `kommuner/<kommun>.toml`. Filnamnet är kommunens
  id, `kommun` i front matter. Schemat står i
  [03-ARKITEKTUR.md](../03-ARKITEKTUR.md#kommunkonfigurationen).
* **Organ** har id, alla namn som källorna använt, giltighetsperiod och
  föregångare, som i datamodellen. Ett organ som byter namn får ett namn
  till; ett organ som ersätts av ett nytt blir ett nytt organ med
  föregångare. Giltighetsperioden avgör vilket organ ett namn syftar på
  när ett nytt organ tar ett gammalt namn.
* **Källor** står i prioritetsordning. Varje källa har en adapter och de
  fält adaptern anger. De fält som är gemensamma bestäms här; varje
  adapters egna fält beskrivs i arkitekturen när adaptern skrivs, och
  ett fält som varken schemat eller adaptern har stoppar körningen.
* **Mönster** är reguljära uttryck med namngivna grupper ur en fast
  uppsättning. Datumet byggs av `ar`, `manad` och `dag`, så att en kommun
  som skriver datum i en annan ordning inte kräver någon kodändring. En
  rubrik som inget mönster eller organnamn passar tas inte in utan nämns
  i körningens sammanfattning.
* **Artigheten** – User-Agent och intervall per värd – står i
  `hamtning.toml` i roten. Den skrivs med den artiga HTTP-klienten, som
  håller intervallet per värd över alla kommuner i körningen.
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
* Bra, eftersom inga ord blir sanningsvärden av sig själva: `no`, `NO`
  och `off` är strängar, och bara `true` och `false` är sanningsvärden.
* Bra, eftersom reguljära uttryck står inom `'…'` utan dubbla bakstreck.
* Bra, eftersom två kommuner på samma värd inte kan hämta tätare än
  värdens intervall.
* Dåligt, eftersom listor av tabeller (`[[organ]]`) tar fler rader än i
  YAML.
* Dåligt, eftersom repot får två format för strukturerad text: TOML för
  konfiguration och YAML för front matter. Front matter måste också
  läsas av varje körning (ADR-0004), så repot slipper inte YAML helt;
  hur den läses avgörs när pipelinen skrivs.

### Confirmation

När koden som läser konfigurationen skrivs testas den mot en liten
kommunfil i `tests/fixtures/`: varje fel som enligt arkitekturen stoppar
körningen gör det innan något hämtas, och en rubrik som inget mönster
passar ger ingen kandidat men nämns i sammanfattningen. Granskaren
kontrollerar att inget om en kommun står i koden.

## Pros and Cons of the Options

### A – TOML

* Bra, eftersom `tomllib` finns i standardbiblioteket sedan Python 3.11.
* Bra, eftersom sanningsvärden bara skrivs `true` och `false`, och `'…'`
  tar reguljära uttryck ordagrant.
* Bra, eftersom det är samma format som `pyproject.toml`.
* Dåligt, eftersom djupt nästlade strukturer blir klumpiga. Schemat har
  högst två nivåer.

### B – YAML

* Bra, eftersom det är kortast och mest läsbart för nästlade listor, och
  det fanns ett utkast.
* Dåligt, eftersom det kräver ett beroende (PyYAML).
* Dåligt, eftersom YAML 1.1, som PyYAML följer, gör ord till
  sanningsvärden utan att någon bett om det: `NO`, `no` och `off` blir
  `false`.

### C – JSON

* Bra, eftersom det finns i standardbiblioteket och är strikt.
* Dåligt, eftersom det saknar kommentarer, och bakstreck i reguljära
  uttryck måste dubblas.

### 1 – Artigheten per värd i en gemensam fil

* Bra, eftersom K10 gäller per värd och filen är det enda stället som ser
  alla kommuner. Klienten håller sedan intervallet per värd i hela
  körningen.
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
   och adapterspecifika fält med varje adapter. Det äldre utkastet till
   konfiguration gicks igenom: kommunkod, tidszon,
   diarieprefix och antal samtidiga anrop ströks, eftersom inget krav
   använder dem, och fältet för prioritet ersattes av källornas ordning.
3. **Agentens invändning mot sig själv:** organ byter namn och ersätts,
   och källorna skriver namnen olika, till exempel "nämnden för Gymnasium
   & Arbetsmarknad" i ett protokoll och "Nämnden …" i handlingarna.
   Därför är `namn` en lista för namnbyten, jämförelsen bortser från
   versaler och sammanslagna blanksteg, och giltighetsperioden skiljer
   två organ med samma namn.
4. **Ägarens beslut** 2026-10-07: alla fyra rekommendationerna.
5. **Granskningen** (fas 6) fann att `AGENTS.md` lovar att datumformatet
   står i kommunfilen, medan schemat låste datumet till `ÅÅÅÅ-MM-DD`.
   Datumet byggs därför av grupperna `ar`, `manad` och `dag`. Granskningen
   ville också ha skrivet vad som händer när inget mönster passar, när två
   organ har samma namn och vem som avgör om ett källfält är okänt, och
   rättade påståendet om YAML:s typer: ett tal och ett datum utan
   citattecken är tal och datum i båda formaten, men bara YAML 1.1 gör
   ord till sanningsvärden.
6. **ADR-0001** nämner `kommuner/*.yaml` i sina skisser. Den detaljen
   ersätts här, och ADR-0001 har fått en anteckning; beslutet om ett repo
   med bara text står fast.

### När beslutet bör omprövas

Om en kommun publicerar på ett sätt som kräver djupt nästlad
konfiguration, eller om en kommun skriver datum med månadens namn, som
"16 oktober 2025", vilket grupperna `ar`, `manad` och `dag` inte täcker.
