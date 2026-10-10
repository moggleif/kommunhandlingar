---
status: proposed
date: 2026-10-10
decision-makers: projektägaren
consulted: AI-agenten
---

# Personnummer, mobilnummer, e-post och gatuadresser maskas vid konverteringen; namn står kvar

## Context and Problem Statement

Handlingarna innehåller personuppgifter som kommunen har publicerat. En
sökning i poolen 2026-10-10 hittade ett fyrtiotal fullständiga
personnummer i fjorton ärenden: stipendiater, fastighetsägare,
anställda i ett delegationsbeslut, firmatecknare och styrelser i
registreringsbevis. Dessutom fanns ett par hundra mobilnummer, ett
par tusen e-postadresser och adresser till privatpersoner. Poolen är
publik, och den ska paketeras för AI
([#56](https://github.com/moggleif/kommunhandlingar/issues/56)), där
uppgifterna blir lättare att söka fram och sammanställa
([#63](https://github.com/moggleif/kommunhandlingar/issues/63)).

Poolens syfte är besluten och handlingarna, inte personerna. Vilka
uppgifter ska bort, var tas de bort, och vad händer med det som redan
finns i poolen och i historiken?

## Decision Drivers

* **Syftet behöver inga identifierare.** Ett personnummer eller ett
  mobilnummer tillför ingenting till ett beslut.
* **Det politiska innehållet står kvar.** Vem som yrkade, röstade eller
  handlade ett ärende står i protokollen med namn.
* **Tal är data** och ska vara rätt eller märkta. Maskningen får inte ändra
  ett belopp eller ett diarienummer.
* **Enkelhet.** Mönster som går att pröva, ingen modell och inget nytt
  beroende.
* **Historiken skrivs inte om** ([ADR-0007](0007-poolen-ar-en-ogonblicksbild.md)),
  och det var kommunen som publicerade uppgifterna.

## Considered Options

* A – Konverteringen maskar identifierare med mönster: personnummer,
  mobilnummer, e-post och gatuadresser
* B – Som A, och dessutom enskildas namn
* C – Ingenting maskas i poolen; bara det som byggs ovanpå (webbplatsen,
  paketet) rensas
* D – Ingenting maskas

## Decision Outcome

Valt alternativ: "A – Identifierare maskas med mönster", eftersom det tar
bort de uppgifter som inte behövs utan att röra namnen, och mönstren går
att pröva mot hela poolen. Reglerna står i
[ARKITEKTUR](../03-ARKITEKTUR.md#personuppgifter).

* **Var:** i konverteringen, på sidans text och varje tabellcell, innan
  något skrivs. Omaskad text checkas aldrig in, och ingen egen action
  behövs.
* **Vad:** personnummer, mobilnummer, alla e-postadresser och gatuadresser
  som följs av postnummer. Markören säger vad som stod där, till exempel
  `(personnummer borttaget)`, eftersom tomt inte är noll.
* **Vad inte:** namn, fasta telefonnummer, postnummer och ort,
  organisationsnummer och fastighetsbeteckningar.
* **Poolen** maskas en gång med samma regel utan att PDF:erna hämtas
  (`python -m kommunhandlingar.maska_poolen data`). `pipeline` rörs inte, så
  omkonverteringen ([ADR-0019](0019-omkonvertering-efter-poolens-version.md))
  ser fortfarande vilka dokument som lästs av en äldre version.
  Maskningen tål att köras flera gånger, så samma kommando används för en
  nattgren som en äldre version skrivit.
* **Datakontrollen** faller på en fil där maskningen skulle ändra något,
  så att inget omaskat når `main` (K11).
* **Versionen** höjs till 0.5.0.
* **Historiken** lämnas som den är.
* **Felen i källan** blir ett `avvikelse`-issue per ärende, #68–#81, utan
  uppgifterna själva. En människa mejlar kommunen.

### Consequences

* Bra, eftersom de uppgifter som pekar ut en person tas bort ur allt som
  skrivs från och med nu, också i paketet för AI.
* Bra, eftersom samma regel används i konverteringen, i engångskörningen
  och i datakontrollen.
* Dåligt, eftersom mönster inte hittar allt: ett personnummer utan
  bindestreck med tio siffror, ett nummer som OCR läst fel eller som
  brutits av en rad, och en adress utan postnummer står kvar.
* Dåligt, eftersom också organisationers e-post och adresser maskas, till
  exempel kommunens egen adress och adresser till verksamheter i en
  tabell. Mönstret kan inte skilja dem från en privatpersons.
* Dåligt, eftersom uppgifterna finns kvar i git-historiken och i kloner.
* Neutralt, eftersom enskildas namn står kvar.

### Confirmation

* `tests/test_maskning.py` prövar varje mönster med påhittade exempel där
  facit går att räkna för hand: giltiga och ogiltiga personnummer, belopp,
  diarienummer, datumintervall och organisationsnummer som ska stå kvar,
  mobilnummer mitt i en talrad, escapad e-post och adresser i en
  tabellcell. En andra maskning ändrar ingenting.
* `tests/test_datakontroll.py` prövar att datakontrollen faller på en fil
  med ett personnummer.
* Engångskörningen på poolen granskas för hand: antalet träffar per slag,
  och ett urval av de maskade raderna, så att inga tal i tabeller rörts.

## Pros and Cons of the Options

### A – Identifierare maskas med mönster

* Bra, eftersom mönstren är små och går att pröva.
* Bra, eftersom namnen och därmed det politiska innehållet står kvar.
* Dåligt, eftersom mönster missar och ibland tar för mycket.

### B – Som A, och enskildas namn

* Bra, eftersom också namnet på en sökande eller en fastighetsägare
  försvinner.
* Dåligt, eftersom ett namn inte går att hitta med mönster. Det kräver en
  språkmodell och en lista över förtroendevalda och tjänstepersoner som
  ska stå kvar, och blir aldrig felfritt.

### C – Bara det som byggs ovanpå rensas

* Bra, eftersom poolen förblir en exakt avskrift.
* Dåligt, eftersom poolen själv är publik, och varje produkt måste rensa
  på nytt.

### D – Ingenting maskas

* Bra, eftersom ingen kod behövs.
* Dåligt, eftersom poolen sprider personnummer vidare.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Uppdraget (projektägaren).** Personuppgifter borde kommunen redan ha
   rensat, men syftet behöver dem inte, så de kan tas bort. Visa exempel
   och peka ut det som bör rapporteras till kommunen.
2. **Kartläggningen (agenten).** Ett fyrtiotal personnummer i fjorton
   ärenden, räknade med giltigt datum och kontrollsiffra, flera hundra
   mobilnummer och tusentals e-postadresser. Inga personnummer i
   tabellerna.
3. **Namn (projektägaren).** Frågade om enskildas namn också kunde
   maskas. Agenten svarade att det bara går delvis med regler, till
   exempel namnet bredvid ett maskat personnummer, och fullt ut först med
   ett språkverktyg. Projektägaren valde att inte maska några namn.
4. **Historiken (projektägaren).** Att skriva om historiken skulle kräva
   ett undantag från regeln på `main`, nya commit-id för alla grenar och
   GitHubs hjälp med de stängda pull requesterna, och kloner behåller
   ändå allt. Beslut: historiken lämnas, eftersom det är kommunen som
   eventuellt felat.
5. **Nattkörningen (projektägaren).** Frågade om nattkörningen tar bort
   uppgifterna direkt, och om det behövs en egen action. Agenten: nej,
   maskningen ligger i konverteringen. En egen action skulle checka in
   uppgifterna först och ta bort dem sedan, och då hamnar de i historiken.
   Datakontrollen stoppar det som ändå slinker igenom.
6. **Mönstren (agenten).** Prövades mot hela poolen innan reglerna
   skrevs. Tio siffror utan bindestreck gav falska personnummer bland
   beloppen och togs bort. Mobilnummer med fritt placerade mellanslag
   matchade talgrupper i en balansräkning, och grupperingen stramades åt.
   Fasta telefonnummer var till största delen växlar, stödlinjer och
   företag, så de maskas inte. Gatuadresser med postnummer var mest
   verksamheter, men maskas ändå, eftersom privatpersonernas adresser
   står i samma form. Alla e-postadresser maskas, eftersom en lista över
   privata e-posttjänster vore en gissning; de flesta i poolen är
   anställdas `förnamn.efternamn@`.
7. **Omprövas** när poolen paketeras för AI (#56), om namn eller fler
   slags uppgifter behöver bort.
