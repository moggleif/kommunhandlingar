---
status: accepted
date: 2026-11-15
decision-makers: projektägaren
consulted: AI-agenten
---

# Menyn följer projektets gemensamma form och laddar sajtraden från Giffå

## Context and Problem Statement

Poolen är en av tre sajter i projektet, tillsammans med Giffå och
Kungsbacka i siffror, och alla ligger på samma värd. Projektägaren vill
att läsaren ska kunna gå mellan sajterna och att menyerna ska följa samma
form. Poolens meny var en lång rad länkar per kommun som inte nådde
organen och inte ledde till de andra sajterna. Hur ska menyn byggas så att
den hänger ihop med de andra sajterna utan att poolen äger något av dem?

## Decision Drivers

* Läsaren ska kunna gå mellan projektets sajter från varje sida.
* Samma form för menyn på alla sajter, med högst sex poster och en nivå
  undermeny.
* Poolen ska inte veta något om de andra sajterna utöver var menyn
  hämtas.
* Utan JavaScript ska menyn fortfarande fungera.

## Considered Options

* Ladda Giffås `sajter.js` och `sajter.css` och skriva menyn i den
  gemensamma formen
* Skriva länkarna till de andra sajterna direkt i poolens meny
* Låta menyn vara som den är

## Decision Outcome

Valt alternativ: "Ladda Giffås `sajter.js` och `sajter.css`", eftersom
listan över sajterna och menyns utseende då står på ett ställe, i Giffå
(beslut 0013 där), och poolen bara skriver sin egen meny i formen:
`nav.sajtmeny` med sajtnamnet och en lista där en post är en länk eller en
`details` med undermenyn. Varje kommun blir en enda post, en undermeny
med översikten, kalendern, statussidan och organen grupp för grupp, och
sist står avvikelserna. Så ryms fem kommuner inom sex poster.

### Consequences

* Bra, eftersom en ny sajt i projektet syns överallt utan ändring här.
* Bra, eftersom organen nås från varje sida.
* Dåligt, eftersom en sjätte kommun kräver ett nytt beslut om menyn.
* Dåligt, eftersom poolens sida laddar ett skript från en annan sajt på
  samma värd; går den inte att nå står menyn som en lista utan sajtraden.

### Confirmation

`tests/test_navigering.py` prövar menyns form och att varje sida laddar
`/giffa/sajter.css` och `/giffa/sajter.js` (K57).
