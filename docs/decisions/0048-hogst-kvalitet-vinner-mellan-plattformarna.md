---
status: accepted
date: 2026-10-13
decision-makers: projektägaren
consulted: AI-agenten
---

# När samma möte finns ur arkivet från två plattformar vinner dokumentet med högst kvalitet

## Context and Problem Statement

Åren 2021–2022 finns i Internet Archive både hos Sitevision och hos
Episerver ([källorna](../kallor/kungsbacka.md#täckning)).
[ADR-0039](0039-episerver-ur-arkivet-med-mappar-och-monster.md) säger att
en kandidat inte hämtas när sammanträdet redan har ett fullständigt
dokument av samma typ från en annan plattform. Det dokument som kommer
först vinner alltså. Kandidaterna ordnas efter källnyckeln, så för ett
nytt sammanträde går `episerver` före `sitevision`. ADR-0039 säger att
ordningen ska avgöras innan fler organ får Episerver-mappar
([#154](https://github.com/moggleif/kommunhandlingar/issues/154)).

Vilket dokument ska stå kvar när båda plattformarna har mötets typ?

## Decision Drivers

* **Data ska vara rätt eller märkt.** Det bästa dokumentet ska stå i
  poolen, inte det som råkade komma först.
* **Samma möte en gång.** Ett sammanträde får fortfarande inte samma typ
  två gånger (ADR-0039).
* **Inget hämtas i onödan om och om igen.**

## Considered Options

* A – Båda hämtas, och det med högst `kvalitet` står kvar
* B – En plattform går alltid först, till exempel Sitevision
* C – Det som kommer först står kvar, som i dag

## Decision Outcome

Valt: A, eftersom ägaren valde den med högst kvalitet.

* **Jämförelsen.** En kandidat ur arkivet, för ett sammanträde vars enda
  dokument av typen är fullständigt, utan namn och ur arkivet från en
  annan plattform, hämtas och konverteras. Kvaliteten jämförs i ordningen `full`,
  `text-utan-tabeller`, `ocr`, `delvis`, `ej-konverterad`, `ej-hamtad`
  (`KVALITETER` i koden).
* **Högre vinner.** Kandidaten skrivs på dokumentets plats, och den
  gamla källnyckeln blir en tidigare källnyckel.
* **Lika eller lägre förlorar.** Dokumentet står kvar, och kandidatens
  källnyckel läggs i dess `tidigare_kallnycklar`. Därför hämtas den inte
  igen.
* **Bara en mot en.** Har sammanträdet flera dokument av typen, har
  kandidatens plattform flera kandidater av typen för sammanträdet, är
  typen `bilaga`, eller har kandidatens plattform redan prövats mot
  dokumentet (en nyckel från den står bland dess tidigare källnycklar), gäller
  regeln i ADR-0039: kandidaten hämtas inte. Annars kunde ett dokument
  ersätta ett annat dokument än sitt eget, till exempel ett av flera
  protokollsutdrag.
* **Levande källor** prövas inte. Ett dokument från en levande källa
  står kvar som i [ADR-0018](0018-wayback-sist-nyast-forst-och-bara-luckor.md).
* **Ett misslyckat försök** lämnar dokumentet orört, och nästa körning
  försöker igen.

Det ersätter regeln om samma typ i ADR-0039 när ett dokument står mot ett.

### Consequences

* Bra, eftersom poolen får det bästa dokumentet oavsett ordningen.
* Dåligt, eftersom ett möte som finns på båda plattformarna hämtas och
  konverteras två gånger, en gång per källnyckel. Det gäller 2021–2022.
* Dåligt, eftersom en kandidat som inte går att hämta, till exempel en
  kopia som alltid är kapad, hämtas varje natt så länge det andra
  dokumentet finns, eftersom ett misslyckat försök inte sparas.
* Dåligt, eftersom jämförelsen använder det befintliga dokumentets
  kvalitet från den version av konverteringen som gjorde det, och en
  förlorare prövas inte igen när konverteringen blir bättre.
* Dåligt, eftersom två lika bra dokument avgörs av vilket som kom först.
* Dåligt, eftersom en plattforms enda kandidat kan vara ett utdrag ur
  protokollet, och med högre kvalitet tar det det fullständiga
  protokollets plats. Det går inte att se utan att jämföra innehållet.

### Confirmation

`tests/test_plattformar.py` prövar att högre kvalitet tar platsen, att
lika och lägre kvalitet lämnar dokumentet, att ingen av de två hämtas
igen, att ett misslyckat försök lämnar dokumentet orört, och att flera
dokument eller kandidater av typen, bilagor, en redan prövad plattform
och levande källor inte prövas.

## Pros and Cons of the Options

### A – Högst kvalitet

* Bra, eftersom det bästa dokumentet står kvar.
* Dåligt, eftersom båda måste hämtas och konverteras för att jämföras.

### B – En plattform först

* Bra, eftersom bara ett dokument hämtas.
* Dåligt, eftersom ingen plattform alltid är bäst. En Sitevision-kopia
  kan vara kapad där Episervers är hel.

### C – Först kommen

* Bra, eftersom ingen kod ändras.
* Dåligt, eftersom ordningen efter källnyckeln avgör, och den säger
  inget om dokumentet.

## More Information

Agenten föreslog att Sitevision skulle gå före Episerver. Ägaren valde
2026-10-13 "den med högst kvalitet".
