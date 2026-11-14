---
status: proposed
date: 2026-11-14
decision-makers: projektägaren
consulted: AI-agenten
---

# Arkivet konverterar om sina egna dokument från en annan version av poolen, efter luckorna

## Context and Problem Statement

Omkonverteringen (ADR-0019) har fört de levande källornas dokument till
version 0.11.0, men 1 573 dokument ur webbarkivet står kvar på äldre
versioner ([#84](https://github.com/moggleif/kommunhandlingar/issues/84)).
Arkivsteget fyller bara luckor (ADR-0018): en kandidat vars källnyckel
finns i poolen utan `ej-hamtad` hämtas inte, också när dokumentet kom ur
arkivet självt och är från en annan version. Med dagens kod blir #84
aldrig klar för dem.

Projektägaren beslutade 2026-11-14 att arkivets dokument ska konverteras
om innan #84 stängs. Hur ska arkivsteget göra det, utan att en kopia ur
arkivet någonsin ersätter ett dokument från en levande källa?

## Decision Drivers

* **Levande källor går före arkivet** (ADR-0018). En kopia ur arkivet
  ersätter aldrig ett dokument från en levande källa.
* **Luckor går före omkonvertering** (ADR-0019): ett dokument som saknas
  är värre än ett som är läst av en äldre version.
* **Samma regel som för de levande.** Flaggan `omkonvertera`, versionen i
  `pipeline` och undantaget för granskade dokument (ADR-0055) ska gälla
  likadant.
* **Enkelt först.** Ingen ny flagga och inget nytt steg.

## Considered Options

* A – Arkivets kandidat med samma källnyckel och samma `kalla_url` som ett
  dokument från en annan version konverteras om, efter luckorna
* B – Ett eget kommando som konverterar om arkivets dokument utanför
  nattkörningen
* C – #84 stängs med de levande källorna, och arkivets dokument står kvar
  på sina versioner

## Decision Outcome

Valt: A, eftersom villkoret redan finns för de levande källorna
(`bara_omkonvertering`) och bara behöver gälla också i arkivet.

* **Signalen** är densamma som i ADR-0019: kommunfilen har
  `omkonvertera = true`, dokumentet är fullständigt och inte granskat,
  dess `pipeline` har en annan version av poolen än den som körs, och
  kandidaten har samma källnyckel och samma `kalla_url`.
* **Bara arkivets egna dokument.** Ett dokument från en levande källa har
  en `kalla_url` utanför `https://web.archive.org/web/`, och en kandidat
  ur arkivet har aldrig samma `kalla_url`. Regeln om luckor gäller därför
  oförändrad för dem.
* **Ordningen.** Omkonverteringarna tas sist i arkivets lista, efter
  luckorna, som för de levande källorna (`ordna`).
* **Resten följer ADR-0019**: samma sha256 skrivs om på samma sökväg och
  räknas som "konverterad om", och går kopian inte att hämta står den
  gamla `.md` kvar.

### Consequences

* Bra, eftersom hela poolen kan föras till samma version, och #84 kan
  stängas när sammanfattningen inte längre har några "konverterad om".
* Bra, eftersom koden blir ett villkor.
* Dåligt, eftersom 1 573 kopior hämtas igen ur webbarkivet. Med arkivets
  intervall och konverteringen tar det flera nätter, efter de levande
  källorna.
* Dåligt, eftersom en kopia som försvunnit ur arkivet försöks igen varje
  natt, som ett försvunnet original i ADR-0019.
* Neutralt, eftersom varje höjning av versionen framöver konverterar om
  också arkivets dokument.

### Confirmation

Tester i `tests/test_hamta_arkiv.py`: ett dokument ur arkivet från en
annan version konverteras om, ett från samma version är en lucka som
förut, ett dokument från en levande källa rörs inte av arkivets kandidat
med samma källnyckel, och arkivets omkonverteringar tas efter dess
luckor.

## Pros and Cons of the Options

### A – Arkivet konverterar om sina egna

* Bra, eftersom regeln är densamma för alla källor.
* Bra, eftersom den levande källans företräde inte ändras.
* Dåligt, eftersom arkivet hämtas igen vid varje höjning av versionen.

### B – Ett eget kommando

* Bra, eftersom nattkörningens tid inte påverkas.
* Dåligt, eftersom det blir en andra väg in i poolen, med egna kontroller
  och en egen gren.
* Dåligt, eftersom det behöver köras för hand vid varje höjning.

### C – Arkivets dokument står kvar

* Bra, eftersom ingenting behöver hämtas.
* Dåligt, eftersom poolen då har två versioner av konverteringen sida vid
  sida, och arkivets dokument saknar det som lagts till sedan de lästes.

## More Information

Frågan togs upp i #274, eftersom arkivsteget aldrig fick tid när
nattkörningen fastnade. Projektägaren valde att konvertera om arkivet
(A eller B) framför att stänga #84 med de levande källorna (C), och
agenten föreslog A för att inte bygga en andra väg in i poolen.

ADR-0018 står kvar: arkivet fyller luckor och ersätter aldrig ett
dokument från en levande källa. Det här beslutet lägger till att arkivet
håller sina egna dokument på poolens version.
