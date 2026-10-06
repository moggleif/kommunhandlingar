# Krav (beteenden)

Kraven beskriver hur det färdiga systemet fungerar, som Given/When/Then.
Varje krav får ett GitHub-issue när arbetet på det börjar.

## Syfte

Samla **alla** politiska handlingar och protokoll från kommunfullmäktige,
kommunstyrelsen och samtliga nämnder, så långt bakåt som möjligt, som text
och tabeller att bygga dataanalyser på. Kungsbacka först; fler kommuner ska
kunna läggas till utan kodändring.

## K1 — En kommun läggs till med konfiguration

- **Givet** att en kommun publicerar via en plattform som redan har en adapter
- **När** någon skriver `kommuner/<kommun>.yaml` med organ, startadresser och
  filnamnsmönster
- **Så** hämtas och konverteras kommunens handlingar utan att någon kod ändras.

## K2 — Alla organ och dokumenttyper hittas

- **Givet** en kommuns konfiguration
- **När** upptäckten körs
- **Så** listas varje sammanträde för varje organ i konfigurationen, med
  kallelse, handlingar, protokoll och bilagor som separata dokument, var
  och ett med organ, datum, typ och källnyckel.

## K3 — Historiken hämtas så långt bakåt den finns

- **Givet** att kommunens webbplats bara visar de senaste åren
- **När** upptäckten körs
- **Så** prövas också de äldre källor konfigurationen anger (t.ex. Internet
  Archive och kommunens diarium), och varje dokument registreras med den
  källa det hittades i.

## K4 — Varje dokument blir en Markdown-fil med härkomst

- **Givet** ett hämtat PDF-dokument
- **När** det konverteras
- **Så** skrivs en `.md` vars front matter anger källänk, originalets
  sha256, tid för hämtning och konvertering, pipelineversion och
  kvalitet – och PDF:en raderas.

## K5 — Tabeller blir CSV

- **Givet** ett dokument med tabeller
- **När** det konverteras
- **Så** skrivs varje tabell som en CSV-fil bredvid dokumentets `.md`,
  med sidnummer, och tabellen syns också i Markdown-texten.
- **Givet** en tabell som inte går att läsa säkert
- **Så** märks den som osäker i stället för att sparas som om den vore riktig.

## K6 — Det som inte gick att konvertera syns

- **Givet** ett dokument som inte gick att konvertera, helt eller delvis
- **När** konverteringen är klar
- **Så** finns ändå en `.md` med metadata, kvalitetsnivå per dokument och
  per sida, och status – dokumentet utelämnas aldrig.

## K7 — Luckor redovisas

- **Givet** ett sammanträde som vi vet har hållits
- **När** ett av dess dokument inte hittas i någon källa
- **Så** registreras det som saknat, med vilka källor som prövats och när.

## K8 — Körningen är inkrementell och kan avbrytas

- **Givet** att poolen redan innehåller tidigare körningar
- **När** en ny körning startas
- **Så** hämtas och konverteras bara dokument som är nya eller har ändrats,
  och en avbruten körning fortsätter där den slutade.

## K9 — Ändrade dokument blir nya versioner

- **Givet** att kommunen byter ut en fil som redan finns i poolen – under
  samma adress, eller under ny adress eller nytt filnamn med samma
  källnyckel
- **När** nästa körning hittar den nya filen
- **Så** konverteras den nya versionen och skrivs över den gamla på samma
  sökväg, och git-historiken visar vad som ändrats.

- **Givet** att filen under en ny adress har samma sha256 som den som
  redan finns
- **När** nästa körning hittar den
- **Så** uppdateras bara `kalla_url`, och texten konverteras inte om.

## K10 — Hämtningen är artig

- **Givet** vilken källa som helst
- **När** något hämtas
- **Så** följs `robots.txt`, User-Agent anger vem vi är och hur vi nås,
  anropen till samma värd ligger minst det konfigurerade intervallet isär,
  och 429/5xx leder till att körningen väntar och backar.
