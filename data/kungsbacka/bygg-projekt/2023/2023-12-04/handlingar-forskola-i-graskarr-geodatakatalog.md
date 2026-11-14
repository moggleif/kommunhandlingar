---
kommun: kungsbacka
organ: bygg-projekt
datum: 2023-12-04
lopnr: null
typ: handlingar
namn: forskola-i-graskarr-geodatakatalog
kallnyckel: sitevision:18.49ec8ddf18bfb091ca21b5ea
tidigare_kallnycklar: []
arenden: null
kalla_url: https://kungsbacka.se/download/18.49ec8ddf18bfb091ca21b5ea/1701685507849/Geodatakatalog.pdf
sha256: 375d9c677c44f58a4c07225ab4eeddd9b93d71de685c9bf7e53ef008e175d207
bytes: 94241
sidor: 5
hamtad: 2026-11-13T22:39:50+00:00
konverterad: 2026-11-13T22:39:56+00:00
pipeline: kommunhandlingar 0.11.0 / pdfplumber 0.11.10 / pdfminer.six 20260107
kvalitet: full
fel: null
kvalitet_per_sida: [ok, ok, ok, ok, ok]
tal_obekraftade: []
figurer: []
tolkade: []
granskad: null
---

<!-- sida 1 -->

Valideringsrapport        uppdateringstjänst

Uppladdning av Detaljplan för förskola med mera i Gräskär inom Kolla 5:6 i Kungsbacka stad
Sammanfattning
Resultat för validering av detaljplan.v4          2023-11-23 10:22:12

Misslyckade: 1 Varningar: 1 Systemfel: 0
Antal tester: 48 Hoppat över: 2 Tidsåtgång: 6,648

Testfall
Verksamhetsregel                                             Status
BAS-005 Ett värde för attributet versionGiltigTill ska endast finnas för historiska (ej OK
senaste) versioner av ett objekt. Det gällande objektet har således inget värde för
detta attribut.

BAS-006 Attribut med datatypen Text får inte ha ett värde som är tomt eller enbart OK
innehålla blanktecken.

BAS-010 Någon av attributen identitet och länk måste förekomma. Om båda förekommer OK
ska de peka på samma resurs.

BAS-011 Attributet från ska ha ett datum och tid som är före till. OK

BAS-012 Någon av attributen alternativGeometri och referens måste förekomma, dock ej OK
båda.

BAS-013 Någon av attributen format och beskrivningAvFormat måste förekomma, dock ej OK
båda.

DP-0002 Hela planområdet inom en detaljplan ska ha minst en användningsbestämmelse. OK
Ett undantagsfall är om det finns en egenskapsbestämmelse som reglerar enskilt
huvudmannaskap.

DP-0003 Planbestämmelseområde för användningsbestämmelser och  OK
egenskapsbestämmelser (och för äldre gällande planer administrativa
bestämmelser) får inte placeras utanför planområdet.

DP-0004 En plangeometri får endast vara en yta eller kropp.    OK

DP-0005 För en detaljplan som har status laga kraft är följande information obligatorisk. OK

1/5                     maria.malone

<!-- sida 2 -->

DP-0009 Om bestämmelsevärdet är av typ decimaltal ska attributen värdetyp och enhet OK
alltid anges.

DP-0010 I klassen Geometrimetadata är objekt obligatoriska eller ska ej anges för OK
detaljplan och planbestämmelse.

DP-0012 En planbestämmelse i en detaljplan som har status laga kraft och som har ett FAILURE
datum påbörjat efter 2021-12-31 ska ha en planbestämmelsebeskrivning.

Anm:    Bestämmelsen 5844c3b2-b612-4f71-b8ba-dfb86f97c94b saknar planbestämmelsebeskrivning

Bestämmelsen 32b833c0-abef-4ea3-860a-8750a3cd77cb saknar planbestämmelsebeskrivning
Bestämmelsen a21ad78a-c54e-40f5-95e1-33d83110d1e3 saknar planbestämmelsebeskrivning

Bestämmelsen a9e1e6ff-b136-44fe-932e-9e73f429a710 saknar planbestämmelsebeskrivning

Bestämmelsen 40aff12b-2018-4749-82b0-6c6e1aab3969 saknar planbestämmelsebeskrivning

Bestämmelsen 69070b1f-01ab-4c8e-8fd2-c5c16bbfd6cf saknar planbestämmelsebeskrivning
Bestämmelsen a99a96fb-367a-4acc-8867-738343beb83e saknar planbestämmelsebeskrivning

Bestämmelsen 6bcbd425-9744-45c6-802c-053b366fac62 saknar planbestämmelsebeskrivning

Bestämmelsen 84b92480-e3e5-44f2-a732-ee3512f60333 saknar planbestämmelsebeskrivning

Bestämmelsen e44c1cf1-8ef1-4c2f-b751-3918c92bb41d saknar planbestämmelsebeskrivning
Bestämmelsen 95d15577-2c2e-48a4-a7d2-028d1a107dac saknar planbestämmelsebeskrivning

Bestämmelsen 0ec6539f-0d34-41a2-b97f-55c7a9057f81 saknar planbestämmelsebeskrivning
DP-0014 För en detaljplan som har status laga kraft ska minst en beslutsinformation ha en OK
beslutshandling som innehåller plankarta.

