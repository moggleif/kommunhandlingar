---
status: accepted
date: 2026-10-06
decision-makers: projektägaren
consulted: AI-agenten
---

# Ett repo med bara text – PDF:en raderas efter konvertering

## Context and Problem Statement

Datapoolen ska hämta alla kallelser, handlingar och protokoll från
kommunfullmäktige, kommunstyrelsen och samtliga nämnder i Kungsbacka, så långt
bakåt som möjligt, och konvertera dem till Markdown och CSV för dataanalyser.
Den ska gå att återanvända för andra kommuner.

Var ska poolen bo – kod, text och originalfiler – och behöver originalen
(PDF:erna) sparas alls?

## Decision Drivers

* **Volym.** Ungefär 12 organ × 10 möten om året × (handlingar 3–33 MB +
  protokoll + kallelse) ger 1–3 GB PDF per år och kommun, 10–30 GB med tio
  års historik. Texten är ungefär 1–5 % av det, alltså några hundra MB.
* **GitHubs gränser.** Max 100 MB per fil, rekommenderat under 1 GB per repo.
  Git LFS ingår med 1 GB lagring och 1 GB bandbredd i månaden; mer kostar.
* **`moggleif/politik` har egna regler.** En statisk webbplats som bara
  använder standardbiblioteket, där allt i `data/` ska kunna byggas om av ett
  skript och CI kör facit mot sidorna. Poolen behöver PDF- och OCR-verktyg och
  nattliga körningar.
* **Generalitet.** Poolen ska vara kommunoberoende.
* **Enkelhet.** Så få konton, tjänster och repon som möjligt.
* **Spårbarhet.** Varje text ska gå att föra tillbaka till sin källa.

## Considered Options

* A – Nytt kodrepo, originalen i objektlagring, texten i releaser
* B – Två nya repon (kod + text), originalen i objektlagring
* C – Allt i politik-repot
* D – Nytt kodrepo, allt data i ett Hugging Face-dataset
* E – Nytt repo med originalen i Git LFS
* F – Ett repo med bara text, PDF:en raderas efter konvertering

## Decision Outcome

Valt alternativ: "F – Ett repo med bara text", eftersom datat är texten och
inte PDF:erna. Det är det enda alternativet som klarar sig med ett repo och
inga externa konton, och spårbarheten löses med källänk och sha256 i varje
fil i stället för med lagrade original.

### Consequences

* Bra, eftersom allt – kod, konfiguration, beslut och text – finns på ett
  ställe, går att diffa och söka i på GitHub, och git-historiken visar vad
  kommunen har ändrat i sina handlingar.
* Bra, eftersom det inte kostar något och inte kräver några konton.
* Dåligt, eftersom en konvertering inte kan göras om utan att originalet
  hämtas på nytt. Kommunen visar bara ungefär två år bakåt, så för äldre
  dokument kan det bli svårt.
* Dåligt, eftersom kod och text har samma synlighet. Repot är publikt
  (ägarens beslut: protokoll och handlingar är offentliga).
* Neutralt, eftersom repot växer för varje kommun; texten kan brytas ut per
  kommun senare om det behövs.

### Confirmation

* Inga PDF:er eller andra binärer i repot – kontrolleras i CI. Små
  testfixturer under `tests/fixtures/` är undantagna (förtydligat
  2026-10-06, se AGENTS.md); de är testdata, inte poolens data.
* Varje `.md` under `data/` har front matter med källänk, sha256, tider för
  hämtning och konvertering, pipelineversion och kvalitet – kontrolleras i CI. Ett dokument
  som inte gick att hämta saknar original och därmed sha256 (förtydligat
  2026-10-06, se ADR-0004).

## Pros and Cons of the Options

### A – Nytt kodrepo, originalen i objektlagring, texten i releaser

```text
github.com/<ägare>/<repo>        kod, kommuner/*.yaml, docs/
objektlagring (R2 / B2 / S3)     ra/<sha256>.pdf
GitHub Releases                  text-<datum>.tar.zst, index
```

* Bra, eftersom kodrepot är litet och originalen skalar fritt.
* Bra, eftersom releaser är tydliga ögonblicksbilder att peka på.
* Dåligt, eftersom texten inte går att diffa eller bläddra i på GitHub.
* Dåligt, eftersom det kräver ett konto för objektlagring och hemligheter i CI.
* Neutralt, eftersom ~30 GB i R2 kostar runt 0,45 USD i månaden.

### B – Två nya repon (kod + text), originalen i objektlagring

```text
github.com/<ägare>/<repo>        kod, konfiguration, docs/
github.com/<ägare>/<repo>-data   text och tabeller
objektlagring                    ra/<sha256>.pdf
```

