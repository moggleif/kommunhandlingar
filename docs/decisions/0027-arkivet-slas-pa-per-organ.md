---
status: accepted
date: 2026-10-11
decision-makers: projektägaren
consulted: AI-agenten
---

# Arkivet slås på per organ, med en lista över organen i källans `wayback`

## Context and Problem Statement

Enligt [ADR-0018](0018-wayback-sist-nyast-forst-och-bara-luckor.md) slås
Internet Archive på per källa med `wayback = true`, och arkivets lista tas
nyast först för alla organ. Kungsbackas källa har 17 mötessidor och
Sitevision-generationen 2021–2023 omkring 1 400 filer i arkivet. Ägaren
vill ha alla dokument för Gymnasium & Arbetsmarknad (`ga`) ur arkiven,
cirka 65 filer, utan att resten av arkivet hämtas innan konverteringen är
färdig ([#87](https://github.com/moggleif/kommunhandlingar/issues/87)).

Hur slås arkivet på för ett organ, men inte för de andra i samma källa?

## Decision Drivers

* **Konverteringen först.** Det som hämtas nu ska konverteras om senare;
  hela arkivet ska inte hämtas förrän konverteringen är färdig.
* **Inget hårdkodat om en kommun.** Vilka organ som läses ur arkivet står
  i kommunfilen.
* **Enkelt först.** Ingen ny ordning, ingen ny källtyp.

## Considered Options

* A – `wayback` blir en lista med organens id, `wayback = ["ga"]`
* B – `wayback = true` som förut, och arkivet får ta flera nätter
* C – Arkivets lista tas organ för organ, som de levande källorna (K13),
  i stället för nyast först
* D – En andra källa i kommunfilen med bara `ga` och `wayback = true`

## Decision Outcome

Valt: A, eftersom det ger ägaren det den ber om med en rad i kommunfilen
och ett par rader kod, och lämnar ordningen i ADR-0018 orörd.

* **Fältet.** `wayback` är en lista med id för organ som har en mötessida
  i källan. Bara de organens mötessidor läses ur arkivet. Utelämnas fältet
  läses inget ur arkivet. Ett id utan mötessida i källan stoppar körningen
  som andra fel i kommunfilen (K1).
* **Allt annat är som i ADR-0018:** arkivet körs sist, nyast först, och
  fyller bara luckor.
* **Kungsbacka** får `wayback = ["ga"]`.

Det ersätter den del av ADR-0018 som säger att arkivet slås på per källa.

### Consequences

* Bra, eftersom ägaren väljer organ för organ när arkivet ska hämtas, och
  ett organ till är en rad i kommunfilen.
* Bra, eftersom `true` försvinner och fältet har en enda form.
* Dåligt, eftersom en källa som ska läsas helt ur arkivet måste räkna upp
  alla sina organ. Det är 17 id i Kungsbackas fall, och de står redan
  under `kalla.sidor`.

### Confirmation

`tests/test_sitevision_arkiv.py` prövar att bara de listade organens
mötessidor frågas i arkivet, och `tests/test_konfiguration.py` att ett
okänt organ eller ett värde som inte är en lista stoppar körningen.

## Pros and Cons of the Options

### A – En lista med organ

* Bra, eftersom det är det minsta som gör jobbet.
* Dåligt, eftersom kommunfilens schema ändras och äldre filer med
  `wayback = true` måste skrivas om. Bara Kungsbackas finns, med `false`.

### B – Hela källan, flera nätter

* Bra, eftersom ingen kod ändras.
* Dåligt, eftersom alla organs arkiv hämtas innan konverteringen är
  färdig, tvärt emot ägarens prioritering, och `ga` blandas med de andra.

### C – Organ för organ i arkivet

* Bra, eftersom `ga` står först i Kungsbackas organlista och hämtas först.
* Dåligt, eftersom ADR-0018 valde nyast först för att fylla de senaste
  luckorna i alla organ, och resten av arkivet hämtas ändå efter `ga`.

### D – En andra källa

* Bra, eftersom ingen kod ändras.
* Dåligt, eftersom den levande upptäckten då läser mötessidan två gånger
  och får varje kandidat dubbelt, och mönstren måste upprepas.

## More Information

Ägaren bad 2026-10-11 om alla dokument för Gymnasium & Arbetsmarknad,
"tillbaka till 2010 eller vad vi kunde finna". Agenten jämförde först den
levande mötessidan med poolen: alla 98 filer fanns redan. Det som finns
utöver dem ligger i arkivet: Sitevision 2021–2023, som koden redan läser,
och två äldre Episerver-generationer 2013–2022, som kräver en ny adapter.
Agenten föreslog att dela upp arbetet: arkivet per organ nu, så att
nattkörningen hämtar `ga` 2021–2023, och ett eget issue för
Episerver-generationerna. Ägaren valde det.

Omkonverteringen (ADR-0019) slogs inte på samtidigt. Den körs före
arkivet och gäller alla organ, så den hade tagit tidsbudgeten innan
arkivet stod på tur.
