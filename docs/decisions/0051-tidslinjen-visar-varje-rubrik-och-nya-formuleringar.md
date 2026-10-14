---
status: accepted
date: 2026-10-14
decision-makers: projektägaren
consulted: AI-agenten
---

# Tidslinjen visar varje rubrik på en egen rad och markerar nya formuleringar

## Context and Problem Statement

Tidslinjen på målsidan
([ADR-0050](0050-malsidan-visas-som-tidslinje-och-malkort.md)) har en rad
per mål med den senaste rubriken, och ett namnbyte är en liten punkt med
en pekruta. Ett mål som hette "From Great to Excellent" 2018–2021 står då
under rubriken det fick 2024, redan från 2018. Läsaren ser inte att målet
bytt namn, och tror att nämnden beslutat något den inte beslutat det året
([#156](https://github.com/moggleif/kommunhandlingar/issues/156)). Hur
ska tidslinjen visa att ett mål bytt rubrik och utvecklats?

## Decision Drivers

* **Ingen falsk bild.** Ett år ska aldrig visas under en rubrik som målet
  inte hade det året.
* **Utvecklingen ska synas utan att läsaren pekar** på något.
* **Varje uppgift bär sin härkomst**, och en tolkad koppling är märkt.

## Considered Options

* En rad per rubrik, grupperad per mål, som en trappa
* En rad per mål, med rubriken skriven i bandet där den byts
* En rad per mål, med de tidigare rubrikerna under den senaste i rubrikkolumnen

## Decision Outcome

Valt: en rad per rubrik, grupperad per mål, eftersom den är den enda som
visar vilken rubrik som gällde vilket år, också för långa rubriker och på
en smal skärm.

* Raderna står i den ordning rubrikerna först står, och varje rad efter
  den första är märkt med en pil och "Ny rubrik år:" för skärmläsare.
  En tolkad rubrik är märkt tolkad, och en rubrik av ett annat slag än
  målets senaste har sitt slag utskrivet. Ett slagbyte med samma rubrik
  är ingen ny rubrik.
* Varje rad har sitt eget band med årets status, så att trappan visar
  när målet bytte rubrik.
* Ett år då ingen av rubrikens formuleringar står året innan med
  formulering har en punkt med den nya formuleringen i pekrutan.
  Radbrytningar, versaler och punkter räknas inte, och olika
  formuleringar inom samma år markeras inte, eftersom ett dokument kan
  citera en förkortad formulering.
  Hela formuleringen står i kortets historik.
* Urvalet och korten är som förut; alla rader för ett mål hör till samma
  kort.

### Consequences

* Good, eftersom tidslinjen inte längre visar en senare rubrik för ett år
  då målet hette något annat.
* Good, eftersom namnbytena syns som en trappa utan pekrutor.
* Bad, eftersom tidslinjen får fler rader: för GA 47 i stället för 33.

### Confirmation

`tests/test_malkort.py` prövar att varje rubrik har sin rad och sitt
band, att en ny rubrik står under den förra och att en ny formulering
markeras.

## Pros and Cons of the Options

### En rad per rubrik, som en trappa

* Good, eftersom varje år står under den rubrik det hade.
* Bad, eftersom ett mål tar flera rader.

### Rubriken skriven i bandet

* Good, eftersom målet har en rad.
* Bad, eftersom rubrikerna är långa och inte ryms i ett band som är ett
  eller två år brett.

### Tidigare rubriker i rubrikkolumnen

* Good, eftersom namnen syns utan pekruta.
* Bad, eftersom det inte syns vilket år som hörde till vilken rubrik.

## More Information

Projektägaren påpekade att tidslinjen dolde hur målen bytt namn och
utvecklats, och att den då ger en felaktig bild. AI-agenten valde
trappan, som den enda som knyter varje år till sin rubrik.
