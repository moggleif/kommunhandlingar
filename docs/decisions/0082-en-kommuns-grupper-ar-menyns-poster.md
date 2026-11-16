---
status: accepted
date: 2026-11-16
decision-makers: projektägaren
consulted: AI-agenten
---

# En enda kommuns grupper är menyns poster, och dess översikt är startsidan

## Context and Problem Statement

Med den gemensamma menyn
([ADR-0081](0081-menyn-i-projektets-gemensamma-form.md)) och en pool med en
enda kommun (K58) stod kommunens namn fyra gånger överst på Kungsbacka
kommuns sida: i Giffås sajtrad, som sajtens namn i menyn, som menyns enda
post och som startsidans rubrik. Startsidan var dessutom bara en länk
vidare till översikten, som hette likadant, och statussidan, kalendern och
stigen överst på varje sida upprepade namnet. Temaknappen stod fast i
övre högra hörnet
([ADR-0074](0074-webbplatsen-har-ljust-och-morkt-tema.md)), ovanpå
sajtraden, där Giffås knapp *Meny* står på mobilen sedan Giffås beslut
0014. Ägaren bad 2026-11-16 om ett helhetsgrepp över projektets fyra
sajter och godkände förslaget efter ett menyträd över dem. Hur ska menyn
och rubrikerna se ut när poolen har en enda kommun?

## Decision Drivers

* Varje namn ska stå en gång; sidans rubrik säger vad sidan visar.
* Mobilen och äldre läsare: innehållet först, inga extra klick.
* Inget hårdkodat om en kommun; grupperna kommer ur kommunfilen.

## Considered Options

* Kommunens grupper som menyns poster, och översikten som startsida
* Behålla en undermeny per kommun, och bara byta startsidans rubrik
* En egen förkortad menytext per grupp i kommunfilen

## Decision Outcome

Valt alternativ: "Kommunens grupper som menyns poster, och översikten som
startsida", eftersom en undermeny som heter som sajten bara upprepar
namnet och lägger ett klick framför organen.

* Med en enda kommun är posterna "Kalender" (när den finns), en
  undermeny per grupp i kommunfilen och sist "Om poolen" med statussidan
  och avvikelserna. Med flera kommuner gäller ADR-0081 som förut.
* Översikten, som sedan tillägget till ADR-0081 också är startsidan,
  får rubriken "Organ och handlingar" i stället för sajtens namn, och
  `index.html` märks som startsidan i menyn.
* Rubriker som slutade med kommunens namn, och stigen som började med
  det, gör det bara när poolen har flera kommuner (`kommunens()` och
  `oversiktsnamn()` i `webbplats/meny.py`).
* Temaknappen står sist i menyn i stället för fast i hörnet. Det ändrar
  den delen av ADR-0074; resten av det beslutet gäller.

### Consequences

* Bra, eftersom namnet står en gång och organen nås med ett klick.
* Bra, eftersom Region Halland får samma form utan egen kod.
* Dåligt, eftersom en kommunfil med fler än fyra grupper ger fler än sex
  poster; i dag har Kungsbacka tre grupper.
* Dåligt, eftersom temaknappen inte längre syns när sidan rullas, och på
  mobilen står den bakom knappen *Meny*.

### Confirmation

`tests/test_navigering.py` och `tests/test_webbplats.py`.

## Pros and Cons of the Options

### Kommunens grupper som menyns poster, och översikten som startsida

* Bra, eftersom organen nås direkt och startsidan visar innehåll.
* Dåligt, eftersom menyn ser olika ut med en och med flera kommuner.

### Behålla en undermeny per kommun, och bara byta startsidans rubrik

* Bra, eftersom koden är densamma för en och flera kommuner.
* Dåligt, eftersom menyns enda post fortfarande heter som sajten, och
  startsidan fortfarande bara länkar vidare.

### En egen förkortad menytext per grupp i kommunfilen

* Bra, eftersom korta poster, som "KF och KS", får plats på en rad.
* Dåligt, eftersom förkortningar är svårare för ovana läsare, och ett nytt
  fält i kommunfilen behövs; det kan läggas till om menyn blir för bred.

## More Information

Giffås beslut 0014 lägger sajtens namn bara i sajtraden och knappen *Meny*
där på mobilen; det här beslutet är kommunhandlingars del av samma grepp.
