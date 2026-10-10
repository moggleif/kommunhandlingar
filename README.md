# kommunhandlingar

En datapool med kommunernas politiska handlingar: kallelser, handlingar och
protokoll från kommunfullmäktige, kommunstyrelsen och nämnderna, så långt
bakåt som de går att hitta. Varje dokument konverteras till Markdown, och
tabeller dessutom till CSV, så att det går att bygga analyser ovanpå.

Kungsbacka först. Ingenting i koden ska veta vilken kommun det gäller – det
står i en konfigurationsfil per kommun.

Vad poolen innehåller just nu, vilka sammanträden som saknar kallelse
och handlingar eller protokoll, och varje dokument med sina tabeller, går
att läsa på webbplatsen:
<https://moggleif.github.io/kommunhandlingar/>.

## Hur det fungerar

PDF:en hämtas tillfälligt, konverteras och raderas. Kvar blir texten, och
överst i varje Markdown-fil står varifrån den kom och hur väl
konverteringen lyckades ([fälten](docs/03-ARKITEKTUR.md#front-matter)).
Bakgrunden står i [ADR-0001](docs/decisions/0001-ett-repo-bara-text.md).

## Dokumentation

- [AGENTS.md](AGENTS.md) – regler för alla som arbetar i repot, människa som AI
- [docs/01-BIDRA.md](docs/01-BIDRA.md) – hur man sätter upp och kör kontrollerna
- [docs/02-KRAV.md](docs/02-KRAV.md) – vad poolen ska göra
- [docs/03-ARKITEKTUR.md](docs/03-ARKITEKTUR.md) – hur den byggs
- [docs/decisions/](docs/decisions/) – arkitekturbeslut, med diskussionen bakom
- [docs/kallor/kungsbacka.md](docs/kallor/kungsbacka.md) – hur Kungsbacka
  publicerar sina handlingar, och vad som återstår att verifiera

## Vad som återanvänds från politik-repot

Repot byggs inte vidare; följande kopieras in och anpassas:

| Från `moggleif/politik` | Används till |
|---|---|
| `scripts/pdftabell.py` | Tabeller ur ordens koordinater, när textlagret saknar avgränsare |
| `hamta()` i `scripts/hamta_fullmaktige.py` | Mönstret för väntetid och omförsök vid 429 |
| `data/KALLOR.md` (Kungsbacka-avsnitten) | Utgångspunkt för `docs/kallor/kungsbacka.md` |
| Lärdomen om Wayback | Kopior kapas tyst; se [docs/kallor/kungsbacka.md](docs/kallor/kungsbacka.md#2-internet-archive-wayback) |
| Regeln "hellre stanna än spara fel" | Konverteringen märker eller avbryter, gissar aldrig |

Politik-repot kan i sin tur senare läsa ur poolen i stället för att hämta
nämndhandlingar själv.

## Licens

[MIT](LICENSE) gäller koden. Texten och tabellerna i `data/` återger
kommunernas allmänna handlingar och får ingen egen licens här. Bilagor kan
innehålla verk av andra än kommunen, och där finns upphovsrätten kvar.
