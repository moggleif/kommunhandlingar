---
status: proposed
date: 2026-10-14
decision-makers: projektägaren
consulted: AI-agenten
---

# Tidigare sammanträden läses ur poolens mappar och skrivs i kalenderfilen, och listan döljer dem bakom en knapp

## Context and Problem Statement

Kalendern ([ADR-0032](0032-kalendern-las-ur-besluten-och-skrivs-for-hand.md))
har innevarande och kommande år. Besökare vill kunna se historiken bakåt
([#162](https://github.com/moggleif/kommunhandlingar/issues/162)). Var
kommer de tidigare datumen ifrån, hur långt bakåt går kalendern, och hur
visas de utan att ta över sidan?

Poolen har ett sammanträde per mapp, `<organ>/<år>/<datum>/`
([ADR-0003](0003-dokumentets-identitet-och-datamodell.md)). För 2026
stämmer mapparna före dagens datum exakt med kalenderns datum ur
mötessidorna, organ för organ, utom revisionen som kalendern inte tar
med. Alla organ finns i poolen från 2024; före det har poolen bara
Gymnasium & Arbetsmarknad, med hela år som saknas.

## Decision Drivers

* **Varje uppgift bär sin härkomst.** Ett tidigare sammanträde ska kunna
  öppnas i sitt dokument.
* **Tomt är inte noll.** En tom månad i kalendern ska betyda att inget
  sammanträde hölls, inte att poolen saknar året.
* **En modell för hela kalendern.** Samma fil och samma kontroller som
  för kommande sammanträden.
* **Listan är för det som kommer.** Det som varit ska finnas, men inte
  vara det första besökaren ser.

## Considered Options

* A – Raderna läses ur poolens mappar en gång och skrivs i kalenderfilen,
  från 2024, med protokollet som källa
* B – Bygget lägger till sammanträdena ur poolens mappar av sig självt
* C – Som A, men så långt bakåt som poolen räcker, för Gymnasium &
  Arbetsmarknad från 2013
* D – Som A, men listan visar också det som varit, utan knapp

## Decision Outcome

Valt: A, eftersom det ger varje tidigare sammanträde en källa med samma
fil och samma kontroller som resten av kalendern, och bara år där alla
organ finns.

* **Raderna** är ett sammanträde per mapp i poolen, 2024 och framåt till
  det år kalenderns rader ur mötessidorna börjar, för organen som
  kalendern redan visar. Revisionen tas inte med (ADR-0032).
* **Källan** är mötets protokoll, eller kallelsen när protokollet saknas.
  Utan protokoll märks sammanträdet osäkert, eftersom det inte är visat
  att mötet hölls. Tid och plats lämnas tomma.
* **Listan** börjar som förut på dagens datum. En knapp, "Visa tidigare
  sammanträden", visar och döljer det som varit. Utan skript visas allt,
  som förut.
* **Källtabellen** under Kvalitet räknar de sammanträden som har sitt
  eget dokument som källa, det vill säga ett dokument i sammanträdets
  mapp, och länkar antalet till organets sida. Annars blir cellen en lista
  med upp till trettio länkar. Övriga källor, mötessidorna och besluten om
  kommande år, länkas som förut.

### Consequences

* Good, eftersom varje tidigare sammanträde länkar till sitt protokoll.
* Good, eftersom ingen ny kod läser poolen och kontrollerna är desamma.
* Bad, eftersom ett sammanträde utan dokument i poolen inte står med.
* Bad, eftersom raderna inte följer med när poolen får fler sammanträden
  ur arkivet; de läggs till för hand.

### Confirmation

`tests/test_kalender.py` prövar knappen och källtabellens antal med en
påhittad kommun, och att Kungsbackas fil, med de tidigare raderna, går
igenom kontrollen mot poolen.

## Pros and Cons of the Options

### A – En gång i kalenderfilen, från 2024

* Good, eftersom en diff visar varje rad och dess källa.
* Good, eftersom alla organ är med alla år som visas.
* Bad, eftersom det är en läsning som görs om för hand.

### B – Bygget läser mapparna

* Good, eftersom nya sammanträden i poolen kommer med av sig själva.
* Bad, eftersom kalendern får två källor till samma sammanträde, och
  koden måste avgöra vilken som gäller och vilka organ som inte ska med,
  utan att något om kommunen står i koden.

### C – Så långt bakåt som poolen räcker

* Good, eftersom Gymnasium & Arbetsmarknad får hela sin historik.
* Bad, eftersom åren före 2024 bara har ett organ, och år som helt saknas
  i poolen ser ut som år utan sammanträden.

### D – Listan visar allt

* Good, eftersom ingen knapp behövs.
* Bad, eftersom listan börjar två år bakåt och det kommande hamnar långt
  ner.

## More Information

Agenten föreslog i fas 0 A eller C och rekommenderade C, med 2024 för
alla organ och Gymnasium & Arbetsmarknad från 2013. Projektägaren valde
2024 för alla, och att raderna skrivs i kalenderfilen, inte läses av
bygget.

Den enda mappen 2024–2025 utan protokoll är kommunstyrelsens
arbetsutskott 2025-09-09; kallelsen finns. Raderna för 2026 före dagens
datum står kvar med mötessidan som källa, eftersom den visar ändringar
och inställda möten.

Kommer äldre år för alla organ in i poolen ur arkivet
([ADR-0047](0047-alla-organ-lases-ur-arkivet.md)) kan kalendern gå
längre bakåt på samma sätt.
