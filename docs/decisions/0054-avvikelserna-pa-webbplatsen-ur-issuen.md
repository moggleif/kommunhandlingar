---
status: proposed
date: 2026-10-14
decision-makers: projektägaren
consulted: AI-agenten
---

# Webbplatsen visar avvikelserna i källan ur de öppna issuen, hämtade när den byggs

## Context and Problem Statement

Varje avvikelse i källan är ett eget issue med etiketten `avvikelse`,
med status på en rad
([ADR-0041](0041-avvikelser-ett-issue-per-avvikelse.md)). Issuen går inte
att läsa som en helhet, och det syns inte vilka som ska mejlas till
kommunen ([#133](https://github.com/moggleif/kommunhandlingar/issues/133)).
Hur kommer avvikelserna till webbplatsen, som i dag byggs bara ur repot
([ADR-0012](0012-webbplatsen-byggs-i-actions-och-publiceras-pa-pages.md))?

## Decision Drivers

* Ett faktum på ett ställe: issuet är avvikelsen, med sin status.
* Sidan ska gå att använda som underlag för e-posten till kommunen.
* Text ur ett issue är data och får inte bli markup.
* Inga nya beroenden eller tjänster.

## Considered Options

* A – Arbetsflödet hämtar de öppna issuen när webbplatsen byggs
* B – En fil i repot per kommun, en rad per avvikelse, som issuen pekar
  på
* C – Ett skript på sidan läser GitHubs API i besökarens webbläsare

## Decision Outcome

Valt: A, eftersom avvikelsen då står på ett enda ställe och sidan ändå är
statisk. `webbplats.yml` hämtar de öppna issuen med etiketten med
`gh api` till en fil med ett issue per rad, och
`python -m kommunhandlingar.webbplats` läser filen. Arbetsflödet får
rätten att läsa issues och körs också när ett issue öppnas, ändras,
stängs eller byter etikett, så att sidan följer issuen.

Sidan `avvikelser.html` står i menyn och grupperar avvikelserna efter det
senaste steget på statusraden: först de som ska meddelas kommunen, sedan
de som väntar på kommunen och sist de som är kvar att undersöka. Ett
issue vars statusrad inte går att läsa står under en egen rubrik, i
stället för att utelämnas eller gissas. Stängda issues är avslutade och
står inte med. Avsnitten "Vad som skiljer sig" och "Belägg" renderas med
samma markdown-it-py som dokumenten
([ADR-0023](0023-dokumenten-pa-webbplatsen-med-markdown-it-py.md)), med
HTML avslaget; mallens kommentarer tas bort först.

Sidan är en för alla kommuner, och varje post säger sin kommun ur
issuets fält. Fältet är fri text, så ingen kod behöver känna kommunens
namn.

### Consequences

* Bra, eftersom ett issue som ändrar status flyttar på sidan utan att
  något annat behöver ändras.
* Bra, eftersom sidan är statisk som resten av webbplatsen.
* Dåligt, eftersom webbplatsen inte längre byggs bara ur repot: bygget
  beror på GitHubs API, och en lokal körning behöver en fil med issues,
  som kan vara tom.
* Dåligt, eftersom varje ändring av ett issue med etiketten bygger om
  hela webbplatsen. Ändringar av issues utan etiketten startar också
  arbetsflödet; hämtningen tar då samma avvikelser igen.
* Dåligt, eftersom mallens form bara hålls av den som skriver issuet. Ett
  issue som inte följer den syns under "Utan läsbar status".

### Confirmation

`tests/test_avvikelser.py` prövar tolkningen av mallen och statusraden,
grupperingen och att text ur ett issue inte blir markup.

## Pros and Cons of the Options

### A – Hämtas när webbplatsen byggs

* Bra, eftersom issuet är den enda platsen för avvikelsen och dess
  status.
* Dåligt, eftersom bygget får ett beroende utanför repot.

### B – En fil i repot

* Bra, eftersom webbplatsen fortsatt byggs bara ur repot, som kalendern
  och målen.
* Dåligt, eftersom varje avvikelse och varje statusändring skrivs på två
  ställen, som glider isär.

### C – Ett skript i webbläsaren

* Bra, eftersom sidan alltid visar det senaste.
* Dåligt, eftersom sidan blir tom utan JavaScript eller när GitHubs
  gräns för anrop utan inloggning nås, och texten ur issuen måste
  renderas säkert i webbläsaren.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Projektägaren** bad om en sida med de felaktigheter som hittats och
   borde meddelas kommunen, och att de kända felen skulle läggas in så
   att de kom med. De lades in som issues #134–#143.
2. **Projektägaren** bad sedan AI-agenten göra klart det som var öppet,
   utan avstämningar.
3. **AI-agenten** rekommenderade A. B bryter mot att ett faktum bara står
   på ett ställe, och C gör sidan beroende av besökarens webbläsare.

Ompröva beslutet om avvikelserna flyttar från issuen, eller om bygget
behöver gå utan nätverk.
