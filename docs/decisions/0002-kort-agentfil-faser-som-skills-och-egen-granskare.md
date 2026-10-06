---
status: accepted
date: 2026-10-06
decision-makers: Morgan
consulted: Claude
---

# Kort AGENTS.md, faserna som skills och en egen granskningsagent

## Context and Problem Statement

Repot ska byggas av både människor och AI-agenter. Agenterna behöver
instruktioner om projektets regler, var varje sanning bor och hur arbetet
går till från uppdrag till merge. Hur ska de instruktionerna organiseras så
att de följs, inte glider isär mellan verktyg, och håller när verktygen
utvecklas?

## Decision Drivers

* **Följs i praktiken.** En lång fil som alltid läses in tar plats i
  agentens sammanhang och följs sämre ju längre den blir.
* **En sanning.** Samma regler ska gälla för alla verktyg utan att kopior
  glider isär.
* **Oberoende granskning.** Den som skrev en ändring är dålig på att hitta
  felen i den.
* **Sammanhang i implementationen.** Krav, design och kod bygger på
  varandra; att lämna över mellan agenter tappar detaljer.
* **Beprövat arbetssätt.** Morgans tidigare repon har fungerande upplägg:
  `moggleif/libell` (CLAUDE.md med ägartabell och definition av klart) och
  `MorganDigitalAsyncTransparency/community` (AGENT.md med faserna 0–8,
  kontrollpunkter och synkade kopior för varje verktyg).

## Considered Options

* A – Kort AGENTS.md, faserna som skills, granskningen som egen agent
* B – Community-modellen rakt av: AGENT.md med alla faser, synkad till
  CLAUDE.md och Copilot med hook och CI
* C – En agent per fas
* D – Libell-modellen: en CLAUDE.md med regler och definition av klart

## Decision Outcome

Valt alternativ: "A – Kort AGENTS.md, faserna som skills, granskningen som
egen agent", eftersom det behåller community-modellens arbetssätt (faserna,
kontrollpunkterna, granskningen ur flera perspektiv) men bara laddar det som
behövs, och gör granskningen oberoende av den som skrev ändringen.

### Consequences

* Bra, eftersom `AGENTS.md` är kort och läses varje gång; fasernas detaljer
  läses när fasen börjar.
* Bra, eftersom `CLAUDE.md` importerar `AGENTS.md` (`@AGENTS.md`) – en fil
  att ändra, ingen synkning att hålla i takt.
* Bra, eftersom granskningen görs av en agent utan sammanhang från
  implementationen.
* Dåligt, eftersom skills och agentdefinitioner under `.claude/` är Claude
  Codes format. Andra verktyg hittar dem via tabellen i `AGENTS.md`, men
  laddar dem inte automatiskt.
* Neutralt, eftersom faserna nu ligger i fem filer i stället för en.

### Confirmation

* `CLAUDE.md` innehåller bara `@AGENTS.md`.
* Varje fil som `AGENTS.md` pekar ut finns – kontrolleras när CI byggs upp.

## Pros and Cons of the Options

### A – Kort AGENTS.md, faserna som skills, granskningen som egen agent

```
AGENTS.md                         principer, regler, var sanningen bor, fasöversikt
CLAUDE.md                         @AGENTS.md
.claude/skills/fas-*/SKILL.md     en per fas eller fasgrupp, laddas vid behov
.claude/agents/granskare.md       fas 6, egen agent utan sammanhang
```

* Bra, eftersom det som alltid läses är kort.
* Bra, eftersom granskningen blir oberoende.
* Bra, eftersom fas 1–5 görs av samma agent med hela sammanhanget.
* Dåligt, eftersom automatisk laddning bara fungerar i Claude Code.

### B – Community-modellen rakt av

* Bra, eftersom den är beprövad och fullständig.
* Bra, eftersom hook och CI håller CLAUDE.md och Copilots fil i takt.
* Dåligt, eftersom 220 rader läses in i varje session, också när bara en
  fas är aktuell.
* Dåligt, eftersom granskningen görs av samma agent som skrev ändringen.
* Dåligt, eftersom `AGENT.md` inte är filnamnet de flesta verktyg letar efter;
  `AGENTS.md` är det.

### C – En agent per fas

* Bra, eftersom varje agent har en smal roll.
* Dåligt, eftersom krav, design och kod bygger på varandra och varje
  överlämning tappar sammanhang.
* Dåligt, eftersom åtta agentdefinitioner är mer att underhålla än faserna
  är värda.

### D – Libell-modellen

* Bra, eftersom den är kort och har en tydlig ägartabell.
* Dåligt, eftersom den saknar faserna, kontrollpunkterna och granskningen.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Första versionen (Claude)** var en CLAUDE.md med projektets regler.
   Morgan tyckte att instruktionerna behövde vara bättre och frågade om
   CLAUDE.md och en agentfil hade samma innehåll och var länkade, och om de
   byggde på `moggleif/libell`.
2. **Libell-modellen (Claude).** AGENTS.md blev den enda vägledningen med
   ägartabell, regler och definition av klart enligt libell, och CLAUDE.md
   importerar den. Kraven och arkitekturen fick egna dokument, och besluten
   flyttades till MADR på Morgans begäran.
3. **Morgan: community-repots AGENT.md verkar bättre.** Den har faserna
   0–8, kontrollpunkter och en granskning ur fem perspektiv, och hålls i takt
   med CLAUDE.md och Copilot med en hook och en CI-kontroll.
4. **Morgan: men den är ett år gammal – ska vi ha en agent per fas?**
5. **Svar (Claude):** inte en agent per fas. Fas 1–5 bygger på varandra och
   vinner på samma sammanhang. Det som vinner på en egen agent är
   granskningen, eftersom en agent som inte skrev koden hittar mer. Det som
   åldrats i community-filen är att allt ligger i en fil som alltid läses in;
   i dag kan instruktioner laddas när de behövs. Claude rekommenderade A.
6. **Morgan valde A.**

### Ursprung

Principerna, faserna och granskningsperspektiven kommer ur `AGENT.md` i
`MorganDigitalAsyncTransparency/community`. Ägartabellen och regeln om att
koden har rätt kommer ur `CLAUDE.md` i `moggleif/libell`.

### När beslutet bör omprövas

Om andra verktyg än Claude Code används regelbundet i repot och behöver
ladda faserna automatiskt.
