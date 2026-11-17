---
status: accepted
date: 2026-11-17
decision-makers: projektägaren
consulted: AI-agenten
---

# Alla sidor över tid visar samma år, från poolens första till innevarande

## Context and Problem Statement

Sidorna om mål och direktiv och om spåren över tid (ADR-0050, ADR-0057)
har en kolumn per år. Åren gick från sidans första till dess sista rad,
så en sida med rader bara ett år visade ett enda år, och en sida utan
rader de senaste åren slutade före innevarande år. Två organ eller två
flikar gick inte att jämföra med en blick, och ett tomt år i kanten såg
ut som ett år som inte fanns. Projektägaren vill att alla flikar och
organ visar samma år.

## Decision Drivers

* **Jämförbart:** samma kolumner på varje sida i en kommun.
* **Tomt är inte noll:** ett år utan rader ska synas som tomt, inte
  försvinna.
* **Inget hårdkodat om en kommun:** spannet räknas ur poolen.
* **Ingen rad göms:** en budget för nästa år eller ett äldre ärende ska
  fortfarande få en kolumn.

## Considered Options

* A – Kommunens spann: från poolens första år till byggåret, utvidgat
  med kommunens alla rader
* B – Ett fast första år per kommun i kommunfilen
* C – Organets spann: från organets första dokument till byggåret

## Decision Outcome

Valt: A, eftersom det ger samma år överallt utan något nytt fält i
kommunfilen och inte göms något.

* **Spannet** börjar med det tidigaste av poolens äldsta årskatalog och
  kommunens rader i mål-, uppföljnings- och spårfilerna, och slutar med
  det senaste av byggåret och raderna. När beslutet fattades gav det
  Kungsbacka 2010–2027, eftersom ett initiativärende väcktes 2010 och
  fullmäktiges budget för 2027 fanns.
* **Målsidan:** ett år utan dokument från organet och utan mål är en
  lucka i poolen bara fram till byggåret. Rutan bredvid grafen, urvalet
  "Gäller" och förvalet i Ett år i taget står för målens senaste år.
* **Ändrar** åren i ADR-0050 (målsidan), ADR-0057 (spårsidorna) och
  ADR-0073 (Ett år i taget), som gick från sidans första till sista år.
* **Spårsidorna:** ett år utan steg är en tom kolumn och ett tomt fält
  i kortets remsa, som förut.

### Consequences

* Good, eftersom alla flikar och organ har samma kolumner.
* Good, eftersom ett organ som saknar rader de senaste åren syns som
  det.
* Bad, eftersom tidslinjen blir bredare: Kungsbacka får 18 kolumner. Den
  rullar i sidled som förut.
* Neutral, eftersom ett nytt äldre dokument eller en ny budget flyttar
  kanten för alla sidor i kommunen. Ett felläst år i en rad gör det
  också; raderna skrivs för hand och granskas, så det prövas inte
  särskilt.
* Bad, eftersom ett organ som bildats sent får luckor åren innan det
  fanns. Metodtexten säger det.

## Pros and Cons of the Options

### B – Ett fast första år i kommunfilen

* Good, eftersom kanten inte flyttar sig.
* Bad, eftersom det är ett fält till att hålla i takt med poolen, och
  rader före året skulle gömmas.

### C – Organets spann

* Good, eftersom ett organ som bildats sent inte får tomma år.
* Bad, eftersom organen och flikarna inte längre går att jämföra, vilket
  var själva önskemålet.
