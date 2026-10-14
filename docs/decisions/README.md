# Beslut (ADR)

Beslut skrivs enligt **[MADR 4](https://adr.github.io/madr/)** (Markdown
Any Decision Records). Rubrikerna följer MADR på engelska så att formatet
känns igen; innehållet skrivs på svenska. Mall:
[adr-template.md](adr-template.md). Filnamn `NNNN-rubrik-med-bindestreck.md`.

Regler för det här repot, utöver MADR:

- Ett beslut som är svårt att ändra kommer **med en ny ADR i samma pull
  request**.
- **Minst tre alternativ**, vart och ett med för- och nackdelar.
- **Diskussionen hör hemma i ADR:en**, under *More Information*: hur
  resonemanget gick, invändningar och svar, och vad som avgjorde.
- `decision-makers` är människor och skrivs med roll, aldrig namn
  ([AGENTS.md](../../AGENTS.md), "Inga personnamn"), till exempel
  `projektägaren`. En AI-agent som gett en rekommendation står som
  `AI-agenten` under `consulted`. I texten räcker "ägaren" och "agenten"
  när det inte går att förväxla.
- Beslutet fattas av en människa. Till dess är status `proposed`.
- En accepterad ADR skrivs inte om. Undantaget är redaktionella
  ändringar som inte ändrar beslutet, som att ta bort ett personnamn.
- Ändras beslutet skrivs en ny ADR, och den gamla får
  `status: "superseded by ADR-NNNN"`.

## Index

