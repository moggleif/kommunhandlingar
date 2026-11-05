---
status: proposed
date: 2026-11-05
decision-makers: projektägaren
consulted: AI-agenten
---

# I arkivet gäller filnamnets datum under ett annat möte samma år, ett tvåsiffrigt år är 2000-talets, och statussidan visar år utan dokument

## Context and Problem Statement

Arkivets upptäckt 2026-11-04 gav 1 239 filer utan kandidat
([#217](https://github.com/moggleif/kommunhandlingar/issues/217)). 806 av
dem har ingen kopia i arkivet. Kommunen har också tagit bort dem från sin
webbplats, så de går inte att hämta. Resten hade orsaker som går att
åtgärda:

* **159 filer där filnamnet och mötesrubriken säger olika datum.** I
  arkivets kopior av Sitevision-sidorna 2021–2023 står filer ofta under ett
  annat möte, se [kallor/kungsbacka.md](../kallor/kungsbacka.md#kända-fel-i-källan).
  K2 och ADR-0011 säger att filen då inte blir någon kandidat utan en
  rättelse i kommunfilen.
* **Tvåsiffrigt år utan streck** i Sitevision-filnamn ("Protokoll
  231018.signerad.pub.pdf"). Sitevisions mönster krävde fyra siffror, och
  rubriken på den kopian hade inget datum. Därför saknas GA:s protokoll
  från hösten 2023.
* **Föredragningslistor och revisionens filer** hos Episerver, som inget
  typmönster kände igen ("KSAU_lista140318.pdf",
  "kommunrev.-2020-04-20--227-240.pdf").

Statussidan visar bara luckor vid möten med minst ett dokument (ADR-0020),
så hela år utan dokument, som GA 2015–2017, syns inte.

## Decision Drivers

* **Hellre märka än gissa**, och data ska vara rätt.
* **Inget hårdkodat om en kommun**: typerna står i kommunfilen.
* **Luckorna räknas fram ur poolen** och lagras inte (ADR-0020).

## Considered Options

För datumen:

* A – I arkivet gäller filnamnets datum när rubriken är samma år och mer
  än en vecka bort
* B – En rättelse för hand per fil, belagd i dokumentets text
* C – Låta filerna vara utan kandidat

## Decision Outcome

Valt: A (projektägaren 2026-11-05), med begränsningen till samma år.

* **Datumet i arkivet.** När filnamnet och rubriken i arkivets kopia
  säger olika datum samma år, mer än en vecka isär, gäller filnamnets.
  Filen står då under ett annat möte. En vecka eller mindre kan vara ett
  flyttat möte ("5 april 2024 (flyttat från 4 april)"), och ett annat år
  kan vara ett skrivfel i filnamnet ("2121-02-08"). Båda ger ingen
  kandidat som förut, tills en rättelse finns. De levande sidorna följer
  ADR-0011 som förut.
* **Ett tvåsiffrigt år är 2000-talets** för alla adaptrar, inte bara
  Episerver (ADR-0039). Ingen källa är äldre än 2013.
* **Typerna i kommunfilen.** En föredragningslista (`_lista`) är kallelsen,
  och revisionens filer (`kommunrev.`, `sammantradesant`) är protokoll,
  som revisionens sammanträdesanteckningar redan är hos Sitevision.
* **År utan dokument.** Statussidan visar per organ de år mellan organets
  första och sista dokument som inte har något dokument, räknat ur
  poolen som luckorna.

### Consequences

* Good, eftersom 141 filer från 2021–2023, GA:s protokoll från hösten
  2023, ett trettiotal föredragningslistor och revisionens protokoll
  2019–2021 kan bli kandidater.
* Good, eftersom de stora hålen syns på statussidan.
* Bad, eftersom en fil vars filnamn har fel datum samma år, mer än en
  vecka fel, hamnar vid fel möte. Inget fall av det har setts: de
  skillnader som är skrivfel har varit ett år eller en dag.
* Neutral, eftersom ett organ som bytt namn eller inte fanns några år kan
  visa år utan dokument som aldrig hade något att visa.

### Confirmation

`tests/test_sitevision_arkiv.py` prövar filnamnets datum under ett annat
möte samma år, och att en vecka eller ett annat år inte ger någon
kandidat. `tests/test_monster.py` prövar det tvåsiffriga året,
`tests/test_luckor.py` och `tests/test_webbplats.py` åren utan dokument.
Nattkörningens sammanfattning visar hur många filer som är kvar utan
kandidat.

## Pros and Cons of the Options

### A – Filnamnets datum samma år och mer än en vecka bort

* Good, eftersom filnamnet är skrivet för just den filen, medan rubriken
  är adapterns läsning av sidans uppställning.
* Good, eftersom gränserna utesluter flyttade möten och skrivfel i året.
* Bad, eftersom ingen läser dokumentet innan datumet bestäms.

### B – En rättelse per fil

* Good, eftersom varje datum är belagt.
* Bad, eftersom 141 filer ska läsas, och arkivet nås bara från Actions.

### C – Låta dem vara

* Good, eftersom inget kan bli fel.
* Bad, eftersom 141 dokument saknas utan att statussidan visar varför.

## More Information

Analysen gjordes mot nattkörningens logg 2026-11-04. Av de 159 skillnaderna
var 141 samma år och mer än en vecka, 12 en vecka eller mindre och 6 ett
annat år. Agenten föreslog först bara gränsen på en vecka. När listan gicks
igenom visade sig de 6 med ett annat år vara samma dag och månad året
före, som ser ut som ett skrivfel i filnamnet. Därför kom kravet på samma
år till. Det gör regeln snävare än projektägarens val, inte vidare.

806 filer utan kopia i arkivet prövades mot kommunens webbplats. Två
stickprov från 2022 gav 404, så den vägen är stängd. Kvar finns
kommunens e-arkiv (#23).
