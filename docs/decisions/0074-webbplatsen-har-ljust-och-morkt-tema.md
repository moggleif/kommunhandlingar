---
status: proposed
date: 2026-11-14
decision-makers: projektägaren
consulted: AI-agenten
---

# Webbplatsen följer läsarens ljusa eller mörka inställning, med en knapp i övre högra hörnet som minns valet

## Context and Problem Statement

Webbplatsen har bara ljust tema: färgerna står som fasta värden i
sidmallen, i målsidans och spårsidornas stil, i kalendern och i några
SVG-figurer. Projektägaren vill ha mörkt tema med
([#271](https://github.com/moggleif/kommunhandlingar/issues/271)), och en
knapp för det som alltid syns i övre högra hörnet. Hur ska temat väljas,
och hur ska färgerna skrivas så att båda temana går att läsa?

## Decision Drivers

* **Läsarens inställning först.** Den som har mörkt i systemet ska få
  mörkt utan att göra något.
* **Ett ställe för färgerna**, så att ett nytt tema inte blir en ny
  uppsättning stilar på varje sida.
* **Statusfärgerna läsbara i båda**, och färgen bär aldrig informationen
  ensam (ikonerna har olika form).
* **Sidan fungerar utan skript**, och inga nya beroenden.

## Considered Options

* Färgerna som CSS-variabler med `light-dark()`, `color-scheme` efter
  läsarens inställning, och en knapp som sätter temat och minns det i
  webbläsaren
* Samma variabler, men bara läsarens inställning och ingen knapp
* Två stilmallar, ljus och mörk, som knappen byter mellan
* Ett mörkt tema genom att vända färgerna med ett filter

## Decision Outcome

Valt: CSS-variabler med `light-dark()` och en knapp som minns valet.

* **Färgerna** står som variabler i sidmallens stil (`webbplats/mall.py`),
  var och en med ett ljust och ett mörkt värde i `light-dark()`. Målsidans
  och spårsidornas stil, kalendern och SVG-figurerna använder variablerna
  i stället för egna värden. `color-scheme: light dark` gör att
  webbläsaren också ger länkar, knappar och rullister rätt färg.
* **Knappen** "Mörkt tema" står fast i övre högra hörnet på varje sida och
  är nedtryckt när temat är mörkt. Ett klick byter tema; valet sparas i
  webbläsarens `localStorage` och gäller på alla sidor och vid nästa
  besök. Ett litet skript i sidans `<head>` sätter det sparade temat
  innan sidan ritas, så att den inte blinkar.
* **Utan skript** följer sidan läsarens inställning, och knappen, som
  inte kan göra något, visas inte.
* **Kalenderns organrutor** behåller sina ljusa färgtoner och mörk text i
  båda temana, eftersom tonerna är det som skiljer organen åt.

### Consequences

* Good, eftersom läsaren får sitt tema utan att välja och kan byta när
  hen vill.
* Good, eftersom en ny färg skrivs en gång med båda värdena.
* Bad, eftersom `light-dark()` kräver en webbläsare från 2024 eller
  senare; en äldre visar ljust tema.
* Bad, eftersom valet bara gäller i den webbläsaren, och den som rensar
  den får läsarens inställning igen.

### Confirmation

`tests/test_webbplats.py` prövar att varje sida har knappen och skriptet,
och att stilarna inte har några färger utanför variablerna.
Läsbarheten prövas för hand i båda temana på en målsida, en spårsida, en
dokumentsida och kalendern.

## Pros and Cons of the Options

### Variabler med `light-dark()` och knapp som minns valet

* Good, eftersom en variabel har båda värdena på samma rad.
* Good, eftersom knappen bara behöver sätta `color-scheme`.
* Bad, eftersom ett skript och `localStorage` tillkommer.

### Bara läsarens inställning

* Good, eftersom inget skript behövs.
* Bad, eftersom den som vill läsa mörkt på en ljus dator inte kan.

### Två stilmallar

* Good, eftersom de fungerar i äldre webbläsare.
* Bad, eftersom varje färg står två gånger och kan glida isär.

### Vända färgerna med ett filter

* Good, eftersom det är en rad.
* Bad, eftersom statusfärgerna byter ton, grön blir lila, och ikonerna
  inte längre betyder samma sak.

## More Information

Issuet föreslog att hela webbplatsen ska följa läsarens inställning, och
AI-agenten rekommenderade i fas 0 att avstå från en knapp. Projektägaren
ville ha en knapp som alltid syns i övre högra hörnet. En knapp som
glömmer valet på nästa sida vore värdelös på en webbplats med många
sidor, så valet sparas i webbläsaren; ingenting skickas någonstans.
`light-dark()` valdes framför en mediefråga och en attributväljare per
tema, eftersom de kräver att varje mörkt värde står två gånger, en gång
för inställningen och en gång för knappen.
