---
status: proposed
date: 2026-10-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Nattkörningen checkar in på en egen gren, och datat når `main` genom en PR med samma kontroller som all annan ändring

## Context and Problem Statement

[ADR-0006](0006-schemalagd-korning-i-actions-och-data-direkt-till-main.md)
lät den schemalagda körningen checka in data direkt till `main`. Efter
det fick `main` ett ruleset: ändringar bara genom PR, kontrollen "Ren kod
och tester" måste gå igenom, och ingen får undantas. Projektägaren sa
uttryckligen "inga undantag". Därmed kan körningen inte pusha till `main`,
och ADR-0006 förutsåg det bland sina konsekvenser
([#37](https://github.com/moggleif/kommunhandlingar/issues/37)).

En PR som Actions öppnar med sin egen token startar inga workflows
([GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token),
kontrollerat 2026-10-07), så den obligatoriska kontrollen körs aldrig på
den och PR:en kan inte mergas. Hur når körningens data `main`?

## Decision Drivers

* **Rulesetet ändras inte, och ingen kontroll hoppas över** (projektägaren).
* **Bara färdiga och kontrollerade körningar** når poolen (K11).
* **Inget arbete går förlorat** när en körning inte mergas samma natt.
* **Enkelhet:** så få hemligheter som möjligt (ADR-0006).

## Considered Options

* A – Körningen pushar till `main` och undantas i rulesetet
* B – Körningen pushar en egen gren; en människa eller agent öppnar och
  mergar PR:en
* C – Som B, men körningen öppnar PR:en med en egen token (GitHub App eller
  finkornig token som hemlighet) och slår på automatisk merge
* D – Datat stannar på en gren som aldrig mergas

## Decision Outcome

Valt: **B nu, och C när en token finns.** Körningen checkar in på en
egen gren, `nattkorning/<datum>-<körningens id>`, och datat når `main`
genom en PR, där "Ren kod och tester" kör samma datakontroller som
körningen redan kört. Tills en token finns öppnar och mergar en människa
eller AI-agenten PR:en. C är samma flöde utan handpåläggning och
rekommenderas som nästa steg.

* **Varje körning får en egen gren.** En körning som inte mergas finns
  kvar, och nästa körning skriver aldrig över den.
* **Varje körning börjar från `main`.** En omergad körnings dokument
  hämtas därför igen nästa natt. Det kostar tid men aldrig rätt, och
  upphör med C.
* **Datakontrollerna körs i körningen och i CI** på varje PR, så en
  datacommit får samma kontroller som all annan ändring.
* **Webbplatsen byggs om** av mergen till `main`, som startar
  `webbplats.yml` som vanligt.
* "Gren, inte `main`" i AGENTS.md gäller nu utan undantag.

Det som ADR-0006 i övrigt bestämde gäller: Actions varje natt och för
hand, tidsbudgeten och dess hårda gräns, att ett fel stoppar körningen
utan att något checkas in, och att pipelinen är ett vanligt kommando.

### Consequences

* Bra, eftersom rulesetet gäller utan undantag och varje datacommit går
  genom samma obligatoriska kontroll som koden.
* Bra, eftersom ingen ny hemlighet behövs för att komma igång.
* Bra, eftersom varje körning får en sida med diff och kontroller.
* Dåligt, eftersom poolen bara växer när någon mergar, tills C finns.
* Dåligt, eftersom körningar som inte mergas hämtar samma dokument igen.
* Dåligt, eftersom grenarna blir kvar tills någon tar bort dem efter merge.

### Confirmation

`.github/workflows/nattkorning.yml` har schema och `workflow_dispatch`,
en `concurrency`-grupp utan `cancel-in-progress`, `contents: write` bara i
jobbet, kör datakontrollerna och kontrollerar att bara `data/` ändrats
innan grenen pushas. `kontroll.yml` kör datakontrollerna. Den första
körningen redovisas i sin PR.

## Pros and Cons of the Options

### A – Undantag i rulesetet

* Bra, eftersom ADR-0006 gäller oförändrat.
* Dåligt, eftersom projektägaren uttryckligen sagt "inga undantag".
* Dåligt, eftersom Actions egen token inte kan undantas utan en GitHub App.

### B – Egen gren, PR som en människa eller agent öppnar och mergar

* Bra, eftersom det fungerar i dag utan hemlighet.
* Bra, eftersom PR:en startar "Ren kod och tester" när den öppnas av
  någon annan än Actions egen token.
* Dåligt, eftersom poolen står still när ingen mergar.

### C – Egen gren, PR med egen token och automatisk merge

* Bra, eftersom det går av sig självt varje natt med alla kontroller.
* Dåligt, eftersom det kräver en GitHub App eller token som hemlighet,
  som måste skötas och förnyas.

### D – En datagren som aldrig mergas

* Dåligt av samma skäl som i ADR-0006: två sanningar, och pipelinen läser
  sitt tillstånd från `main`.

## More Information

Projektägaren bad om att nattkörningen skulle komma igång samma natt,
med PR och merge för varje issue, och sa att rulesetet inte får ändras
och att ingen kontroll får hoppas över. En token kunde inte läggas in
samma kväll. AI-agenten valde därför B, som kräver varken hemlighet eller
undantag, och rekommenderar C så snart en token finns: då öppnar jobbet
PR:en med den och slår på automatisk merge, och "Ren kod och tester"
avgör. Projektägaren har inte sett valet, så ADR:n står som `proposed`. När
den accepteras får ADR-0006 status `superseded by ADR-0015`.

ADR-0006 lät det pågående dokumentet vid den hårda gränsen tas bort eller
återställas från `main`. Med tidsbudgeten i koden avbryts ett dokument
aldrig medan det skrivs, så det finns inget att städa: avbryts det före
skrivningen har det inte skrivit något, och nås gränsen under skrivningen
skrivs det klart (docs/03-ARKITEKTUR.md, "Körning och incheckning").
