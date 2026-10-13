---
status: proposed
date: 2026-10-13
decision-makers: projektägaren
consulted: AI-agenten
---

# Avvikelser i källan blir ett issue per fel, skrivet av en människa efter en mall

## Context and Problem Statement

Handlingarna namnges och publiceras för hand, och fel görs lätt. Under
[#49](https://github.com/moggleif/kommunhandlingar/issues/49) hittades
ett protokoll med arbetsutskottets namn som gällde nämndens möte
([#59](https://github.com/moggleif/kommunhandlingar/issues/59)). Poolen
ska samla sådana avvikelser, så att de undersöks och, när de är
kommunens fel, rapporteras till kommunen med e-post
([#58](https://github.com/moggleif/kommunhandlingar/issues/58)).
Projektägaren har redan bestämt fyra saker:

* varje avvikelse blir ett eget issue;
* `avvikelse` är den enda etiketten;
* statusen står som en rad i issuets text;
* en människa skickar e-posten.

Kvar att avgöra är hur ett issue ser ut, vem som skapar det, och vad som
gäller för dokumentet i poolen.

## Decision Drivers

* Varje avvikelse ska bära det som behövs för e-posten till kommunen.
* Inget ska rättas tyst: poolen återger källan.
* Inga fler etiketter, verktyg eller automatik än det finns ett verkligt
  behov av.
* Personuppgifter får aldrig hamna i ett issue
  ([ADR-0022](0022-personuppgifter-maskas-vid-konverteringen.md)).

## Considered Options

* A – En mall för issuet, och en människa eller AI-agenten skapar issuet
  när avvikelsen hittas
* B – Körningen hittar avvikelser och skapar issuen själv
* C – Körningen skriver en lista över misstänkta avvikelser, som en
  människa läser och gör issues av

## Decision Outcome

Valt: A, eftersom det räcker för de avvikelser som hittas i dag och inte
kräver någon ny kod. Mallen `.github/ISSUE_TEMPLATE/avvikelse.md` sätter
etiketten `avvikelse` och har fälten:

* kommun;
* organ och möte;
* status;
* vad som skiljer sig, med länkar;
* belägg, med sökvägen i poolen;
* vad som är kvar att undersöka.

Statusen ändras i ordningen:

1. `att undersöka`;
2. antingen `undersökt – inget fel`, och issuet stängs, eller
   `undersökt – fel hos kommunen`;
3. `e-post skickad` med datumet;
4. `rättat i källan`, och issuet stängs.

Dokumentet i poolen står som källan publicerat det, och avvikelsen
rättas inte tyst. Kommunfilens rättelser, som avgör under vilket organ
och datum ett dokument hamnar
([ADR-0011](0011-sitevision-organ-fran-sidan-datum-och-rattelser.md)),
gäller som förut.
Avsnittet "Kända fel i källan" i `docs/kallor/kungsbacka.md` länkar till
issuena. Arbetssättet står i `docs/01-BIDRA.md`, och kravet är K24.

### Consequences

* Bra, eftersom varje avvikelse ser likadan ut och bär sitt belägg, och
  statusen syns direkt i issuet.
* Bra, eftersom ingen kod tillkommer.
* Dåligt, eftersom avvikelser bara hittas när någon letar. De kontroller
  som issuet föreslog görs inte av sig själva: organ eller datum i
  filnamnet mot mötessidan, och två dokument av samma typ till ett möte.
  Luckorna (K7) syns redan på webbplatsen.
* Dåligt, eftersom statusen inte går att filtrera på; det kräver att
  issuet läses.

### Confirmation

Granskningen (fas 6) prövar att ett nytt avvikelse-issue följer mallen,
och att inga personuppgifter står i det.

## Pros and Cons of the Options

### A – Mall, och en människa skapar issuet

* Bra, eftersom den som skapar issuet har undersökt det första och kan
  skriva vad som skiljer sig.
* Dåligt, eftersom ingen letar efter avvikelser av sig själv.

### B – Körningen skapar issuen

* Bra, eftersom inget missas.
* Dåligt, eftersom körningen behöver rätt att skapa issues, och varje
  falsk träff blir ett issue som måste stängas. Den kan inte heller
  avgöra om en handling innehåller personuppgifter som inte får hamna i
  ett issue.

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

Ompröva beslutet om avvikelserna blir många, eller om samma slags
avvikelse kommer tillbaka; då är en kontroll enligt C nästa steg.
