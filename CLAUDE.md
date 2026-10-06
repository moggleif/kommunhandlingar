# CLAUDE.md – kommunhandlingar

Vägledning för var och en som arbetar i repot, människa som AI-agent.

## Regler

- **Besluten står i `docs/adr/`.** En ny princip blir en ny ADR, med
  alternativen och diskussionen bakom. Rekommendationer skrivna av Claude
  märks som Claudes.
- **Inget hårdkodat om en kommun.** Kommunnamn, organ, adresser och
  filnamnsmönster står i konfigurationen per kommun, aldrig i koden.
- **Varje textfil bär sin härkomst**: källänk, sha256, tid för hämtning och
  konvertering, och konverteringens kvalitet.
- **Tomt är inte noll.** Ett dokument som inte gick att konvertera, eller
  ett möte som saknar protokoll, registreras som det – det utelämnas inte.
- **Hellre stanna än spara fel.** Osäkra tabeller märks som osäkra.
- **Artig hämtning**: följ robots.txt, säg vem vi är, håll avstånd mellan
  anropen.
- **Namn skrivs på svenska**, i kod som i data.
- **Gren, inte `main`.**
