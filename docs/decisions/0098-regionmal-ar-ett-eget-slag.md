---
status: accepted
date: 2026-11-20
decision-makers: projektägaren
consulted: AI-agenten
---

# Regionens fullmäktigemål är ett eget slag, regionmål

## Context and Problem Statement

Region Hallands sidor byggs med samma kod som kommunens. Fullmäktiges mål
läses ur regionens årsredovisningar och uppföljningsrapporter och står på
regionfullmäktiges sida om mål och direktiv. Målfilens slag är
`nämndmål`, `kommunmål`, `fokusområde` och `direktiv` (ADR-0044,
ADR-0056), och slaget syns på sidan: i urvalet, tidslinjen och antalet
per år. Med slaget `kommunmål` stod det "Kommunmål" på regionens sida,
vilket är fel. Vilket slag ska en regions fullmäktigemål ha?

## Decision Drivers

* Sidan ska säga vad målen är, med regionens ord.
* Ingen konfiguration för en enda skillnad i ett ord; inget hårdkodat om
  en viss region.
* Så lite kod som möjligt.

## Considered Options

* Ett nytt slag `regionmål`.
* Etiketten för `kommunmål` ur kommunfilen.
* Slaget `nämndmål` för fullmäktiges mål.

## Decision Outcome

Valt alternativ: "Ett nytt slag `regionmål`", eftersom det är en rad i
listan över slag och en i ordlistan för antalet, och målfilen säger då
vad målet är. Regionmål beter sig som kommunmål utan fokusområden: ett
fokusområdes huvudmål är fortfarande ett kommunmål. Regionens fokusområden
står inte som egna rader, eftersom de i kommunen är underordnade
kommunmålen, medan regionens fokusområden är överordnade målen.

### Consequences

* Bra, eftersom regionens sida säger Regionmål och kommunens sida är
  oförändrad.
* Dåligt, eftersom en kommun i princip kan skriva `regionmål`; bygget
  hindrar det inte.

### Confirmation

`tests/test_regionmal.py` läser en rad med slaget och prövar att sidan
säger Regionmål i urvalet, tidslinjen och antalet per år, och inte kommunmål eller nämndmål.

## Pros and Cons of the Options

### Etiketten för `kommunmål` ur kommunfilen

* Bra, eftersom slagen förblir fyra.
* Dåligt, eftersom en konfigurationsflagga för ett enda ord är en
  abstraktion för ett fall, och målfilen skulle säga kommunmål om något
  som inte är det.

### Slaget `nämndmål`

* Bra, eftersom ingen kod ändras.
* Dåligt, eftersom fullmäktige inte är en nämnd och sidan blir lika fel.

## More Information

Regionens fullmäktigemål lades först in som `kommunmål` (regionhalland
PR #50), och projektägaren ville ha rätt ord på sidan. Kravet är K71.
