---
status: accepted
date: 2026-11-16
decision-makers: projektägaren
consulted: AI-agenten
---

# Handlingar och protokoll är menyns första post, och kalendern har ingen stig

## Context and Problem Statement

Med en enda kommun är översikten startsidan och heter "Handlingar och
protokoll" ([ADR-0082](0082-en-kommuns-grupper-ar-menyns-poster.md)). Den
nåddes bara genom sajtens namn och genom stigen under kalenderns rubrik,
så den såg ut att höra till kalendern. Ägaren bad 2026-11-16 att den
flyttas från kalendern in i menyn.

## Considered Options

* "Handlingar och protokoll" som första post i menyn, och ingen stig på
  kalendern.
* Menyposten, och stigen kvar på kalendern.
* Översikten som en länk i undermenyn "Om poolen".
* Bara sajtens namn som länk till översikten, som förut.

## Decision Outcome

Valt: "Handlingar och protokoll" som första post i menyn, och ingen stig på
kalendern, eftersom det är vad ägaren bad om.

Med en enda kommun är menyns första post länken "Handlingar och
protokoll" till startsidan, före "Kalender". Kalendersidan har ingen stig,
med en eller flera kommuner: den står bredvid översikten i menyn, inte
under den. Organens, dokumentens och sammanträdenas sidor behåller sin
stig. Kungsbacka får sex poster, som är menyns tak
([ADR-0081](0081-menyn-i-projektets-gemensamma-form.md)).

### Consequences

* Bra, eftersom översikten nu syns i menyn och inte ser ut att ligga under
  kalendern.
* Dåligt, eftersom en kommunfil med fyra grupper och en kalender skulle ge
  sju poster. Ingen av dagens kommunfiler har det.

## More Information

Med stigen kvar skulle översikten fortfarande se ut att ligga ovanför
kalendern, vilket var felet. Under "Om poolen" hamnar den bland sidor om
poolen, inte om handlingarna. Sajtens namn ensamt räckte inte: ägaren såg
inte att det var en länk till handlingarna. Beslutet ändrar vilka poster
menyn har enligt
[ADR-0082](0082-en-kommuns-grupper-ar-menyns-poster.md); resten av 0082
gäller.
