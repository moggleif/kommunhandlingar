---
status: proposed
date: 2026-10-08
decision-makers: projektägaren
consulted: AI-agenten
---

# Wayback hämtas sist i nattkörningen, nyast först, och fyller bara luckor

## Context and Problem Statement

Kungsbackas mötessidor visar bara tre år. Det som publicerades före 2024
finns kvar i Internet Archive (Wayback), i tre generationer av webbplatsen
([källorna](../kallor/kungsbacka.md#2-internet-archive-wayback),
[#24](https://github.com/moggleif/kommunhandlingar/issues/24)). Den här
ADR:en gäller hur Wayback tas in i nattkörningen
([#51](https://github.com/moggleif/kommunhandlingar/issues/51)), med
Sitevisions år 2021–2023 som första källa. Episervers två generationer
(2013–2022) tas i ett eget issue.

[ADR-0010](0010-ordningen-organ-for-organ.md) lät ny historik för ett
tidigt organ gå före nya dokument för ett senare. Ägarens krav är det
motsatta: Wayback körs först när allt från de levande källorna är hämtat.
Det väcker fem frågor som ADR-0003, ADR-0004 och ADR-0010 lämnade till
"när adaptern skrivs":

1. I vilken ordning tas Wayback, och vad betyder "allt är hämtat"?
2. Vad händer när Wayback inte svarar?
3. Får en kopia i arkivet ändra ett dokument som redan finns?
4. Vilken kopia väljs när samma fil sparats flera gånger?
5. Hur känns en kapad kopia igen?

## Decision Drivers

* **De levande källorna först** (ägarens krav). Wayback har lägst
  prioritet och fyller det som saknas.
* **Trenddata från i dag och bakåt** (ägarens krav). Det som hämtas ur
  arkivet ska ge sammanhängande år, med de nyaste först.
* **En nyare version ersätts aldrig av en äldre**
  ([ADR-0003](0003-dokumentets-identitet-och-datamodell.md)).
* **Samma val varje natt** ([ADR-0004](0004-inkrementell-korning-poolen-ar-tillstandet.md)):
  en ny ögonblicksbild av oförändrat innehåll ger ingen ny kandidat.
* **Ett avbrott i arkivet får inte kosta det som redan hämtats.**
  `web.archive.org` bryter ibland anslutningen, också från Actions.
* **Ingen kod "för säkerhets skull"** och inget hårdkodat om en kommun
  (AGENTS.md).

## Considered Options

* A – En egen kandidatlista för arkivet, som tas efter de levande
  källorna, nyast först, och bara fyller luckor
* B – Arkivets kandidater i samma lista som de levande, i K13:s ordning
  (ADR-0010 som den står)
* C – Arkivets kandidater i samma lista, men sist i sorteringen
* D – Arkivet i ett eget jobb i Actions, med egen tidsbudget

## Decision Outcome

Valt alternativ: "A – En egen kandidatlista för arkivet", eftersom den
uppfyller ägarens krav utan ny kod för att avgöra när de levande källorna
är klara, och eftersom en egen lista gör det enkelt att ge arkivet egna
regler: nyast först, och bara luckor.

Det ersätter den del av ADR-0010 som gäller ny historik. Ordningen för de
levande källorna är oförändrad. Beteendet står i K3, K13 och K16, och hur
det är byggt i [03-ARKITEKTUR.md](../03-ARKITEKTUR.md).

* **Arkivet slås på per källa.** En Sitevision-källa med `wayback =
  true` läses också ur de arkiverade kopiorna av sina mötessidor.
  Inget annat i kommunfilen upprepas: organ, mönster, rubrik och rättelser
  är källans.
* **Ordningen.** Nattjobbet kör först upptäckt och steg 2 för de levande
  källorna i alla kommuner, och sedan för arkivet i alla kommuner. Arkivets
  lista tas **nyast först**: sammanträdets datum fallande, sedan organ och
  typ som i K13 och sist källnyckeln.
* **"Allt är hämtat"** betyder att steg 2 för de levande källorna har gått
  igenom hela sin lista: varje kandidat är försökt, vad det än blev. Ett
  `ej-hamtad`, till exempel `robots`, räknas som försökt och stoppar inte
  arkivet. Har den levande hämtningen tagit budgeten är den mjuka gränsen
  passerad; då frågas arkivet inte alls, och nästa natt försöker igen.
  Nås den hårda gränsen medan arkivet upptäcks avbryts upptäckten och
  arkivets lista blir tom, så att jobbet hinner checka in det levande
  före Actions gräns på sex timmar.
* **Ett avbrott i arkivet stoppar ingenting.** Arkivet frågas efter att
  det levande är hämtat. Svarar en fråga till arkivet inte, efter K10:s
  nya försök, hoppas den över och nämns i sammanfattningen, och det som
  hämtats checkas in som vanligt. Det är ett undantag från K2:s stopp, och
  bara för arkivet. En fil som inte går att hämta blir `ej-hamtad` (K6)
  och prövas igen nästa natt.
* **Arkivet fyller bara luckor.** En kandidat ur arkivet hämtas inte när
  dess källnyckel redan finns i poolen och inte är `ej-hamtad`, inte när
  dess plats har ett dokument från en levande källa, och inte när platsens
  dokument ur arkivet har en källnyckel som inte finns i arkivets lista.
  Ett dokument kommer ur arkivet när dess `kalla_url` är en kopia i
  arkivet. Två filer ur arkivet på samma plats, till exempel ett
  protokoll delat i två, blir två dokument som förut (ADR-0003). Ett
  `ej-hamtad` från den levande källan kan fyllas ur arkivet; går inte
  heller arkivets kopia att hämta står den levande källans försök kvar, så
  att de två inte skriver om filen varannan gång.
* **Valet av kopia.** Källnyckeln är originalets, `sitevision:<nod-id>`,
  som den levande. För varje nod-id tas den nyaste versionen, det vill
  säga den största tidsstämpeln i Sitevisions adress (K9). Bland
  arkivets kopior av den versionen tas den största och vid lika den
  äldsta. Storleken är CDX-fältet `length`, den komprimerade postens
  längd i arkivet, som följer filens storlek. En kapad kopia är mindre än
  en hel av samma fil, så den största är den som bäst kan vara hel, och
  valet beror bara på arkivets lista.
* **De arkiverade mötessidorna.** För varje mötessida läses den sista
  ögonblicksbilden från varje år. Sidan visar tre år, så den sista från
  ett år visar det året och de två före i sin slutliga form. Filerna läses
  med samma adapter som de levande sidorna (ADR-0011), och den nyaste
  ögonblicksbilden går först när samma fil står på flera. En mötessida
  som arkivet inte har någon kopia av nämns i sammanfattningen.
* **Kapad kopia.** En hämtad kopia som inte har `%%EOF` bland sina sista
  1 024 byte blir `ej-hamtad` med `fel: kapad`. En kopia som har `%%EOF`
  men inte går att öppna följer K6 som alla andra filer. Kontrollen görs
  bara för arkivet.
* **Härkomsten** är `kalla_url`, kopians adress
  `https://web.archive.org/web/<tidsstämpel>id_/<originalets adress>`, där
  tidsstämpeln är den då arkivet sparade filen (ADR-0003). Inget nytt
  fält.

### Consequences

* Bra, eftersom de levande källorna aldrig väntar på arkivet, och ett
  avbrott i arkivet inte kostar något som redan hämtats.
* Bra, eftersom poolen växer bakåt från i dag i hela år, för alla organ
  samtidigt, och trender går att följa så långt som hämtats.
* Bra, eftersom ett dokument i poolen aldrig skrivs över med en äldre
  kopia, och K8 och K9 gäller oförändrade för de levande källorna.
* Bra, eftersom den befintliga Sitevision-adaptern läser de arkiverade
  sidorna, med samma mönster och rättelser.
* Dåligt, eftersom en version som kommunen bytt ut inom samma år, och som
  bara fanns på en tidigare ögonblicksbild, inte hittas. Den sista
  ögonblicksbilden har den version som gällde.
* Dåligt, eftersom arkivets upptäckt tar tid varje natt arkivet frågas,
  med en fråga och omkring fem ögonblicksbilder per mötessida.
* Dåligt, eftersom en fil som bara finns kapad i arkivet förblir
  `ej-hamtad` med `fel: kapad`. Den syns, och kan begäras ut hos kommunen.
  Det gäller också när bara den nyaste versionen är kapad och en äldre
  finns hel: den äldre är ersatt och tas inte i stället.
* Dåligt, eftersom en fil som kommunen ersatt med ett nytt nod-id mellan
  två ögonblicksbilder blir två dokument på samma plats, där det senare
  får ett namn, när ingen av dem finns på den levande sidan. Arkivets lista kan inte skilja ett utbyte från ett
  protokoll som delats i två filer. Båda är filer som kommunen
  publicerat, och inget skrivs över.
* Dåligt, eftersom ett protokoll som delats i två filer, där den levande
  sidan bara har den ena, inte får den andra ur arkivet: platsen har ett
  levande dokument.
* Dåligt, eftersom en fil vars levande försök är `ej-hamtad` och vars
  kopia är kapad laddas ned på nytt varje natt, utan att något skrivs.
* Neutralt, eftersom den största kopian kan vara en annan version än en
  mindre, om arkivet sparat två olika filer under samma adress. Sitevision
  ger en ny tidsstämpel för en ny version, så det bör inte hända där.

### Confirmation

Testerna i `tests/` prövar, utan nät: att arkivets lista ordnas nyast
först; att en källnyckel i poolen och en upptagen plats inte hämtas ur
arkivet; att den nyaste versionen och den största kopian väljs, vid lika
den äldsta; att den sista ögonblicksbilden per år läses; att en kopia utan
`%%EOF` blir `kapad` och en med `%%EOF` följt av några byte inte blir det;
att en fråga som inte besvaras, ett svar som inte är JSON och en mötessida
utan kopior nämns och inte stoppar upptäckten; att den levande källans
försök inte skrivs om av ett misslyckat försök ur arkivet; att arkivet inte
frågas efter den mjuka gränsen; och att den hårda gränsen ger en tom
lista. Att `web.archive.org` svarar
och släpper in oss prövas i Actions innan PR:en mergas.

## Pros and Cons of the Options

### A – En egen kandidatlista för arkivet

* Bra, eftersom "efter de levande" följer av körningens ordning, utan kod
  som räknar ut när de levande är klara.
* Bra, eftersom arkivet kan ha egen ordning (nyast först) och egen regel
  (bara luckor) utan att K13 och K8 ändras för de levande.
* Dåligt, eftersom upptäckten och steg 2 behöver ett läge till, och
  nattjobbet ett steg till.

### B – Samma lista, i K13:s ordning

* Bra, eftersom det inte kräver något nytt.
* Dåligt, eftersom det bryter mot ägarens krav: arkivet för ett tidigt
  organ tas före nya dokument för ett senare, och ett nytt protokoll från
  fullmäktige kan vänta flera nätter.
* Dåligt, eftersom en fråga till arkivet som inte svarar stoppar hela
  upptäckten enligt K2, också för de levande källorna.

### C – Samma lista, sist i sorteringen

* Bra, eftersom de levande tas först med en enda sorteringsnyckel till.
* Dåligt, eftersom arkivet ändå frågas före den levande hämtningen, i
  upptäckten, och ett avbrott där stoppar allt.
* Dåligt, eftersom regeln om bara luckor och kontrollen av kapade kopior
  måste skilja arkivets kandidater från de levande i samma lista.

### D – Ett eget jobb i Actions

* Bra, eftersom arkivet får en egen tidsbudget och inte tränger undan
  något.
* Dåligt, eftersom två jobb kan skriva samma dokument, och ADR-0015:s
  gren och PR blir två per natt, eller kräver samordning.
* Dåligt, eftersom "efter de levande" då måste samordnas mellan jobb.

## More Information

### Diskussionen

1. **Ägarens krav kom med #24:** Wayback körs i nattjobbet och först när
   allt från de vanliga källorna är hämtat, med lägst prioritet. Det går
   emot ADR-0010:s konsekvens om ny historik, och därför den här ADR:en.
2. **Agenten föreslog alternativ A i fas 0**, med att arkivet bara fyller
   luckor och att den största kopian väljs. Ägaren sade ja till båda.
3. **Ägaren lade till ordningen:** arkivet tas från det nyaste mot det
   äldsta, så att trenddata går att få från i dag och bakåt. Agentens
   tolkning är att det gäller hela listan, inte organ för organ: poolen
   fylls år för år för alla organ samtidigt. Inom ett datum gäller K13:s
   organ och typ. Ordningen för de levande källorna ändras inte; de tar
   ungefär en natt.
4. **Ägaren begränsade arkivet till Kungsbacka.** Det står som `wayback =
   true` i Kungsbackas kommunfil, inte i koden. Nattjobbet kör ändå
   arkivet efter de levande källorna för alla kommuner, eftersom det inte
   kostar något extra och följer kravet som det står.
5. **Bara luckor (ägarens ja).** Agentens argument: arkivet är äldre än
   den levande sidan, så det har inget att tillföra ett dokument som redan
   finns, och ADR-0003 säger redan att en äldre ögonblicksbild aldrig
   ersätter en nyare version. Regeln om upptagen plats behövs för att
   ADR-0003 annars skulle göra en ersatt, äldre fil ur arkivet till en ny
   version av det levande dokumentet på samma plats. Det andra
   granskningsvarvet visade att regeln måste gälla varje plats med ett
   levande dokument, eftersom arkivets lista också har de levande filernas
   nod-id:n från ögonblicksbilderna 2024–2026. Inom arkivets egna dokument
   blir två nod-id:n på samma plats två dokument (se Consequences).
6. **Den största kopian (ägarens ja).** Issuet krävde att valet inte låser
   fast en kapad kopia när en hel finns. Agentens argument: en kapning tar
   bort slutet av filen, så den hela kopian är alltid den största. Att
   välja den äldsta vid lika storlek gör valet stabilt när arkivet sparar
   samma fil igen. CDX-fältet `digest` behövs inte för valet.
7. **Den sista ögonblicksbilden per år** är agentens val, för att begränsa
   antalet sidor som läses varje natt till omkring fem per mötessida, mot
   69 kopior av sex sidor som #24 räknade.
8. **Granskningen (fas 6)** hittade att upptäckten i arkivet saknade en
   hård tidsgräns: ett segt arkiv strax före fem timmar hade kunnat ta
   jobbet förbi Actions gräns, och då hade inget checkats in. Därför den
   hårda gränsen också i arkivets upptäckt. Den föreslog också `wayback =
   true` i stället för en sträng med ett enda tillåtet värde, och att en
   mötessida utan kopior ska nämnas. Vid provet 2026-10-08 svarade
   arkivet ibland med en HTML-sida, "Temporarily Offline", i stället för
   CDX-listan; den räknas som en fråga som inte besvaras.
9. **`%%EOF` bara för arkivet.** Kapningen har bara setts i arkivet; för
   de levande källorna fångar HTTP-klienten ett avbrutet svar. Kontrollen
   tillåter några byte efter `%%EOF`, som filer ofta har.

### När beslutet bör omprövas

* När Episervers generationer läggs till, eftersom deras källnycklar är
  andra än Sitevisions och samma möte kan finnas på två plattformar.
* När en andra kommun läggs till och arkivet för den första tränger undan
  den andras levande källor i budgeten.
* När en fil visar sig finnas hel bara i en mindre kopia.
