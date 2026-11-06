---
status: proposed
date: 2026-11-06
decision-makers: projektägaren
consulted: AI-agenten
---

# Text på högkant tas ur flödet och skrivs sist på sidan; på en OCR-sida målas den vit och sidan läses om

## Context and Problem Statement

Skannade sidor har ofta en stämpel eller ett diarienummer på högkant i
marginalen
([#218](https://github.com/moggleif/kommunhandlingar/issues/218)).
Tesseract läser det och lägger det där det står i höjdled, mitt i ett
stycke, och bryter stycket med en tom rad
(`data/kungsbacka/ks/2026/2026-05-26/handlingar.md`, sida 779–787).
Ungefär 330 sådana ställen finns i poolen. I textlagret blir ett
sidhuvud på högkant baklänges, `REBOTKO` för `OKTOBER`, eftersom tecknen
sorteras uppifrån. Var ska sådan text stå, och hur får man bort den ur
styckena?

## Decision Drivers

* Ett stycke ska inte brytas av en stämpel.
* Ingenting utelämnas tyst: diarienummer och datum i en stämpel är
  ofta användbara.
* Tabeller med kolumnrubriker på högkant ska inte ändras.
* OCR är det långsammaste steget; sidor utan text på högkant ska inte bli
  långsammare.

## Considered Options

* Skriv texten på högkant sist på sidan; på en OCR-sida måla den vit och
  läs om sidan
* Ta bort texten på högkant
* Skriv den sist utan att läsa om OCR-sidan
* Låt den stå där den står

## Decision Outcome

Valt alternativ: "Skriv texten på högkant sist på sidan; på en OCR-sida
måla den vit och läs om sidan", eftersom projektägaren valde att texten
står sist (fas 0) och omläsningen är det som gör styckena hela.

### Consequences

* Bra, eftersom stämpeln står kvar, i rätt läsriktning, och styckena i
  OCR-texten inte längre bryts av den. Prövat på Energimarknadsinspektionens
  beslut i kommunstyrelsens handlingar 2026-05-26, sida 779: båda
  stämplarna står sist på sidan.
* Bra, eftersom bara sidor med ord på högkant läses två gånger.
* Dåligt, eftersom en OCR-sida med en stämpel tar dubbelt så lång tid.
* Dåligt, eftersom Tesseract ibland inte känner igen text på högkant
  som ord, utan som enstaka tecken eller brus; den står då kvar där den
  stod.
* Neutralt, eftersom en sida ur textlagret med tecken på högkant
  fortfarande har obekräftade tal (ADR-0038). Regeln gäller hela sidan och
  ändras inte här.
* Neutralt, eftersom tomma rader mitt i ett stycke som har andra orsaker,
  som Tesseracts styckeindelning eller radavståndet i textlagret, står
  kvar.

### Confirmation

`tests/test_hogkant.py` prövar läsriktningen med påhittade tecken,
igenkänningen med en påhittad TSV, och `tests/fixtures/pdf/hogkant.pdf`:
ett stycke med ett diarienummer på högkant, i textlagret och inskannat.
Facit körs före och efter.

## Pros and Cons of the Options

### Sist på sidan, och omläsning av OCR-sidan

* Bra, eftersom styckena blir hela och ingenting försvinner.
* Dåligt, eftersom en sida med stämpel läses två gånger med OCR.

### Ta bort texten

* Bra, eftersom det är enklast.
* Dåligt, eftersom ett diarienummer eller ett datum försvinner tyst, mot
  poolens regel.

### Sist utan omläsning

* Bra, eftersom OCR går lika fort som i dag.
* Dåligt, eftersom Tesseract redan delat stycket där stämpeln stod, så
  den tomma raden mitt i meningen står kvar.

### Låt den stå

* Bra, eftersom ingenting ändras.
* Dåligt, eftersom felet projektägaren såg står kvar.

## More Information

Fas 0 för #218 delade arbetet i två delar: spalterna (ADR-0063) och text
på högkant (det här beslutet). Agenten föreslog att texten skrivs sist,
och projektägaren valde det framför att ta bort den. Ord på högkant känns
igen på formen i Tesseracts TSV: i provet var stämplarnas ord omkring tio
gånger så höga som breda, medan ett vanligt ord är bredare än högt. Fyra
tecken krävs så att ett `I` eller ett `|` inte räknas. Beslutet bör
omprövas om omkonverteringen visar stämplar som inte känns igen.
