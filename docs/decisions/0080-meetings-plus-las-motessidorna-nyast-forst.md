---
status: accepted
date: 2026-11-16
decision-makers: projektägaren
consulted: AI-agenten
---

# Meetings Plus läses mötessida för mötessida, med bilagorna var för sig och det nyaste mötet först

## Context and Problem Statement

Region Halland publicerar sina handlingar på Formpipe Meetings Plus
(<https://politik.regionhalland.se/>), som ingen av poolens adaptrar läser
([#292](https://github.com/moggleif/kommunhandlingar/issues/292)). Regionens
data läggs i ett eget repo som installerar den här koden, så adaptern
skrivs här och läser allt regionspecifikt ur kommunfilen. Hur ska
plattformen läsas, och i vilken ordning ska de omkring 15 000 filerna tas?

Uppmätt 2026-11-15:

* 17 publika organ. Organets sida listar alla dess möten på en gång,
  2013–2027, utan bläddring; till exempel 73 för driftnämnden Hallands
  sjukhus.
* Mötets sida har kallelsen och protokollet, och under varje ärendepunkt
  bilagorna, en PDF per bilaga, ofta 10–40 per möte. Varje fil har en
  länk som öppnar den och en som laddar ner den, och det finns zip-paket
  för hela mötet och varje punkt.
* På äldre mötessidor står bilagorna en gång till under protokollet, med
  samma filnamn men en annan adress.
* Före 2018 är ett års protokoll samlade i ett "möte" daterat 1 januari,
  med sammanträdets datum i filnamnet: `Protokoll 2014-04-16.pdf`,
  `Protokoll RS 161109.pdf`, `2013-02-06.pdf`.
* Plattformen har ett JSON-svar med organen
  (`/api/v2.0/committees`) men inget med mötena eller filerna.
* `robots.txt` stänger bara `/admin`.

## Decision Drivers

* **Adaptrar per plattform, aldrig per kommun.** Adresser, organ och
  samlingsmöten står i kommunfilen.
* **Korrekthet före fart.** Ett datum gissas inte, och samma bilaga
  sparas inte två gånger.
* **Tomt är inte noll.** En fil som inte blir kandidat nämns i
  sammanfattningen.
* **Det nya först.** Med tre gånger Kungsbackas volym tar den första
  hämtningen flera nätter.

## Considered Options

Läsningen:

* A – Organets sida och sedan varje mötes sida, en kandidat per PDF
* B – Zip-paketet per möte
* C – Plattformens JSON-svar

Ordningen:

* D – Det nyaste mötet först över alla organ, som arkivet
* E – Organ för organ, äldst först, som de levande källorna (ADR-0010)

## Decision Outcome

Valt: A och D. Projektägaren bekräftade rekommendationen i fas 0, också
att alla 17 organ och bilagorna tas med från början.

* **Typen** är avsnittets: kallelsen och protokollet ligger under
  mötessidans egen adress, bilagorna under en annan. Bilagan får sitt namn
  ur filnamnet, som i dag (K30).
* **Protokollets bilagor** tas bara med när filnamnet inte står bland
  kallelsens bilagor. Annars hade varje bilaga på de äldre sidorna sparats
  två gånger.
* **Två kallelser** för samma möte, som när en rättad kallelse lagts upp
  bredvid den första, blir två dokument. Vilken som gäller går inte att
  avgöra ur sidan, och ingen gissas fram.
* **Samlingsmötena** står som adresser i kommunfilen, och mönstren läser
  typ och datum ur filnamnet där. Ett möte daterat 1 januari är inte
  samlingsmöte av sig självt: listan gör det synligt vilka sidor som
  tolkas annorlunda. En fil i ett samlingsmöte utan datum i filnamnet, som
  plattformens manual eller revisionsrapporterna 2022, blir ingen kandidat.
* **Källnyckeln** är filens sökväg. Den är stabil, unik per fil och utan
  frågesträng.
* **Ordningen** D: plattformens hela historik är levande, så som i arkivet
  ([ADR-0018](0018-wayback-sist-nyast-forst-och-bara-luckor.md)) kommer det
  senaste först och de äldsta åren sist. Kandidaterna står efter övriga
  levande källors, så en kommun med båda får sina vanliga mötessidor
  först.
* **Upptäckten** väljer adapter efter `adapter` i kommunfilen; källorna
  på Meetings Plus läses i en egen lista bredvid Sitevisions.

### Consequences

* Bra, eftersom varje bilaga blir ett eget dokument med eget namn, som
  går att länka och söka på.
* Bra, eftersom ingenting regionspecifikt finns i koden.
* Dåligt, eftersom upptäckten hämtar varje mötessida varje natt: omkring
  1 100 sidor, en halvtimme med två sekunder mellan anropen. En upptäckt
  som bara läser nya möten kräver att den läser poolen, och väntar tills
  tiden blir ett problem.
* Dåligt, eftersom ett samlingsmöte som saknas i kommunfilen gör dess
  filer till bilagor med mötets datum, och dokumentets plats följer sedan
  källnyckeln. Läggs mötet till i efterhand måste dokumenten tas bort ur
  poolen för hand, så att nästa körning hämtar dem på rätt plats. Därför
  gicks alla regionens möten daterade 1 januari igenom innan den första
  körningen, och alla står i kommunfilen.
* Dåligt, eftersom en mötessida som inte går att hämta ger en lucka till
  nästa körning. Den nämns i sammanfattningen, och organets alla
  kandidater den dagen väntar också, så att ett annat möte samma dag inte
  tar det missade mötets plats i poolen. En organsida som inte går att
  hämta stoppar upptäckten som förut, eftersom den listar alla mötena.

### Confirmation

`tests/test_meetingsplus.py` läser sparade sidor ur
`tests/fixtures/meetingsplus/`: en organsida, ett vanligt möte, ett med
protokollets bilagor och ett samlingsmöte. `tests/test_upptack.py` prövar
ordningen. Hela upptäckten kördes mot regionen 2026-11-15, och
sammanfattningens filer utan kandidat gicks igenom för hand.

## Pros and Cons of the Options

### A – Organets sida och varje mötes sida

* Bra, eftersom sidan visar avsnittet, filnamnet och adressen för varje
  fil.
* Dåligt, eftersom varje möte är ett anrop till.

### B – Zip-paketet per möte

* Bra, eftersom ett anrop ger alla filer.
* Dåligt, eftersom poolen bara lagrar text och en zip måste packas upp i
  koden, och en enskild fils version inte går att känna igen.

### C – Plattformens JSON-svar

* Dåligt, eftersom det bara listar organen.

### D – Nyast först över alla organ

* Bra, eftersom det som är aktuellt i dag finns efter första natten.

### E – Organ för organ, äldst först

* Dåligt, eftersom de första nätterna bara hade gett 2013–2017 för de
  första organen.

## More Information

Utredningen före beslutet jämförde regionen med Kungsbacka: omkring 1 100
möten och uppskattat 15 000 dokument, tre gånger Kungsbackas. Därför ett
eget datarepo, `moggleif/regionhalland`, med kommunfil, data och
nattkörning, som installerar den här koden i en fast version.
Webbplatsen för regionen är ett senare steg.

**Tillägg 2026-11-16.** Först stoppade en mötessida som inte gick att
hämta hela upptäckten, som en Sitevision-sida. Den första körningen för
regionen stannade efter 37 minuter på ett anslutningsfel på en av
omkring 1 100 mötessidor, och ingenting hämtades. Med så många sidor
blir det för ofta, så en mötessida som inte går att hämta stoppar nu
bara sitt organs dag (K57).

**Tillägg 2026-11-16, webbplatsen.** Regionens webbplats byggs i
datarepot med samma kod och samma sidor, och publiceras på dess GitHub
Pages. Sidornas länkar till data, Markdown-filer och issues går till
datarepot, som skickas till bygget, men länkarna till arkitekturen,
ADR:erna och Bidra går till kommunhandlingar (`KALLKOD` i
`webbplats/mall.py`), eftersom dokumentationen bara finns här. En
konstant räcker: koden har ett hem, och ett andra argument eller ett fält
i kommunfilen hade bara kunnat ha det värdet (K14). Länkarna går till
`main` och kan beskriva en nyare version än den regionen kör.

GitHub Pages tar högst 1 GB. Kungsbackas sida är omkring 766 MB för
5 210 dokument, och nästan allt är dokumentens text. Regionen väntas få
tre till fyra gånger så mycket. Därför säger kommunfilen vilka typer som
visar texten på sin sida (`sidor_med_text`, K18): för regionen kallelser
och protokoll, 1 546 av 20 632 filer. Bilagornas sidor visar härkomsten
och länkar till Markdown-filen i repot, som GitHub visar med front matter
som tabell. Varje dokument har kvar sin sida, så alla länkar på
webbplatsen, i kalendern, målen och spåren fungerar som förut, och
indexet är oförändrat. En egen server (#18) hade gett all text på sidan
men står sist i planen. Utan fältet visar alla dokument sin text, som i
Kungsbacka.

Uppskattad storlek för regionen när poolen är ikapp: sidorna utan text
omkring 10 kB styck, för 19 086 bilagor ungefär 185 MB; kallelserna och
protokollen med text ungefär 150 MB; tabellerna, som kopieras för alla
dokument så att indexet stämmer, ungefär 200 MB. Det ger omkring 550 MB,
under gränsen. Priset är att en länk med `#sida-N` till en bilaga,
från målen, spåren eller punktkorten, landar högst upp på sidan utan
text, och att Markdown-filen saknar sidankare.
