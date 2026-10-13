---
status: proposed
date: 2026-10-13
decision-makers: projektägaren
consulted: AI-agenten
---

# Text som inte går att läsa i ordning ger obekräftade tal

## Context and Problem Statement

Granskningen av #91 hittade sidor i poolen vars textlager inte går att
läsa i ordning
([#119](https://github.com/moggleif/kommunhandlingar/issues/119)). I en
lista över bidrag flyter cellen `Lokalt aktivitetsstöd` in i nästa
kolumn, och datumet där är ritat ovanpå slutet av ordet. pdfplumber
sorterar tecknen efter läget och skriver `aktivitetsstö2d0225-05-21`. På
en annan sida står två spalter text roterade, och tecknen blandas till
rader som `eoaertrct ,h ok fvcru…`. Sidorna var märkta `ok`, och deras
tal räknades som bekräftade. Hur känns en sådan sida igen, och hur ska
den märkas?

## Decision Drivers

* Ett tal som kan ha blandats ihop med annan text ska inte räknas som
  bekräftat: hellre märka än gissa.
* Kursiv stil, tät spärrning och fetstil som ritats två gånger får
  tecknens rutor att överlappa utan att texten är i oordning; sådana sidor
  ska inte märkas.
* Märkningen ska passa i det som redan finns, utan ett nytt fält.

## Considered Options

* A – Sidans tal blir obekräftade, som vid oläsliga tecken
* B – En ny sidkvalitet, till exempel `text-osaker`
* C – Sidan läses med OCR, som när textlagret är oläsligt

## Decision Outcome

Valt: A, eftersom det är samma märkning som en sida med oläsliga tecken
redan får: sidan står i `tal_obekraftade`, och texten läses ur
textlagret som förut. En sida har text i oordning när något tecken är
roterat, eller när två tecken på samma rad täcker mer än halva det
smalare av dem utan att stå intill varandra i textlagret och utan att
vara samma tecken. Grannar i textlagret får överlappa, eftersom kursiv
stil ger bredare rutor än tecknen; text som ritats ovanpå annan text
kommer från ett annat ställe i textlagret. Regeln står i
`konvertering/ordning.py` och prövas på sidan innan mellanslag tas bort
ur talen ([ADR-0036](0036-mellanslag-inne-i-en-siffra-tas-bort.md)).

Poolens version höjs till 0.8.9. Poolen rättas när den konverteras om
([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

### Consequences

* Bra, eftersom ett stickprov på tio handlingar ur poolen, 1 975 sidor
  med textlager, märker sex sidor och ingen annan. Det är de två sidorna
  i issuet och fyra sidor med roterad text: ett avtal med en liggande
  tabell som läses en bokstav per rad, en tabell med roterade
  kolumnrubriker som står baklänges i cellerna (`rah eslekivvA`) och två
  diagram med roterade axeltitlar.
* Bra, eftersom regeln inte märker kursiv Garamond, där tecknens rutor
  överlappar på nästan varje rad. En enklare regel, som bara mätte
  överlappet, märkte tolv andra sidor i stickprovet: elva med kursiv text
  och en tabell där en cell går ända fram till talet i nästa, som
  `centrum800`, och texten ändå står i ordning.
* Dåligt, eftersom en sida med en roterad axeltitel i ett diagram får
  obekräftade tal fast resten av texten är i ordning. Diagrammet märks
  redan som figur.
* Dåligt, eftersom sidans kvalitet fortfarande är `ok` eller
  `tabell-osaker`. Att texten är i oordning syns bara i
  `tal_obekraftade`, inte i texten.
* Facit ändras inte: ingen av dess sidor har text i oordning.

### Confirmation

`tests/test_ordning.py` prövar regeln på påhittade tecken efter sidorna i
issuet, med kursiv stil och dubbelritad fetstil som inte ska märkas.

## Pros and Cons of the Options

### A – Obekräftade tal

* Bra, eftersom det är den märkning som redan finns för oläsliga tecken,
  och texten finns kvar.
* Dåligt, eftersom textens kvalitet inte märks.

### B – En ny sidkvalitet

* Bra, eftersom också texten märks.
* Dåligt, eftersom en ny kvalitet ändrar front matter-schemat,
  datakontrollen, dokumentets kvalitet och webbplatsen för sex sidor av
  2 000.

### C – OCR

* Bra, eftersom OCR läser det som syns, och överlagrad text blir ett ord
  i taget.
* Dåligt, eftersom OCR körs utan orienteringsdetektering: en liggande
  tabell blir `ej-konverterad`, och sidans text försvinner. Tabellerna
  blir dessutom inga CSV:er.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet** kom ur granskningen av #91. Projektägaren bad AI-agenten ta
   det utan avstämningar och välja det rekommenderade alternativet vid
   varje vägval.
2. **AI-agenten** mätte först överlappet mellan tecken intill varandra på
   en rad. Det träffade tolv sidor till, de flesta med kursiv text, där
   tecknens rutor är bredare än tecknen. Att också kräva att tecknens mitt passeras
   träffade fortfarande kursiven. Det som skiljer överlagrad text från
   kursiv är ordningen i textlagret: kursiva tecken som överlappar är
   grannar där, medan text som ritats ovanpå kommer från ett annat
   ställe. Med det villkoret märktes bara sidorna i issuet.

Ompröva beslutet om poolen visar många sidor där bara en axeltitel är
roterad, eller om textens kvalitet behöver märkas för sig.