DP-0015 Attributet vertikal avgränsning får endast förekomma på planbestämmelse som OK
har geometrityp punkt, linje eller yta.

DP-0016 Attributet vertikal avgränsning får endast förekomma på detaljplaner som har OK
geometrityp yta.

DP-0017 För en detaljplan som har status laga kraft ska minst en beslutsinformation OK
innehålla följande obligatoriska attribut.

DP-0018 En bestämmelsegeometri får endast vara en punkt, linje, yta eller kropp. OK

2/5                     maria.malone

<!-- sida 3 -->

DP-0019 Om bestämmelsen är en typ av teknisk anläggning ska alltid den generella OK
planbestämmelsen "Tekniska anläggningar" användas.

DP-0020 Om planbestämmelsen är en typ av teknisk anläggning ska motiv, när det anges, OK
endast innehålla "Tekniska anläggningar".

DP-0021 Om planbestämmelsen är en typ av teknisk anläggning ska OK
bestämmelseformulering samt ursprunglig bestämmelseformulering, när det
anges, endast innehålla "Tekniska anläggningar".

DP-0022 När bestämmelseformulering överensstämmer med motsvarande formulering i SKIPPED
Boverkets planbestämmelsekatalog ska variabler i bestämmelseformuleringen
anges som bestämmelsevärde. När variabel utgår ur bestämmelseformuleringen
ska inget bestämmelsevärde anges.
Anm:    Bestämmelseformuleringen följer inte Boverkets formulering i planbestämmelsekatalogen

DP-0023 För ursprungligGeometri ska varken attributen format eller typ användas. OK

DP-Krav- Uppgift om geometri ska finnas för alla detaljplaner. OK
0002

DP-Krav- Uppgift om geometri ska finnas för alla planbestämmelser. OK
0003

DP-Krav- Alla förekomster ska överensstämma med informationsmodellen. OK
0004

DP-Krav- Alla förekomster ska följa reglerna i informationsmodellen. SKIPPED
0005

Anm:    Testet kördes inte pga. att ett tidigare test misslyckades
DP-Krav- Alla förekomster ska överensstämma med värden i värdemängder (kodlistor). OK
0006

DP-Krav- Intilliggande planbestämmelser, påbörjade efter 2021-12-31, som inte ska dela OK
0011    gräns bör ha ett avstånd mellan varandra på minst 0,5 meter.

DP-Krav- Intilliggande planbestämmelser, påbörjade före 2022-01-01, som inte ska dela OK
0012    gräns bör ha ett avstånd mellan varandra på minst 2 meter.

DP-Krav- Planbestämmelser, påbörjade efter 2021-12-31, som ska dela gräns får inte ha OK
0013    ogiltiga ytglapp eller ytöverlapp.
3/5                     maria.malone

<!-- sida 4 -->

DP-Krav- Planbestämmelser, påbörjade innan 2022-01-01, som ska dela gräns får inte ha OK
0014    ogiltiga ytglapp eller ytöverlapp.

DP-Krav- Bestämmelseformulering bör överensstämma med motsvarande formulering i WARNING
0017    Boverkets planbestämmelsekatalog.
Anm:    Bestämmelsen e44c1cf1-8ef1-4c2f-b751-3918c92bb41d har en bestämmelseformulering som
inte matchar planbestämmelsekatalogen: Största byggnadsarea är [exploatering:decimaltal] m².
DP-Krav- Ingen gränslinje får korsa sig själv.                 OK
0018

DPÖ-0002 Attributet kommun måste innehålla ett gällande kommunnamn. OK

DPÖ-0003 Planens geometri måste ligga inom gällande kommun.    OK

DPÖ-0004 Värden i attributen huvudområde och underlagstyp måste stämma överens. OK

DPÖ-0005 Bestämmelserna "Största/Minsta lutning är [lutning1:decimaltal]: OK
[lutning2:decimaltal]. (Pilen pekar uppåt)" ska ha exakt två bestämmelsevärden
av typ decimaltal.

DPÖ-0006 Bestämmelser med fler än ett bestämmelsevärde av typ decimaltal kommer inte OK
att få bestämmelsevärdet sökbart.

GEO-003 För nya lägesbestämningar ska minst en av följande attribut förekomma. OK

TK-0001 En fil per objekthierarki - filen innehåller exakt ett huvudobjekt. OK

TK-0002 En fil per objekthierarki - alla underobjekt ska direkt eller indirekt peka på filens OK
huvudobjekt.

TK-0003 Om feature.id är satt så ska värdet vara objektidentiteten. OK

TK-0004 Alla referenser till objekt i modellen ska referera till objekt i hierarkin. OK

TK-0005 Detaljplanens objektidentitet måste vara samma som registrerades i forandring i OK
mottagningen.
4/5                     maria.malone

<!-- sida 5 -->

mottagningen.

TK-0006 Planens kommun måste vara samma som providerns kommun. OK

TK-0007 Om bestämmelsevärdet är av typ decimaltal ska variabelvärdet vara ett nummer. OK

TK-0008 GeometryCollections får bara innehålla geometrier av typen MultiPolygon. OK

5/5                     maria.malone