| #    | Beslut                                                                        | Status   |
| ---- | ----------------------------------------------------------------------------- | -------- |
| 0001 | [Ett repo med bara text – PDF:en raderas efter konvertering](0001-ett-repo-bara-text.md) | accepted |
| 0002 | [Kort AGENTS.md, faserna som skills och en egen granskningsagent](0002-kort-agentfil-faser-som-skills-och-egen-granskare.md) | accepted |
| 0003 | [Dokumentet identifieras av sin plats i modellen och en källnyckel; sha256 är versionen](0003-dokumentets-identitet-och-datamodell.md) | accepted |
| 0004 | [Inkrementell körning: poolen är tillståndet och adressen är signalen](0004-inkrementell-korning-poolen-ar-tillstandet.md) | accepted (0019 lägger till omkonvertering vid en annan version) |
| 0005 | [Konvertering: pdfplumber och Tesseract, tal bara från textlagret, och kvalitet som den sämsta sidan avgör](0005-konvertering-verktyg-ocr-och-kvalitet.md) | accepted (0016 skärper av säker tabell, 0033 märker talrader i linje, 0034 fäller avskurna tabeller, 0036 tar bort mellanslag inne i en siffra) |
| 0006 | [Körningen sker varje natt i GitHub Actions och checkar in data direkt till `main` efter datakontrollerna](0006-schemalagd-korning-i-actions-och-data-direkt-till-main.md) | accepted |
| 0007 | [Poolen är en ögonblicksbild: det som en gång checkats in tas inte bort, och historiken skrivs inte om](0007-poolen-ar-en-ogonblicksbild.md) | accepted |
| 0008 | [Kommunkonfigurationen skrivs i TOML, en fil per kommun, och artigheten per värd står i en gemensam fil](0008-kommunkonfigurationen-i-toml.md) | accepted |
| 0009 | [Tabellernas härkomst är dokumentets, sidnumret står i filnamnet, och CSV skrivs i ett fast format](0009-tabellernas-harkomst-och-csv-format.md) | accepted (0024 lägger till ett namn för tabeller över flera sidor) |
| 0010 | [Kandidaterna hämtas organ för organ i konfigurationens ordning, och inom organet protokoll före handlingar](0010-ordningen-organ-for-organ.md) | accepted (0018 ger en ny ordning för ny historik, 0019 lägger omkonverteringen sist) |
| 0011 | [Sitevision-adaptern tar organet från sidan, datumet ur filnamnet eller rubriken, och avvikande datum rättas i kommunfilen](0011-sitevision-organ-fran-sidan-datum-och-rattelser.md) | accepted |
| 0012 | [Webbplatsen byggs ur poolen i GitHub Actions och publiceras på GitHub Pages utan att checkas in](0012-webbplatsen-byggs-i-actions-och-publiceras-pa-pages.md) | accepted (0023 lägger till markdown-it-py för dokumenten, 0032 ett skript för kalendern, 0044 ett skript för målen) |
| 0013 | [Hämtningen görs med standardbiblioteket och en egen läsning av robots.txt, och kandidatlistan skrivs som JSON](0013-artig-hamtning-och-kandidatlistan.md) | accepted |
| 0014 | [Markdown-texten har en kommentar per sida, uppställningen kvar och de säkra tabellerna efter sidans text](0014-markdown-texten-och-steg-2.md) | accepted (0021 lägger till escapning) |
| 0015 | [Nattkörningen checkar in på en egen gren, och datat når `main` genom en PR med samma kontroller som all annan ändring](0015-nattkorningen-pa-egen-gren-och-pr.md) | accepted |
| 0016 | [Tabeller utan lodräta linjer läses ur textlagrets ord och blir CSV bara när talen står i linje](0016-tabeller-utan-lodrata-linjer.md) | accepted (0028 delar tabeller med linjer och flera tal i en cell; 0030 fäller en ombruten etikett; 0035 tar med avsnittsrubriker och årtal) |
| 0017 | [Sidor med figurer märks vid konverteringen och tolkas i efterhand av en Claude-session](0017-figurer-marks-och-tolkas-i-efterhand.md) | accepted |
| 0018 | [Wayback hämtas sist i nattkörningen, nyast först, och fyller bara luckor](0018-wayback-sist-nyast-forst-och-bara-luckor.md) | accepted (0027 slår på arkivet per organ) |
| 0019 | [Ett dokument från en annan version av poolen hämtas igen och konverteras om, efter alla andra kandidater](0019-omkonvertering-efter-poolens-version.md) | accepted |
| 0020 | [Luckorna räknas fram ur poolen på statussidan och lagras inte](0020-luckor-raknas-fram-lagras-inte.md) | accepted |
| 0021 | [Poolens text escapas vid konverteringen så att den är riktig Markdown, och CI kör Markdown-lint](0021-texten-ar-riktig-markdown.md) | accepted |
| 0022 | [Personnummer, mobilnummer, e-post och gatuadresser maskas vid konverteringen; namn står kvar](0022-personuppgifter-maskas-vid-konverteringen.md) | accepted |
| 0023 | [Webbplatsen renderar poolens dokument med markdown-it-py, en sida per dokument och en per organ](0023-dokumenten-pa-webbplatsen-med-markdown-it-py.md) | accepted |
| 0024 | [En tabell som fortsätter på nästa sida slås ihop vid konverteringen när ingenting står emellan, och filnamnet anger sidorna](0024-tabeller-over-flera-sidor-slas-ihop.md) | accepted |
| 0025 | [Konverteringen mäts mot ett facit för utdrag ur riktiga handlingar, och måtten för varje version låses i en fil som testet prövar](0025-facit-for-konverteringen.md) | accepted |
| 0027 | [Arkivet slås på per organ, med en lista över organen i källans `wayback`](0027-arkivet-slas-pa-per-organ.md) | accepted (0047 läser alla organ utan att vänta på konverteringen) |
| 0028 | [En tabell med linjer och flera tal i en cell delas efter linjerna i andra rader och efter textraderna](0028-tabeller-med-linjer-delas-efter-linjer-och-textrader.md) | accepted |
| 0029 | [Tal i linje utan lodrät linje emellan blir kolumner i en tabell med linjer](0029-tal-i-linje-utan-lodrat-linje-blir-kolumner.md) | accepted |
| 0030 | [En etikett som fortsätter på nästa rad gör en tabell som delats i rader osäker](0030-en-ombruten-etikett-gor-tabellen-osaker.md) | accepted |
| 0031 | [Ett rutnät utan text är ingen tabell](0031-ett-rutnat-utan-text-ar-ingen-tabell.md) | accepted |
| 0032 | [Kalendern läses ur organens beslut av AI-agenten, skrivs i en CSV per kommun och visas med ett litet skript](0032-kalendern-las-ur-besluten-och-skrivs-for-hand.md) | accepted |
| 0033 | [Talrader i linje som inte blev någon tabell märker sidan osäker](0033-talrader-i-linje-marker-sidan-osaker.md) | accepted |
| 0034 | [En tabell med linjer som bara ramar in en del av sig själv fälls](0034-en-avskuren-tabell-med-linjer-falls.md) | accepted |
| 0035 | [Avsnittsrubriker och årtal håller ihop en tabell utan lodräta linjer](0035-avsnittsrubriker-och-artal-i-tabeller-utan-linjer.md) | accepted |
| 0036 | [Ett mellanslag som börjar inne i en siffra tas bort innan texten läses](0036-mellanslag-inne-i-en-siffra-tas-bort.md) | accepted |
| 0037 | [Rubrikrader, radavstånd och sidfot i tabeller utan lodräta linjer](0037-rubrikrader-och-sidfot-i-tabeller-utan-linjer.md) | accepted |
| 0038 | [Text som inte går att läsa i ordning ger obekräftade tal](0038-text-i-oordning-ger-obekraftade-tal.md) | accepted |
| 0039 | [Episerver-generationerna läses ur arkivet med organens mappar och mönster för sökvägen, och ett sammanträde får inte samma typ från två plattformar](0039-episerver-ur-arkivet-med-mappar-och-monster.md) | accepted |
| 0040 | [Rubriker över flera kolumner och på flera textrader i tabeller utan lodräta linjer](0040-rubriker-over-flera-kolumner-och-textrader.md) | proposed |
| 0041 | [Varje avvikelse i källan blir ett eget issue efter en mall](0041-avvikelser-ett-issue-per-avvikelse.md) | proposed |
| 0044 | [Nämndens mål och direktiv läses ur dokumenten av AI-agenten, skrivs i en CSV per kommun med sidan som källa, och bygget prövar att texten står där](0044-namndens-mal-och-direktiv-las-ur-dokumenten-och-skrivs-for-hand.md) | accepted (0045 grupperar omdöpta mål, låter protokollet gå före och visar status som ikoner; 0050 ersätter sidans upplägg och skript) |
| 0045 | [Omdöpta mål grupperas i målfilen med tolkade kopplingar märkta, protokollet går före handlingarna, status blir ikoner, och sidan räknar antal per år](0045-omdopta-mal-grupperas-protokollet-gar-fore-och-status-blir-ikoner.md) | accepted |
| 0046 | [Nämndens uppföljningar och dragningar om målen läses ur protokollen av AI-agenten, skrivs i en CSV per kommun och räknas per år på målsidan](0046-uppfoljningar-i-namnden-las-ur-protokollen-och-skrivs-for-hand.md) | accepted |
| 0047 | [Alla organ läses ur arkivets Sitevision-kopior, utan att vänta på att konverteringen blir färdig](0047-alla-organ-lases-ur-arkivet.md) | accepted |
| 0050 | [Målsidan visas som en tidslinje över alla mål och ett kort per mål, med sammandraget överst](0050-malsidan-visas-som-tidslinje-och-malkort.md) | accepted (0051 ger tidslinjen en rad per rubrik) |
| 0051 | [Tidslinjen visar varje rubrik på en egen rad och markerar nya formuleringar](0051-tidslinjen-visar-varje-rubrik-och-nya-formuleringar.md) | accepted |
