---
status: accepted
date: 2026-10-12
decision-makers: projektägaren
consulted: AI-agenten
---

# En tabell med linjer och flera tal i en cell delas efter linjerna i andra rader och efter textraderna

## Context and Problem Statement

Sedan [ADR-0016](0016-tabeller-utan-lodrata-linjer.md) är en tabell med
linjer där en cell rymmer mer än ett tal inte säker. Den blir ingen CSV,
och sidan märks `tabell-osaker`. Det hindrar att två tal sparas som ett,
men tabellerna går förlorade som data
([#60](https://github.com/moggleif/kommunhandlingar/issues/60)).

Räknat med dagens regel har 976 CSV:er i 223 av poolens dokument, skrivna
innan regeln fanns, en sådan cell. (Issuet räknade 223 CSV:er i 79
dokument med en tidigare, snävare regel; att 223 kommer igen är en
slump.) Ett stickprov visade tre mönster:

* **En vågrät linje saknas** och flera rader står i samma ruta, som
  `30 %⏎18 %⏎10 %⏎5 %`. Ungefär 60 % av CSV:erna.
* **Lodräta linjer saknas** i en rad, oftast rubrikraden, så att
  `Årets resultat 2020 2021 2022 2023` står i en enda ruta, eller flera
  tal står på samma rad i en ruta. Ungefär 35 %.
* **En rubrik och ett värde i samma ruta**, som `Bokslut 2024⏎-1,3` eller
  `2023⏎117`, vanligt i nämndernas ekonomitabeller.

Resten är spann som `0,20 - 1,90` och textrutor med datum och belopp,
som delegeringslistor.

Hur kan de här tabellerna bli CSV utan att ett enda tal hamnar i fel
cell?

## Decision Drivers

* **Ett fel tal som ser riktigt ut är värre än ett som saknas**
  ([ADR-0005](0005-konvertering-verktyg-ocr-och-kvalitet.md)). Det gäller
  också raden och kolumnen talet står i.
* **Hellre märka än gissa.** Det som inte går ihop förblir osäkert.
* **Ur textlagret och linjerna**, som resten av tabellreglerna, så att
  varje villkor går att pröva mekaniskt.
* **Inga nya beroenden.**

## Considered Options

* A – Dela efter linjerna i andra rader och efter textraderna
* B – Läsa hela tabellen som en tabell utan lodräta linjer
* C – Låta pdfplumber gissa linjerna ur texten
* D – Som i dag: tabellen fälls

## Decision Outcome

Valt: A, eftersom det bygger på det som redan står i PDF:en, linjerna i
tabellens andra rader och textradernas höjd, och fäller tabellen så
fort något inte går ihop. Reglerna står i
[ARKITEKTUR](../03-ARKITEKTUR.md#tabeller-med-linjer-och-flera-tal-i-en-cell).
I korthet:

* **Kolumnerna** är varje cells kanter i hela tabellen. En rad utan
  lodräta linjer delas efter dem, fält för fält, och ett fält som går
  över en gräns fäller tabellen. (Ändrat i ADR-0029 för text utan
  siffror i tabellens första rad.)
* **En sammanslagen cell** med ett tal delas bara när den går över
  hela tabellens bredd, eller får text i varje kolumn den täcker och
  bara har tal, eller står i första raden med ett tal i varje
  textrad och inget fält som bara är ett tal, som `Bokslut 2025 |
  Budget 2026`. Ett ensamt tal i en cell som är sammanslagen med flit
  flyttas inte till en kolumn.
* **Ett tal** är här en siffra, eller ett streck som står för ett tal.
* **Raderna** delas nerifrån: den nedersta textraden blir en egen rad när
  den står på samma höjd i varje ruta som inte är tom. Det som står
  ovanför blir en rad bara när dess textrader med tal står på samma
  höjd, och varje ruta har en textrad där. En rubrik ovanför ett värde
  blir då en rubrikrad. Samma krav gäller en rad som har en cell som
  delats efter fälten, utom tabellens första rad när dess etikett står
  på högst en textrad: den antas vara en rubrik i flera rader.
* **En rad med högst ett tal per cell** delas inte, så en rubrik i två
  rader, `Prognos⏎2024`, står kvar i en cell.

Poolens version höjs till 0.7.0. Poolen rättas när den konverteras om
([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).

### Consequences

* Bra, eftersom de vanliga ekonomitabellerna blir CSV: i stickprovets
  nio dokument blev 21 av 35 fällda tabeller CSV. Varje ord i tabellen
  står i CSV:n exakt en gång, och summaraderna stämmer där tabellen har
  sådana.
* Bra, eftersom en rubrik och ett värde i samma ruta skiljs åt, i
  stället för att stå i en cell som `Bokslut 2024⏎-1,3`.
* Bra, eftersom inget nytt beroende behövs och regeln är kort.
* Dåligt, eftersom en tabell som helt saknar lodräta linjer mellan två
  tal, som `94,3 % 96,9 %` i en ruta över hela bredden, förblir osäker.
  Där finns ingen linje att låna. (Ändrat i
  [ADR-0029](0029-tal-i-linje-utan-lodrat-linje-blir-kolumner.md).)
* Dåligt, eftersom en etikett som bryts över två rader runt talen, med
  talen mitt emellan, gör att tabellen inte delas. (Ändrat i ADR-0029
  för en rad med ett enda tal per cell.)
* Dåligt, eftersom en etikett som är längre än sin kolumn, eller en
  rubrik som står mitt över två kolumner, i en rad utan lodräta linjer
  fäller tabellen, fast en människa kan läsa den. I stickprovet gällde
  det tre av 35 tabeller. (Ändrat i ADR-0029 för text utan siffror.)
* Dåligt, eftersom ett tal i en rad som helt saknar lodräta linjer, en
  cell över hela tabellens bredd, placeras i den kolumn det står i. Det
  är så en människa läser det, men ingen linje i raden säger det.
* Dåligt, eftersom en etikett utan värden i samma ruta som en rad med
  värden kan slås ihop med den, som `Intäkter⏎Kostnader` med talen för
  intäkterna. Geometriskt är det samma sak som en etikett som bryts över
  två rader, och en tabell med linjer gör likadant i dag.
* Dåligt, eftersom tabellens första rad antas vara en rubrik när dess
  etikett står på högst en textrad, så att tal på olika höjder i den
  blir en rad. Är första raden data utan rubrik, med två värden ur olika
  rader och bara en etikett, blir de en rad. Likaså delas en rubrikcell
  som `Bokslut 2025 | Budget 2026` i första raden också när raden
  egentligen är data.
* Dåligt, eftersom en sammanslagen cell med bara tal, som `2026 | 8 132`,
  delas i varje rad, också när ett av talen är ett år som hör till
  rubriken. Det är så en människa läser raden, men ingen linje säger det.
* Dåligt, eftersom en etikett som bryts över två rader bredvid två
  staplade tal, som `Kostnader för⏎verksamheten` bredvid ett värde och
  dess andel, blir två rader med var sin halva av etiketten. Tabellerna
  utan lodräta linjer (ADR-0016) läser samma ruta likadant i dag, så en
  regel för det hör hemma i båda
  ([#97](https://github.com/moggleif/kommunhandlingar/issues/97)).
  (Ändrat i
  [ADR-0030](0030-en-ombruten-etikett-gor-tabellen-osaker.md).)
* Dåligt, eftersom ett streck räknas som ett tal, också när det är en
  punkt i en lista med en bred lucka efter. En sådan rad över hela
  bredden med punkter på olika höjder fäller tabellen, som då läses som
  en tabell utan lodräta linjer.
* Dåligt, eftersom en tabell där text eller tal sticker ut över sin
  linje, också med en enda bokstav, inte delas, eftersom ett diagram ser
  likadant ut.
* Dåligt, eftersom skyddet mot diagram bara gäller tabeller som delas.
  Ett diagram vars rutnät har högst ett tal per ruta blir en säker tabell
  som förut, och ett diagram vars etiketter står inne i rutorna delas.
* Neutralt, eftersom en kolumn kan bli tom i varje rad när två linjer
  bara finns i en del av tabellen.

### Confirmation

Tester mot en PDF i `tests/fixtures/pdf/delade.pdf` med en rubrikrad
utan lodräta linjer, tre rader i en ruta, rubrik och värde i samma
ruta, en etikett mitt emellan två tal, en etikett över en linje och ett
tal i en sammanslagen cell, och enhetstester av raddelningen, också med
tal ur olika rader och en etikett under sina tal. Facit (K20) mäts före
och efter, och mätningen på stickprovet står nedan.

## Pros and Cons of the Options

### A – Dela efter linjerna i andra rader och efter textraderna

* Bra, eftersom varje cellgräns är en linje som står i PDF:en eller en
  textrad som står på samma höjd i varje cell.
* Bra, eftersom det täcker alla tre mönstren.
* Dåligt, eftersom det inte hjälper där ingen linje finns att låna.

### B – Läsa hela tabellen som en tabell utan lodräta linjer

* Bra, eftersom reglerna redan finns (ADR-0016).
* Dåligt, eftersom de kräver att varje rad är en etikett följd av tal i
  linje. Rubrikrader och celler med rubrik och värde klarar dem inte,
  och linjerna, som säger mest, används inte.

### C – Låta pdfplumber gissa linjerna ur texten

pdfplumbers strategi `text` drar linjer där texten står i linje.

* Bra, eftersom ingen egen kod behövs.
* Dåligt, eftersom gissade linjer inte går att stämma av, och en
  tusentalsavgränsare kan bli en kolumngräns.

### D – Som i dag

* Bra, eftersom ingenting kan bli fel.
* Dåligt, eftersom några av poolens viktigaste tabeller, nämndernas
  bokslut och budgetar, förblir text.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet (projektägaren)** bad om ett stickprov för att se mönstren,
   en kontroll av att resultatet är rätt, och en fråga om ordningen mot
   facit ([#61](https://github.com/moggleif/kommunhandlingar/issues/61)).
2. **Stickprovet (agenten)** tog tolv dokument ur poolen och hämtade nio
   av dem från källan. En prototyp med kolumnerna ur hela tabellen och
   raderna efter textraderna, där alla celler måste ha samma höjder,
   gjorde 20 av 35 fällda tabeller rätt. Rubrik och värde i samma ruta
   klarade den inte, eftersom rubriken hade fler textrader än etiketten.
3. **Förslaget (agenten)** var att ta med rubrik och värde nu, låta
   tabeller helt utan lodräta linjer vänta till ett eget issue och mäta
   mot facit från #61. Projektägaren valde förslaget.
4. **Delningen nerifrån** ersatte kravet på samma höjder i alla celler:
   bara den nedersta raden behöver stå på samma höjd i varje cell, och
   det som står ovanför prövas igen. Det gav rubrik och värde, och 23 av
   35.
5. **Fälten i en cell som går över flera kolumner** avgränsas som i
   ADR-0016. En löptext har vanliga mellanslag och blir ett fält, som
   går över en gräns och fäller tabellen, i stället för att delas ord för
   ord i kolumnerna. En cell inom en kolumn skrivs i den hel, också när
   texten sticker ut över linjen. (Ändrat i ADR-0029 för text utan
   siffror i tabellens första rad.)
6. **Granskningen (fas 6)** hittade två sätt att få tal i fel rad: tre
   rader i en ruta där två saknade ett värde var, så att talen ur olika
   rader hamnade i samma rad, och en etikett strax under sina tal. Det
   som stod ovanför den avskalade raden prövades inte. Nu prövas det:
   talen ska stå på samma höjd och varje ruta ha en textrad där. Den
   hittade också att ett ensamt tal i en cell som är sammanslagen över
   två kolumner placerades efter sitt läge. Ett första förslag, att
   talet ska stå i linje med kolumnens andra tal, tog bort tabeller där
   årtalen i rubriken inte står i linje med talen, och hindrade inte
   motexemplet, där talet stod i linje. Valet blev att en sådan cell
   delas bara när den är radens enda cell, som när en rad helt saknar
   lodräta linjer, eller får text i varje kolumn den täcker, som en
   rubrik med ett år per kolumn.
7. **Andra granskningsvarvet** hittade att höjdprövningen och regeln för
   sammanslagna celler bara kände igen ett tal som stod ensamt, så att
   `ca 4 078` och `ca 8 132` slank igenom, och att "radens enda cell"
   också gällde en rad där en cell från raden ovanför täcker de andra
   kolumnerna. Nu prövas varje textrad med en siffra, och cellen ska gå
   över hela tabellens bredd. Det kostade en tabell i stickprovet, där
   en rubrik i två rader (`Budgetavvike⏎lse 2025`) har sitt år lägre än
   de andra rubrikerna: 22 av 35 i stället för 23. Hellre det än en
   regel som skiljer årtal från andra tal.
8. **Tredje granskningsvarvet** hittade att en rad över hela bredden,
   som delats efter fälten, inte prövades på höjd när ingen cell hade
   mer än ett tal, så att `Övrigt⏎Netto` fick ett tal från vardera
   raden, och att en sammanslagen cell med `Båda åren` och `8 132`
   delades så att beloppet hamnade under ett av åren. Nu prövas talen
   på höjd i varje rad under rubrikraden som har en sådan cell, och en
   sammanslagen cell som inte går över hela bredden ska ha en siffra i
   varje textrad. Rubrikraden prövas inte, eftersom rubriker i flera
   rader står på olika höjder.
9. **Fjärde granskningsvarvet** hittade att undantaget för första
   raden släppte igenom tal ur olika rader när första raden är data,
   som på en fortsättningssida, och att `2026-27: 8 132` i en
   sammanslagen cell delades eftersom etiketten har en siffra. Att pröva
   varje rad på höjd gav bara 7 av 35 tabeller, eftersom rubriker i
   flera rader står på olika höjder. Valet blev att undantaget bara
   gäller när första radens etikett står på en enda textrad; i
   motexemplen hade etiketten två. En sammanslagen cell som bara har tal
   får delas i varje rad, som `1,0 | 0,0` i en investeringstabell utan
   lodräta linjer mellan åren, medan en cell med annan text och siffror
   bara får delas i första raden.
10. **Femte granskningsvarvet** hittade att en etikett och ett tal,
    `2026-27: | 8 132`, i en sammanslagen cell i första raden räknades
    som en rubrik, eftersom båda har siffror. En rubrikcell får därför
    inget fält som bara är ett tal. Varvet visade också villkor som
    saknade test; de fick test.
11. **Sjätte granskningsvarvet** hittade att ett streck i stället för
    ett tal slapp höjdprövningen, så att två streck ur olika rader kunde
    hamna på samma rad. Ett streck prövas nu som ett tal. Varvet hittade
    också den ombrutna etiketten bredvid ett värde och dess andel. Att
    vägra dela när etikettens sista rad börjar med liten bokstav prövades,
    men då läste tabellerna utan lodräta linjer samma ruta på samma sätt,
    så regeln gav ingenting och flyttades till ett eget issue.
12. **Efter sammanslagningen** visade stickprovet för #95 att ett
    stapeldiagram, vars rutnät pdfplumber läser som en tabell, delades
    till en CSV med diagrammets etiketter. Etiketterna står över
    rutnätets linjer, så en tabell där ett ord har tecken i olika celler
    delas inte längre. Det kostade en tabell i stickprovet, där
    rubriker och tal står en bokstav över sina linjer: 21 av 35 i
    stället för 22.

### Mätningen

Stickprovet: tolv slumpvis valda dokument bland de 223, där sidorna med
en sådan CSV prövades; tre av PDF:erna gick inte att hämta hela. Av 35
fällda tabeller blev först 22 CSV och sedan 21 (punkt 12). Varje ny
CSV lästes för hand mot ordens lägen, och där tabellen har en summarad
stämdes den av. De 14 som förblev osäkra är den i punkt 12, nio
textrutor, som delegeringslistor, ärendelistor
och handlingsplaner, som ska förbli osäkra, tre där en rubrik står
över en kolumngräns, till exempel ett år mitt över två kolumner, och en
där en rubrik i två rader har sitt år på en annan höjd än de andra
rubrikernas (se punkt 7 ovan).

Facit ([ADR-0025](0025-facit-for-konverteringen.md)): en tabell till
blev rätt, skuggbudgetens, och de osäkra gick från två till en. Inga
andra mått ändrades (`tests/fixtures/facit/matt.csv`, 0.6.0 mot 0.7.0).

Ompröva beslutet när facit (#61) visar fel i delade tabeller, eller när
tabellerna utan lodräta linjer mellan talen får en egen regel.
