---
status: proposed
date: 2026-10-22
decision-makers: projektägaren
consulted: AI-agenten
---

# Initiativärendena följs steg för steg som lokalbehoven, med samma kod och avsändaren som värde

## Context and Problem Statement

En ledamot eller ett parti kan väcka ett initiativärende i nämnden. Det
remitteras oftast till förvaltningen och kommer tillbaka på ett senare
möte, där nämnden bifaller, avslår eller anser det besvarat. Ibland
följer en återrapport, ett beslut i kommunstyrelsen eller något som
genomförs. Stegen står i olika protokoll, ibland år efter varandra, och
inget dokument samlar dem
([#191](https://github.com/moggleif/kommunhandlingar/issues/191)).

Webbplatsen ska visa varje initiativärende över tid med en källa för
varje steg, och vem som väckte det: ett parti, flera partier eller
Alliansen. Lokalbehoven har redan en sådan sida (ADR-0057). Hur byggs
sidan om initiativärendena utan att koden för lokalbehoven skrivs en
gång till, och var står avsändaren?

## Decision Drivers

* **Varje uppgift bär sin härkomst**, också avsändaren.
* **Ingen abstraktion förrän det finns två konkreta fall** – och nu finns
  två.
* **Sidan drar inga slutsatser** om ärendena.
* **Inga personnamn i repots texter**; ledamöternas namn står i källan.
* **Inget hårdkodat om en kommun.**

## Considered Options

* A – En gemensam modell för spår över tid, där lokalbehov och
  initiativärenden är två slag med egna faser och texter, och avsändaren
  är värdet i steget `vackt`
* B – Som A, men avsändaren i en egen kolumn
* C – En egen kopia av lokalbehovens kod för initiativärendena
* D – Initiativärendena som ett nytt slag av mål i målfilen

## Decision Outcome

Valt: A, eftersom läsningen, kontrollen mot poolen, ikonerna,
tidslinjen och korten redan finns för lokalbehoven och skiljer sig bara
i data, och eftersom avsändaren då prövas mot källans sida som andra
värden utan någon ny kolumn.

* **Koden** för lokalbehoven blir gemensam för spår över tid
  (`spar.py`, `sparsida.py`, `sparkort.py`, `sparikon.py`). Det som
  skiljer slagen åt – katalogen, kolumnens namn, faserna med ikoner,
  värdenas form, sidans text och vilken fas som bär avsändaren eller
  ger urvalet för senaste året – står som data i `sparslag.py`.
* **Filen** är `initiativ/<kommun>.csv` med lokalbehovsfilens kolumner,
  men `arende` i stället för `behov`. Faserna är `vackt`, `beredning`,
  `bifall`, `avslag`, `besvarat`, `uppfoljning` och `genomfort`.
  Beslutets utfall är en egen fas, så att det får en egen ikon och ett
  eget urval.
* **Avsändaren** är värdet i `vackt` och krävs. Den skrivs som källan
  skriver den: en partiförkortning, `Alliansen`, eller partiernas namn
  när källan räknar upp dem. Sidan räknar och väljer per avsändare.
* **Sidan** är `<kommun>/<organ>/initiativ.html`, länkad från organets
  sida, och ser ut som lokalbehovssidan med avsändaren bredvid namnet.

### Consequences

* Good, eftersom en tredje sida av samma slag bara är en ny post i
  `sparslag.py`, en CSV, färger för nya faser i `spar.css` och en text i
  dokumentationen.
* Good, eftersom avsändaren går att kontrollera med ett klick och sidan
  kan visa vilka partier som väcker initiativ och hur det går.
* Neutral, eftersom lokalbehovssidans adresser till korten byter namn
  (`#behov-N` blir `#sak-N`) och urvalet för senaste året heter
  `senaste` i stället för `aktiv`.
* Bad, eftersom prövningen av en kort avsändare som `S` mot källans sida
  är svag: bokstaven finns på nästan varje sida. Texten i steget, som
  prövas på samma sätt, är det som visar att avsändaren stämmer.
* Bad, eftersom samma grupp kan stå på två sätt, `Alliansen` och fyra
  partinamn, och då får två knappar i urvalet.

### Confirmation

`tests/test_initiativ.py` prövar läsningen, kontrollerna, sidan med
avsändare och urval, bygget och att Kungsbackas fil går igenom
kontrollen mot poolen. `tests/test_lokalbehov.py` visar att
lokalbehovssidan fungerar som förut med den gemensamma koden.

## Pros and Cons of the Options

### A – Gemensam modell, avsändaren som värde

* Good, eftersom ingen kod kopieras.
* Good, eftersom avsändaren prövas mot källan utan ny kontroll.
* Bad, eftersom lokalbehovens moduler byter namn i samma ändring.

### B – Avsändaren i en egen kolumn

* Good, eftersom kolumnen säger vad den är.
* Bad, eftersom kolumnen bara gäller ett steg i ett slag och står tom på
  alla andra rader, och behöver en egen prövning mot källan.

### C – En kopia av lokalbehovens kod

* Good, eftersom lokalbehoven inte rörs.
* Bad, eftersom fem filer kopieras med små skillnader och två ställen
  måste rättas vid varje fel.

### D – Initiativen i målfilen

* Good, eftersom målsidan redan har urval och kort.
* Bad, eftersom ett initiativ inte är ett mål: det har ett beslut och
  ett utfall, inte en status år för år, och källorna är andra organs.

## More Information

Projektägaren bad om sidan 2026-10-22, "precis som lokalplan", och ville
fånga återkopplingen, hur nämnden beslutar, uppföljningarna och om
förslaget blir genomfört, och sedan också vilka partier, Alliansen eller
ett eller flera partier som initiativet kommer ifrån. Agenten
rekommenderade i fas 0 bara initiativ väckta i nämnden, avsändaren med
källans ord och en gemensam modell i stället för en kopia; projektägaren
sa ja till alla tre.

Avsändaren skrivs med förkortning (`S`, `KD`, `SD`) även när texten i
källan säger "Socialdemokraterna", så att samma parti får en knapp.
Fyra partinamn utan ordet Alliansen skrivs som källan skriver dem, för
att inte gissa.

Under genomgången visade det sig att flera möten har protokollet i flera
filer, och att några initiativ bara står i den andra filen. En sökning
som bara läser `protokoll.md` missar dem.

Ett initiativ som bygger på ett tidigare, som Alliansens yrkande
2021-11-10 efter utredningen av initiativet från mars samma år, har eget
diarienummer och står som ett eget ärende.

Ett protokoll (2024-06-12) har en beslutstext som säger att
förvaltningen får i uppdrag att utreda, medan beslutsgången och
omröstningen säger att nämnden avslog initiativet. Steget står som
avslag med omröstningens ord som text.
