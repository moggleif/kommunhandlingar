---
status: proposed
date: 2026-10-14
decision-makers: projektägaren
consulted: AI-agenten
---

# Nattkörningen öppnar sin PR med en egen token och mergas automatiskt när kontrollerna gått igenom

## Context and Problem Statement

Nattkörningen hittar och hämtar nya sammanträden varje natt, men enligt
[ADR-0015](0015-nattkorningen-pa-egen-gren-och-pr.md) når datat `main`
först när en människa eller AI-agenten öppnar och mergar en PR från
körningens gren. Poolen står därför still när ingen gör det, och omergade
grenar hämtar samma dokument igen natt efter natt
([#163](https://github.com/moggleif/kommunhandlingar/issues/163)).

En PR som Actions öppnar med sin egen token startar inga workflows, så den
obligatoriska kontrollen "Ren kod och tester" körs aldrig på den (ADR-0015).
Hur når nya sammanträden `main` utan handpåläggning, utan att rulesetet
ändras eller någon kontroll hoppas över?

## Decision Drivers

* **Rulesetet ändras inte, och ingen kontroll hoppas över** (projektägaren).
* **Nya sammanträden ska in i poolen av sig själva.**
* **Enkelhet:** en hemlighet, inga nya verktyg.
* **Hemligheten exponeras så lite som möjligt**: hämtningen läser
  innehåll från nätet och ska inte kunna nå den.

## Considered Options

* A – Finkornig token som hemlighet; körningen öppnar PR:en och slår på
  automatisk merge
* B – En GitHub App vars token körningen hämtar och använder på samma sätt
* C – Ett eget lördagsjobb som öppnar och mergar veckans grenar
* D – Som i dag: en människa eller AI-agenten öppnar och mergar PR:en

## Decision Outcome

Valt: **A**, alternativ C i ADR-0015. Körningen pushar sin gren som förut
med Actions egen token. Om hemligheten `NATTKORNING_TOKEN` finns öppnar
ett sista steg en PR från grenen med den och slår på automatisk merge
(merge-commit, som för all annan ändring). PR:en startar "Ren kod och
tester", och GitHub mergar när kontrollen är grön. Mergen startar
webbplatsbygget som vanligt.

* **Bara det sista steget får hemligheten**, som miljövariabel. Den står
  inte i utcheckningen, så hämtningen och konverteringen kan inte läsa den.
* **Utan hemlighet** beter sig körningen som i ADR-0015: grenen pushas och
  sammanfattningen säger att någon ska öppna en PR.
* **Faller kontrollen** står PR:en kvar öppen och omergad, och nästa natt
  börjar från `main` som förut. En människa eller agent tittar på den.
* Projektägaren skapar token och hemlighet och slår på automatisk merge i
  repots inställningar; hur står i `docs/01-BIDRA.md`.

### Consequences

* Bra, eftersom nya sammanträden når poolen och webbplatsen dagen efter de
  publicerats, utan att någon gör något.
* Bra, eftersom rulesetet gäller utan undantag och samma kontroll avgör.
* Bra, eftersom omergade grenar som hämtar samma dokument igen upphör.
* Dåligt, eftersom token måste förnyas när den går ut; då faller sista
  steget och körningen syns som misslyckad, men grenen är pushad.
* Dåligt, eftersom PR:erna står som öppnade av den som äger token.

### Confirmation

`.github/workflows/nattkorning.yml` ger `NATTKORNING_TOKEN` bara till
steget som öppnar PR:en, och det steget hoppar över allt utom
sammanfattningen när hemligheten saknas. Den första körningen med
hemligheten ska ge en PR som mergas av sig själv när kontrollen är grön.

## Pros and Cons of the Options

### A – Finkornig token och automatisk merge

* Bra, eftersom det är en hemlighet och två `gh`-kommandon.
* Bra, eftersom token kan begränsas till det här repot och till innehåll
  och PR:er.
* Dåligt, eftersom den är knuten till ett personligt konto och går ut.

### B – GitHub App

* Bra, eftersom den inte är knuten till en person och inte går ut.
* Dåligt, eftersom den kräver en app, två hemligheter och ett steg som
  hämtar token, vilket är mer att sätta upp och sköta än problemet kräver.

### C – Eget lördagsjobb som mergar veckans grenar

* Bra, eftersom det motsvarar önskan om ett jobb på lördagar.
* Dåligt, eftersom grenarna innehåller samma dokument och krockar med
  varandra; bara den nyaste kan mergas.
* Dåligt, eftersom det ändå kräver samma token, och poolen ligger efter
  upp till en vecka.

### D – Som i dag

* Bra, eftersom ingen hemlighet behövs.
* Dåligt, eftersom poolen står still när ingen mergar.

## More Information

Projektägaren bad om ett jobb som varje lördag letar efter nya dokument
som saknas, eftersom nya möten hålls hela tiden. AI-agenten visade att
nattkörningen redan gör det varje natt och att nya dokument går före
omkonverteringen, men att datat bara når `main` när någon mergar. Agenten
föreslog därför tre vägar: låta körningen merga själv, en kontroll på
lördagar som jämför kalendern med poolen, eller ingenting. Projektägaren
valde att låta körningen merga själv.

Ett lördagsjobb (C) avvisades eftersom det ändå behöver en token och en
vecka av omergade grenar med samma dokument inte går att merga tillsammans.
En GitHub App (B) är det robustare valet på sikt, men en finkornig token
räcker för ett repo och kan bytas mot en app utan att flödet ändras.

Att hemligheten hålls borta från utcheckningen var agentens val: steg 2
läser PDF:er och sidor från nätet, och en token i `.git/config` skulle vara
läsbar för allt som körs där.
