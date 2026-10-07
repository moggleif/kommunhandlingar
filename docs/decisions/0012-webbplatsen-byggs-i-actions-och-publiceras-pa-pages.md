---
status: proposed
date: 2026-10-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Webbplatsen byggs ur poolen i GitHub Actions och publiceras på GitHub Pages utan att checkas in

## Context and Problem Statement

Poolen ska ha en webbplats på GitHub Pages. Först kommer en statussida
som räknar vad poolen innehåller per organ, dokumenttyp och kvalitet
([#12](https://github.com/moggleif/kommunhandlingar/issues/12)), och
senare mer. Varje tal ska räknas fram ur poolen, aldrig skrivas för hand.
Var byggs sidorna, och hur kommer de ut på Pages?

## Decision Drivers

* Varje tal på sidan räknas ur poolens front matter, så sidan får inte
  kunna glida isär från datat.
* `main` tar bara emot ändringar via pull request, utan undantag.
* Inga genererade filer i repot som någon kan frestas att redigera för
  hand.
* Inga nya beroenden och inget byggsteg som behöver underhållas.

## Considered Options

* Actions bygger och publicerar med `actions/deploy-pages`
* Sidorna checkas in i `docs/` på `main`
* Sidorna checkas in på en egen gren, `gh-pages`
* En färdig sajtgenerator (Jekyll eller MkDocs)

## Decision Outcome

Valt alternativ: "Actions bygger och publicerar med `actions/deploy-pages`",
eftersom sidan då alltid är byggd ur det som ligger på `main`, ingenting
genererat checkas in och ingen extra gren behöver skyddas.

Sidorna skrivs av ett Python-kommando med bara standardbiblioteket, som
statisk HTML utan JavaScript och utan externa resurser.

### Consequences

* Bra, eftersom ett tal på sidan alltid kommer ur samma commit som datat.
* Bra, eftersom rulesetet för `main` inte behöver något undantag.
* Dåligt, eftersom Pages måste ställas om en gång till källan
  "GitHub Actions" i repots inställningar.
* Dåligt, eftersom en push med Actions egen token inte startar
  workflows: nattkörningen måste starta webbplatsbygget själv.

### Confirmation

Testerna bygger webbplatsen ur en påhittad kommun och kontrollerar
raderna och räkningen. `.github/workflows/webbplats.yml` är det enda som
publicerar, och inget under `_site/` checkas in.

## Pros and Cons of the Options

### Actions bygger och publicerar med `actions/deploy-pages`

* Bra, eftersom inget genererat checkas in.
* Bra, eftersom bygget alltid utgår från `main`.
* Dåligt, eftersom Pages-källan måste ställas om en gång.

### Sidorna checkas in i `docs/` på `main`

* Bra, eftersom Pages kan läsa `docs/` direkt, utan workflow.
* Dåligt, eftersom `docs/` redan är dokumentationen, och sidorna då
  hamnar bland den.
* Dåligt, eftersom varje ny siffra kräver en commit, och via rulesetet en
  pull request.
* Dåligt, eftersom genererad HTML i repot kan redigeras för hand och glida
  isär från datat.

### Sidorna checkas in på en egen gren, `gh-pages`

* Bra, eftersom `main` hålls fri från genererade filer.
* Dåligt, eftersom grenen måste skyddas och skrivas till av Actions,
  och historiken fylls av genererade commits.

### En färdig sajtgenerator (Jekyll eller MkDocs)

* Bra, eftersom meny, mallar och utseende finns färdiga.
* Dåligt, eftersom talen ändå måste räknas fram i Python först.
* Dåligt, eftersom det blir ett beroende och ett byggsteg till för en
  handfull sidor.

## More Information

I fas 0 föreslog AI-agenten att sidan byggs av CI och publiceras utan att
checkas in. Projektägaren bad om en publicering på GitHub Pages, med meny
och en sidfot som länkar till repot, eftersom allt senare ska samlas där,
och om att sidan bara ska räkna, utan procent: det finns ännu inget att
räkna en andel av, eftersom upptäcktslistan inte sparas
([#29](https://github.com/moggleif/kommunhandlingar/issues/29)).
Matrisen organ × år och luckorna (K7) väntar tills det finns riktig data.

Invändningen mot `docs/` var att mappen redan är dokumentationen och att
nattkörningen inte kan checka in på `main` utan pull request. En
sajtgenerator avvisades eftersom den inte sparar något arbete: talen
måste räknas i Python oavsett, och resten är en meny och en sidfot.

Beslutet bör omprövas om webbplatsen växer till något som behöver sök
eller många sidtyper.
