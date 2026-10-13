---
status: proposed
date: 2026-10-13
decision-makers: projektägaren
consulted: AI-agenten
---

# Varje avvikelse i källan blir ett eget issue efter en mall

## Context and Problem Statement

Under [#49](https://github.com/moggleif/kommunhandlingar/issues/49)
hittades ett protokoll vars filnamn säger arbetsutskottet medan första
sidan säger nämnden
([#59](https://github.com/moggleif/kommunhandlingar/issues/59)).
Avvikelser som hittas ska samlas, så att de undersöks och, när de är fel
hos kommunen, kan mejlas till kommunen
([#58](https://github.com/moggleif/kommunhandlingar/issues/58)).
Projektägaren har redan bestämt fyra saker:

* varje avvikelse blir ett eget issue;
* `avvikelse` är den enda etiketten för dem;
* statusen står som en rad i issuets text;
* en människa skickar e-posten.

Kvar att avgöra är hur ett issue ser ut och vem som skapar det.

## Decision Drivers

* Varje avvikelse ska bära det som behövs för e-posten till kommunen.
* Inget ska rättas tyst: poolen återger källan.
* Inga fler etiketter, verktyg eller automatik än det finns ett verkligt
  behov av.
* Inga personnamn och inga personuppgifter i ett issue (AGENTS.md och
  [ADR-0022](0022-personuppgifter-maskas-vid-konverteringen.md)).

## Considered Options

* A – En mall, och den som hittar avvikelsen skapar issuet
* B – Körningen hittar avvikelser och skapar issuen själv
* C – Körningen skriver en lista över misstänkta avvikelser, som en
  människa läser och gör issues av

## Decision Outcome

Valt: A, eftersom det räcker för de avvikelser som hittas i dag och inte
kräver någon ny kod. Den som hittar avvikelsen, en människa eller
AI-agenten, skapar issuet med mallen `.github/ISSUE_TEMPLATE/avvikelse.md`.
Mallen sätter etiketten och har fälten för kommun, möte, status,
avvikelsen, belägg och vad som är kvar att undersöka. Statusen och hur
den ändras står i `docs/01-BIDRA.md`. Varje nytt steg läggs till på
statusraden med datum, så att e-postens datum står kvar. Ett issue
stängs när avvikelsen inte är något fel, när den är rättad i källan,
eller när den inte kommer att rättas.

Dokumentet i poolen står som källan publicerat det. Kommunfilens
rättelser, som avgör under vilket organ och datum ett dokument hamnar
([ADR-0011](0011-sitevision-organ-fran-sidan-datum-och-rattelser.md)),
gäller som förut.

### Consequences

* Bra, eftersom varje avvikelse ser likadan ut och bär sitt belägg, och
  statusen syns direkt i issuet.
* Bra, eftersom ingen kod tillkommer.
* Dåligt, eftersom avvikelser bara hittas när någon letar. De kontroller
  som #58 föreslog görs inte av sig själva: organ eller datum i
  filnamnet mot mötessidan, och två dokument av samma typ till ett möte.
  Luckorna (K7) syns redan på webbplatsen.
* Dåligt, eftersom statusen bara går att söka fram som text, till
  exempel `label:avvikelse "fel hos kommunen"`.
* Dåligt, eftersom de fel som redan står i `docs/kallor/kungsbacka.md`
  saknar issues tills någon skapar dem.

### Confirmation

Mallen sätter etiketten. Att ett issue följer mallen och saknar
personnamn är upp till den som skapar det; inget kontrollerar det
automatiskt.

## Pros and Cons of the Options

### A – En mall, och den som hittar avvikelsen skapar issuet

* Bra, eftersom den som skapar issuet har sett avvikelsen och kan skriva
  vad som skiljer sig.
* Dåligt, eftersom ingen letar efter avvikelser av sig själv.

### B – Körningen skapar issuen

* Bra, eftersom inget missas.
* Dåligt, eftersom körningen behöver rätt att skapa issues, och varje
  falsk träff blir ett issue som måste stängas. Den kan inte heller
  avgöra om ett belägg innehåller personnamn eller personuppgifter som
  inte får hamna i ett issue.

### C – En lista som en människa läser

* Bra, eftersom avvikelserna hittas av sig själva men en människa avgör.
* Dåligt, eftersom det kräver nya kontroller och en ny fil eller sida,
  för ett fåtal kända avvikelser.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet** kom ur #49. Projektägaren bestämde att varje avvikelse blir
   ett eget issue, att listan används i två steg (först undersöks den,
   sedan kontaktas kommunen), att `avvikelse` är den enda etiketten och
   att statusen står som en rad i texten.
2. **Projektägaren** bad AI-agenten ta det som återstod utan
   avstämningar och välja det rekommenderade alternativet vid varje
   vägval.
3. **AI-agenten** rekommenderade A. B och C kräver kontroller som ingen
   har behövt än. En lista eller automatik bör vänta tills avvikelserna
   blir för många för att hittas för hand.
4. **Granskningen** fann att ett första utkast skrev statusen och fälten
   på tre ställen och lade arbetssättet som ett krav i 02-KRAV, fast
   kraven beskriver systemet. Nu äger mallen fälten och 01-BIDRA
   statusen. Granskningen fann också att statusen saknade ett slut för
   en avvikelse som inte rättas, att e-postens datum skrevs över, och
   att mallen bad om belägg ur första sidan, där namn står. Statusen
   fick `rättas inte`, stegen läggs till med datum, och belägg anges med
   sökväg och sidnummer.

Ompröva beslutet om avvikelserna blir många, eller om samma slags
avvikelse kommer tillbaka; då är en kontroll enligt C nästa steg.
