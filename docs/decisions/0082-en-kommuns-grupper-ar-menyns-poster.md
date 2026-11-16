---
status: accepted
date: 2026-11-16
decision-makers: projektägaren, AI-agenten
---

# En enda kommuns grupper är menyns poster, och dess översikt är startsidan

## Context and Problem Statement

Med den gemensamma menyn (ADR-0081) och en pool med en enda kommun
(K58) stod kommunens namn fyra gånger överst på Kungsbacka kommuns sida:
i Giffås sajtrad, som sajtens namn i menyn, som menyns enda post och som
startsidans rubrik. Startsidan var dessutom bara en länk vidare till
översikten, som hette likadant. Statussidan och kalendern hade namnet en
gång till i sin rubrik. Temaknappen stod fast i övre högra hörnet, ovanpå
sajtraden, och på mobilen står Giffås knapp *Meny* där sedan
Giffås beslut 0014. Projektägaren bad 2026-11-16 om ett helhetsgrepp och
godkände förslaget efter ett menyträd över alla fyra sajterna.

## Decision Drivers

* Varje namn ska stå en gång; sidans rubrik säger vad sidan visar.
* Mobilen och äldre läsare: innehållet först, inga extra klick.
* Inget hårdkodat om en kommun; grupperna kommer ur kommunfilen.

## Considered Options

* Kommunens grupper som menyns poster när poolen har en enda kommun
* Behålla en undermeny per kommun, och bara byta startsidans rubrik

## Decision Outcome

Valt alternativ: grupperna som poster, eftersom en undermeny som heter
som sajten bara upprepar namnet och lägger ett klick till framför
organen.

* Med en enda kommun är posterna "Kalender" (när den finns), en
  undermeny per grupp i kommunfilen och sist "Om poolen" med statussidan
  och avvikelserna. Med flera kommuner gäller ADR-0081 som förut.
* Översikten skrivs också som `index.html`, med rubriken "Organ och
  handlingar". `<kommun>.html` finns kvar, så att gamla länkar och
  sökvägen i sidornas stig fungerar.
* Rubriker som slutade med kommunens namn gör det bara när poolen har
  flera kommuner (`kommunens()` i `webbplats/mall.py`).
* Temaknappen står sist i menyn i stället för fast i hörnet.

### Consequences

* Bra, eftersom namnet står en gång och organen nås med ett klick.
* Bra, eftersom Region Halland får samma form utan egen kod.
* Dåligt, eftersom en kommunfil med fler än fyra grupper ger fler än sex
  poster; i dag har Kungsbacka och Region Halland tre grupper var.
* Dåligt, eftersom temaknappen inte längre syns när sidan rullas; den
  står på samma ställe på varje sida.

### Confirmation

`tests/test_navigering.py` och `tests/test_webbplats.py`.
