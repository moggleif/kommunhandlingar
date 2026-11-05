---
status: proposed
date: 2026-11-05
decision-makers: projektägaren
consulted: AI-agenten
---

# Löptext i spalter läses spalt för spalt med XY-snitt över textlagrets rader

## Context and Problem Statement

Projektägaren läste dokument i poolen och såg att bildtexter och annat
klipps in mitt i meningar
([#218](https://github.com/moggleif/kommunhandlingar/issues/218)).
Textlagret läses med pdfplumber i `layout=True`, som tar en rad i taget
över hela sidans bredd. På en sida med två eller tre spalter flätas
raderna från spalterna ihop. I en månadsrapport i nämndens handlingar
(`data/kungsbacka/ga/2025/2025-11-20/handlingar.md`, sida 175) står
bildtexten under ett porträtt i mittspalten mitt i en mening i vänster
spalt. En försiktig sökning hittade minst
77 sidor i 29 dokument där det syns. Hur ska en sida med spalter läsas,
utan att sidor utan spalter ändras?

## Decision Drivers

* Texten ska gå att läsa: en mening ska inte avbrytas av en annan spalt.
* Talraderna och tabellerna får inte påverkas; tal är data, text är
  sammanhang (ADR-0005).
* Sidor utan spalter, som de flesta protokoll och tjänsteskrivelser, ska
  ge samma text som i dag.
* Inget nytt beroende, och en regel som går att pröva med små påhittade
  sidor.

## Considered Options

* XY-snitt över textlagrets radstycken, bara där löptext står bredvid
  löptext
* pdfminers layoutanalys (textrutor ordnade med `boxes_flow`) för alla
  sidor
* pdfminers layoutanalys bara för sidor med spalter
* Ett annat konverteringsverktyg med läsordning (till exempel ett med en
  modell för sidlayout)

## Decision Outcome

Valt alternativ: "XY-snitt över textlagrets radstycken", eftersom det
löser felet på de sidor där det finns, lämnar övriga sidor orörda, och
klarar sig med pdfplumber och några små funktioner.

### Consequences

* Bra, eftersom spalterna står hela och en bildtext står på egna rader
  i sin spalt. Prövat på två riktiga handlingar: av 255 sidor i nämndens
  handlingar 2025-11-20 delades 24 (månadsrapporten och ett reportage),
  och av 950 sidor i kommunstyrelsens handlingar 2026-05-26 ungefär 120
  (budget i spalter, årsredovisningar, revisionsberättelser och en
  plankarta). Varje delad sida som granskades hade spalter.
* Bra, eftersom en sida som inte delas läses exakt som förut, och
  uppställningen finns kvar inne i varje spalt, så att talrader i en
  spalt fortfarande blir kodblocket `osaker-tabell`.
* Bra, eftersom facit (K20) ger samma mått som version 0.9.0.
* Dåligt, eftersom två spalter vars stycken slutar på samma höjd kan
  delas vågrätt där först, så att övre halvan av båda spalterna kommer
  före den undre. Varje del står hel, men en mening som fortsätter från
  vänster spalts nedre del till höger spalts övre står i fel ordning.
* Dåligt, eftersom kort text i spalter, med få eller korta rader, läses
  som förut, och spalter med en lucka smalare än en radhöjd delas inte.
  Trösklarna står i [Spalter](../03-ARKITEKTUR.md#spalter).
* Neutralt, eftersom poolen inte konverteras om nu; det görs en gång när
  konverteringen är bra (projektägarens beslut).

### Confirmation

`tests/test_spalter.py` prövar snitten med påhittade radstycken och
`tests/fixtures/pdf/spalter.pdf`: två spalter med en mening som fortsätter
i nästa spalt och en bildtext, tre spalter, ett brevhuvud med talrader och en
ärendelista som ska läsas som förut. Facit körs före och efter.

## Pros and Cons of the Options

### XY-snitt över textlagrets radstycken

Orden fogas till radstycken som bryts vid en lucka på minst en radhöjd.
Radstyckena delas lodrätt där inget korsar och båda sidor är löptext,
annars vågrätt vid den största luckan.

* Bra, eftersom villkoret om löptext skyddar brevhuvuden, ärendelistor och
  talrader.
* Bra, eftersom rutorna läses med samma `layout=True` som i dag.
* Dåligt, eftersom trösklarna är satta efter de två handlingarna och kan
  behöva justeras.

### pdfminers layoutanalys för alla sidor

* Bra, eftersom pdfminer redan följer med pdfplumber, och dess textrutor
  läste månadsrapportens spalter hela i ett prov.
* Dåligt, eftersom uppställningen försvinner: talraderna kan inte längre
  kännas igen, och texten på alla sidor ändras.
* Dåligt, eftersom ordningen av rutorna (`boxes_flow`) i provet varvade
  stycken ur två spalter.

### pdfminers layoutanalys bara för sidor med spalter

* Bra, eftersom bara sidor med spalter ändras.
* Dåligt, eftersom textrutorna byggs ur pdfminers egna objekt och inte ur
  pdfplumbers urval utan tabellerna; texten i tabellerna skulle komma
  med två gånger.
* Dåligt, eftersom det ändå krävs en egen regel för vilka sidor som har
  spalter.

### Ett annat konverteringsverktyg

* Bra, eftersom verktyg med en layoutmodell läser också svåra sidor.
* Dåligt, eftersom det är ett stort beroende och en ny konvertering av
  allt, när felet bara gäller en liten del av sidorna (ADR-0005).

## More Information

Agenten hittade felet genom att söka i poolen efter stycken som slutar
mitt i en mening och fortsätter efter något annat, och provade sedan
alternativen på två hämtade handlingar. Fas 0 tog också upp text på
högkant, som stämplar och diarienummer i marginalen på skannade sidor;
den hanteras i en egen ändring, där projektägaren valde att texten
skrivs sist på sidan. Projektägaren valde också att poolen konverteras
om senare. Beslutet bör omprövas om en granskning av poolen efter
omkonverteringen visar sidor med spalter som inte delas, eller sidor utan
spalter som delas.
