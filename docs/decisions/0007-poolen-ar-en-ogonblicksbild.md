---
status: accepted
date: 2026-10-07
decision-makers: projektägaren
consulted: AI-agenten
---

# Poolen är en ögonblicksbild: det som en gång checkats in tas inte bort, och historiken skrivs inte om

## Context and Problem Statement

Repot är publikt, och git-historiken behåller allt som en gång checkats in.
Ett dokument som kommunen publicerat av misstag, till exempel med
personuppgifter eller sekretessbelagda uppgifter, ligger då kvar i poolen
även om kommunen drar tillbaka det eller byter ut det mot en maskad
version ([#7](https://github.com/moggleif/kommunhandlingar/issues/7)).
ADR-0001 sade att det räcker att kunna ta bort ett dokument som kommunen
drar tillbaka, men inte hur, och ADR-0006 lät data nå `main` varje natt.

Hur upptäcks ett tillbakadraget dokument, vad händer med det i poolen, och
får historiken skrivas om?

## Decision Drivers

* **Att försvinna ur källan är det normala.** Kungsbackas nämndsidor
  visar ungefär två år bakåt, och allt äldre finns i Internet Archive och
  diariet ([källorna](../kallor/kungsbacka.md)). Poolen finns för att behålla det
  som källan inte längre visar.
* **Handlingarna är offentliga.** Det poolen tar in har kommunen själv
  publicerat.
* **Enkelhet.** Ingen kod och ingen process för ett fall som inte har
  inträffat.
* **Det som en gång varit publikt går inte att dra tillbaka** ur forkar,
  kloner, arkiv och sökmotorer, vad poolen än gör.

## Considered Options

* A – Ögonblicksbild: det som checkats in står kvar, och historiken skrivs
  aldrig om
* B – Borttagning på begäran: texten ersätts av en gravsten, och
  historiken skrivs om i allvarliga fall efter beslut av projektägaren
* C – Som B, och dessutom en karenstid: en ny fil checkas in först när den
  legat publicerad en viss tid
* D – Ett dokument som försvinner ur källan tas bort ur poolen

## Decision Outcome

Valt alternativ: "A – Ögonblicksbild", eftersom det som en gång legat
publikt redan är spritt, poolen inte kan ändra på det, och varje annat
alternativ kräver kod och rutiner för ett fall som inte har inträffat.

* **Ett dokument som försvinner ur källan står kvar** i poolen, med text
  och tabeller (K12). Körningen letar inte efter det som försvunnit.
* **Ett utbytt dokument blir en ny version** enligt K9, också när
  kommunen strukit uppgifter i det. Den tidigare texten finns kvar i
  git-historiken.
* **Historiken på `main` skrivs inte om.**

### Consequences

* Bra, eftersom poolen behåller det som källorna slutar visa, vilket är
  det den finns till för.
* Bra, eftersom det inte behövs någon kod, något nytt kvalitetsvärde eller
  någon rutin för borttagning.
* Bra, eftersom ingen kloning av repot blir inaktuell av en force-push.
* Dåligt, eftersom en uppgift som kommunen publicerat av misstag ligger
  kvar i poolen och i historiken, också efter att kommunen rättat den.
  Byter kommunen ut filen under samma adress upptäcks utbytet inte alls
  (ADR-0004, #10), och den orättade texten står kvar som gällande
  version.

### Confirmation

K12 testas när pipelinen skrivs: ett dokument i poolen som ingen
kandidat har lämnas orört.

## Pros and Cons of the Options

### A – Ögonblicksbild

* Bra, eftersom det är enklast: ingenting att bygga.
* Bra, eftersom historiken förblir en pålitlig versionshistorik
  (ADR-0003).
* Dåligt, eftersom ett misstag från kommunen inte går att rätta i poolen.

### B – Borttagning på begäran, gravsten, omskrivning i allvarliga fall

Texten ersätts av en `.md` med kvalitet `borttagen`, källnyckel och orsak,
så att samma fil inte hämtas in igen. I allvarliga fall skrivs historiken
om med `git filter-repo` och force-push.

* Bra, eftersom ett allvarligt misstag kan tas bort ur repot.
* Dåligt, eftersom det kräver ett nytt kvalitetsvärde, en regel till i K8
  och en privat väg för begäran.
* Dåligt, eftersom en force-push gör alla kloner inaktuella, den nattliga
  körningen måste pausas, och forkar och arkiv ändå inte nås.

### C – Som B, med karenstid

* Bra, eftersom ett misstag som kommunen rättar inom karenstiden aldrig
  når historiken.
* Dåligt, eftersom poolen alltid släpar efter källan, och handlingar
  kommer in först efter mötet.
* Dåligt, eftersom karenstiden bygger på att tidsstämpeln i Sitevisions
  adress är uppladdningstiden, vilket inte är verifierat.

### D – Frånvaro ur källan tar bort

* Bra, eftersom det är automatiskt.
* Dåligt, eftersom nästan allt som försvinner gör det för att källan bara
  visar de senaste åren. Poolen skulle tömma sig själv.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Det viktigaste fyndet.** Agenten visade i fas 0 att frånvaro ur
   källan inte kan vara signalen för ett tillbakadraget dokument, eftersom
   källorna bara visar de senaste åren. D föll därför direkt. Det enda
   kommunen gör som körningen faktiskt ser är att byta ut en fil (K9), och
   då ligger den tidigare texten kvar i historiken.
2. **Agentens rekommendation** var B och C tillsammans: en karenstid på 14
   dagar räknad från uppladdningstiden i Sitevisions adress, en gravsten
   för det som ändå ska bort, omskrivning av historiken i allvarliga fall
   efter beslut av projektägaren, och en privat väg för begäran om
   borttagning.
3. **Ägarens beslut** 2026-10-07: det som legat publikt en gång är redan
   spritt, och det får vara så. Poolen tar en ögonblicksbild, och det ska
   inte göras mer än så. Därför valdes A.
4. **ADR-0001.** Där konstaterades att namn räknas som personuppgifter och
   att det räcker att kunna ta bort ett dokument som kommunen drar
   tillbaka. Det här beslutet ersätter den bedömningen: poolen tar inte
   bort dokument som kommunen drar tillbaka.

### Granskningen

Den oberoende granskningen (fas 6) fann att ADR-0001 fortfarande lovade
borttagning utan att hänvisa hit; punkten fick en anteckning. Kravets
rubrik undviker ordet ögonblicksbild, som i K8 betyder en kopia i
Internet Archive, och kravet säger att det gäller dokument som ingen
kandidat har, så att det inte läses som att det krockar med K9. En
utlovad kontroll i granskningen ströks, eftersom granskaren aldrig ser de
nattliga körningarna, och ett scenario som upprepade K9 ströks.

### När beslutet bör omprövas

Om en myndighet eller domstol kräver att något tas bort, eller om ett
misstag från en kommun visar sig vara vanligt och allvarligt. B och C står
ovan som utgångspunkt.