* Bra, eftersom texten är diffbar och originalen finns kvar för omkonvertering.
* Bra, eftersom datarepot kan vara privat medan koden är publik.
* Dåligt, eftersom det blir tre ställen att hålla i takt.
* Dåligt, eftersom det kräver ett konto för objektlagring.

### C – Allt i politik-repot

* Bra, eftersom inget nytt repo behövs och datat ligger nära sidorna som
  ska använda det.
* Dåligt, eftersom det krockar med repots regler: beroenden, CI som kör facit
  vid varje ändring, och kravet att `data/` byggs om av skript.
* Dåligt, eftersom repot är byggt kring Kungsbacka; generaliteten blir en
  intention snarare än en struktur.

### D – Nytt kodrepo, allt data i ett Hugging Face-dataset

* Bra, eftersom originalen och texten ligger på ett ställe gjort för stora
  dataset, gratis för publika dataset, och Parquet kan läsas direkt.
* Dåligt, eftersom det är ytterligare en plattform med egna villkor.
* Dåligt, eftersom texten inte syns i samma historik som koden.

### E – Nytt repo med originalen i Git LFS

* Bra, eftersom det är ett repo utan externa konton.
* Dåligt, eftersom 30 GB i LFS kostar och varje CI-körning äter bandbredd.
* Dåligt, eftersom LFS är svårt att bli av med senare.

### F – Ett repo med bara text, PDF:en raderas efter konvertering

```text
github.com/<ägare>/<repo>
  src/, kommuner/*.yaml, docs/
  data/<kommun>/<organ>/<år>/<datum>/<typ>.md   + tabeller som .csv
```

(Konfigurationen är `kommuner/*.toml` sedan 2026-10-07, se ADR-0008.)

PDF:en hämtas till en temporär katalog, konverteras och raderas. Front
matter i varje `.md` bär källänk, sha256, tider, pipelineversion och
kvalitet per dokument och per sida (se `docs/03-ARKITEKTUR.md`). Även ett
dokument som inte gick att konvertera får en `.md` med status, så att
luckan syns.

* Bra, eftersom det är ett repo, inga konton och ingen kostnad.
* Bra, eftersom allt är diffbart och sökbart.
* Bra, eftersom kvalitetsnivån i varje fil visar vad som går att använda.
* Dåligt, eftersom omkonvertering kräver ny hämtning.
* Neutralt, eftersom originalet kan arkiveras i Internet Archive vid
  hämtning, vilket gör det troligare att det går att hitta igen. Det är en
  hjälp, inget krav.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Första förslaget (agenten): kod och data isär.** Utgångspunkten var att
   10–30 GB PDF inte ryms i git. Alternativ A–E togs fram, som alla sparar
   originalen någonstans. Agenten rekommenderade B.
2. **Ägaren: varför spara PDF:erna alls?** Hämta PDF:en tillfälligt,
   konvertera, skriv källänk och datum för hämtning och konvertering överst
   i Markdown-filen och radera PDF:en. Då återstår bara text, och ett repo
   räcker. Det blev alternativ F.
3. **Invändning (agenten): konvertering kan behöva göras om.** Verktygen för
   OCR och tabeller blir bättre, och kommunen visar bara ~2 år bakåt. Agenten
   föreslog att osäkra PDF:er skulle sparas tills vidare.
4. **Ägaren: det som inte går att konvertera går inte att använda som
   data.** Det som behövs är att varje fil anger hur väl konverteringen
   lyckades. Vad ska originalet då vara till?
5. **Svar (agenten): två användningar** – konvertera om senare, och belägga en
   siffra som ifrågasätts. Båda klaras med källänk och sha256. Förslaget att
   spara osäkra PDF:er ströks, och kvalitetsnivå per dokument och sida lades
   till.
6. **Överenskommet: konvertera om senare = leta upp filen igen senare.**
   Projektet lagrar inga PDF:er.
7. **Synlighet.** Ägaren beslutade att repot är publikt, eftersom
   handlingarna är offentliga. Agenten påpekade att namn räknas som
   personuppgifter i GDPR; att kunna ta bort ett dokument som kommunen själv
   drar tillbaka räcker som hantering. (Ersatt 2026-10-07, se ADR-0007:
   poolen tar inte bort dokument som kommunen drar tillbaka.)

Agenten rekommenderade till slut F. Beslutet fattades av ägaren 2026-10-06.

### Vad som återanvänds från moggleif/politik

Politik-repot byggs inte vidare för poolen. Det som går att återanvända
kopieras in och anpassas – se README.

### När beslutet bör omprövas

Om omkonvertering av äldre dokument visar sig vara vanlig och originalen inte
går att hitta igen, eller om texten för flera kommuner blir för stor för ett
repo.
