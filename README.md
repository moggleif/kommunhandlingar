# kommunhandlingar

En datapool med kommunernas politiska handlingar: kallelser, handlingar och
protokoll från kommunfullmäktige, kommunstyrelsen och nämnderna, så långt
bakåt som de går att hitta. Varje dokument konverteras till Markdown, och
tabeller dessutom till CSV, så att det går att bygga analyser ovanpå.

Kungsbacka först. Ingenting i koden ska veta vilken kommun det gäller – det
står i en konfigurationsfil per kommun.

## Hur det fungerar

PDF:en hämtas tillfälligt, konverteras och raderas. Kvar blir texten, och
överst i varje Markdown-fil står varifrån den kom, när den hämtades och
konverterades, originalets sha256 och hur väl konverteringen lyckades.
Bakgrunden står i [ADR-0001](docs/adr/0001-var-datapoolen-ska-bo.md).

## Dokumentation

- [docs/adr/](docs/adr/) – arkitekturbeslut, med diskussionen bakom
- [docs/kallor/kungsbacka.md](docs/kallor/kungsbacka.md) – hur Kungsbacka
  publicerar sina handlingar, och vad som återstår att verifiera
## Vad som återanvänds från politik-repot

Repot byggs inte vidare; följande kopieras in och anpassas:

| Från `moggleif/politik` | Används till |
|---|---|
| `scripts/pdftabell.py` | Tabeller ur ordens koordinater, när textlagret saknar avgränsare |
| `hamta()` i `scripts/hamta_fullmaktige.py` | Mönstret för väntetid och omförsök vid 429 |
| `data/KALLOR.md` (Kungsbacka-avsnitten) | Utgångspunkt för `docs/kallor/kungsbacka.md` |
| Lärdomen om Wayback | Kontrollera `%%EOF`; kopior kapas tyst vid 1 MiB |
| Regeln "hellre stanna än spara fel" | Konverteringen märker eller avbryter, gissar aldrig |

Politik-repot kan i sin tur senare läsa ur poolen i stället för att hämta
nämndhandlingar själv.
