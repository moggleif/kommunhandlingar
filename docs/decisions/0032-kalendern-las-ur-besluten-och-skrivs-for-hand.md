---
status: proposed
date: 2026-10-12
decision-makers: projektägaren
consulted: AI-agenten
---

# Kalendern läses ur organens beslut av AI-agenten, skrivs i en CSV per kommun och visas med ett litet skript

## Context and Problem Statement

Webbplatsen ska ha en kalender med kommande sammanträden, från idag och
framåt, med en månadsvy, en lista för året och ett urval av organ
([#106](https://github.com/moggleif/kommunhandlingar/issues/106)). Var
kommer datumen ifrån, var lagras de, och hur blir sidan både statisk och
"från idag"?

Varje organ beslutar sina sammanträdesdagar för nästa år, och besluten
finns i poolen som protokoll. Formen skiljer sig mellan organen: löptext,
två spalter, en tabell, "14 & 21 januari", "9 (onsdag)", och i ett fall
en innehållsförteckning som OCR gjort oläslig. Besluten ändras i
efterhand, och kommunens mötessidor listar årets datum med ändringar och
inställda möten. Ett datum kan vara fel redan i källan: KF:s "6 mars
2027" är en lördag.

## Decision Drivers

* **Hellre märka än gissa.** Ett datum som inte går att läsa säkert ska
  synas som osäkert, inte försvinna och inte se säkert ut.
* **Varje uppgift bär sin härkomst.**
* **Ingen kod för säkerhets skull.** En tolkning av åtta format som byts
  varje år är mycket kod för ett par hundra datum om året.
* **Inget hårdkodat om en kommun.**
* **Statisk webbplats** (ADR-0012), men "från idag" ändras varje dag,
  och webbplatsen byggs bara när `main` ändras.

## Considered Options

* A – AI-agenten läser besluten och mötessidorna och skriver en CSV per
  kommun med en källa per sammanträde; sidan byggs ur CSV:n och ett litet
  skript väljer månad, dag och organ
* B – Kod tolkar besluten ur poolen när webbplatsen byggs
* C – Adaptern läser datumen från mötessidorna i nattkörningen
* D – Som A, men utan skript: sidan visar allt från byggdagen

## Decision Outcome

Valt: A, eftersom det ger rätt datum med källa och märkning nu, utan en
tolkning som måste skrivas om när formen ändras.

* **Filen** är `kalender/<kommun>.csv`, CSV med radslut LF som poolens
  tabeller (ADR-0009) men med en rubrikrad, och kolumnerna `organ`, `datum`, `tid`, `plats`, `kalla` och `osakert`.
  `kalla` är ett dokument i poolen, som sökväg under `data/<kommun>/`,
  eller en adress som börjar med `https://`. `osakert` är tomt eller
  skälet till att datumet är osäkert.
* **Källorna i ordning:** för innevarande år mötessidan, som har
  ändringarna; för kommande år organets beslut, eller förslaget som
  beslutet antog när bara förslaget har datumen, och ett senare beslut går
  före ett tidigare. Ett inställt möte står inte med.
* **Kontrollen:** bygget stoppas om ett organ inte står i kommunfilen, ett
  datum inte finns, ett sammanträde står två gånger, en källa i poolen
  saknas eller ett datum på en helg inte är märkt osäkert.
* **Färgerna:** ett organ i kommunfilen kan ha `hor_till`, id för organet
  det är utskott till. Organ som hör ihop får samma färgton, ljusare för
  utskottet. Förkortningen, organets id med versaler, står alltid i
  rutan, så att färgen aldrig bär informationen ensam.
* **Skriptet** är skrivet i sidan, utan externa resurser. Det döljer
  månader utom en, sammanträden före dagens datum i listan och organ som
  valts bort. Utan skript visas allt.

### Consequences

* Good, eftersom varje datum har en källa som går att öppna och ett skäl
  när det är osäkert.
* Good, eftersom ingen tolkningskod behöver underhållas.
* Good, eftersom sidan stämmer med dagens datum utan att byggas om.
* Bad, eftersom filen inte följer med när ett beslut ändras; den skrivs om
  för hand, och kalendern är aldrig färskare än den senaste omgången.
* Bad, eftersom en läsning av en människa eller en AI-agent kan bli fel
  utan att något fäller den, utöver kontrollerna ovan.
* Bad, eftersom webbplatsen för första gången har JavaScript, som ADR-0012
  valde bort.

### Confirmation

`tests/test_kalender.py` prövar läsningen, kontrollerna, färgerna och
sidan med en påhittad kommun, och att Kungsbackas fil går igenom
kontrollen mot poolen.

## Pros and Cons of the Options

### A – AI-agenten skriver en CSV, sidan har ett litet skript

* Good, eftersom läsningen klarar alla former, också den OCR-skadade, och
  kan jämföra beslut med mötessidan.
* Good, eftersom CSV:n går att granska rad för rad i en diff.
* Bad, eftersom någon måste göra om läsningen när nya beslut kommer.

### B – Kod tolkar besluten

* Good, eftersom nya beslut kommer med av sig själva.
* Bad, eftersom formen skiljer sig mellan organ och år; koden blir stor
  och gissar, och ett beslut som ändrar ett tidigare måste kännas igen.
* Bad, eftersom ett beslut kan nämna andra organs datum, som när en nämnd
  antecknar KF:s och KS:s.

### C – Adaptern läser mötessidorna

* Good, eftersom mötessidan har ändringarna och följs varje natt.
* Bad, eftersom sidan bara har innevarande år; kommande år saknas tills
  kommunen lägger ut dem.
* Bad, eftersom raden är fri text ("3 och 24 februari", "mötet 10 mars är
  inställt") och poolen är dokument, inte möten.

### D – Utan skript

* Good, eftersom webbplatsen förblir utan JavaScript.
* Bad, eftersom "idag" blir byggdagen, och webbplatsen byggs bara när
  `main` ändras.
* Bad, eftersom urvalet av organ inte går att göra i statisk HTML utan
  att bygga en sida per kombination.

## More Information

Agenten föreslog i fas 0 att datumen förs in för hand med en källa per
beslut. Projektägaren preciserade: agenten läser dokumenten och skriver
filen, märker osäkra datum, och stämmer av mot kommunens webbplats, där
innevarande års datum står; kommande år kommer dit senare, och till dess
gäller besluten. Datumen justeras när de nya nämnderna börjar 2027.

Projektägaren bestämde också att revisionen inte tas med, eftersom dess
sammanträden inte är offentliga, och inte heller slutna utskott som inte
publicerar handlingar och inte står i kommunfilen, som individutskotten.
Tid och plats visas där källan anger dem. Alla osäkra inläsningar märks;
de tas inte bort.

Mötessidorna går före besluten för innevarande år eftersom de visar
ändringar som annars bara står i senare protokoll, ibland inte alls, som
ett ombokat eller inställt möte. Ett inställt möte står inte med, eftersom
kalendern visar möten som ska hållas.

Skriptet är det första på webbplatsen. Alternativet att bygga om
webbplatsen varje natt löser "idag" men inte urvalet. Sidan fungerar utan
skriptet, med allt synligt, så att ingenting döljs för den som inte kör
det.

B prövas igen om kalendern ska omfatta fler kommuner och besluten visar
sig ha en form som går att lita på.
