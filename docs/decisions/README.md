# Beslut (ADR)

Beslut skrivs enligt **[MADR 4](https://adr.github.io/madr/)** (Markdown
Any Decision Records). Rubrikerna följer MADR på engelska så att formatet
känns igen; innehållet skrivs på svenska. Mall:
[adr-template.md](adr-template.md). Filnamn `NNNN-rubrik-med-bindestreck.md`.

Regler för det här repot, utöver MADR:

- Ett beslut som är svårt att ändra kommer **med en ny ADR i samma pull
  request**.
- **Diskussionen hör hemma i ADR:en**, under *More Information*: hur
  resonemanget gick, invändningar och svar, och vad som avgjorde.
- `decision-makers` är människor och skrivs med roll, aldrig namn
  ([AGENTS.md](../../AGENTS.md), "Inga personnamn"), till exempel
  `projektägaren`. En AI-agent som gett en rekommendation står som
  `AI-agenten` under `consulted`. I texten räcker "ägaren" och "agenten"
  när det inte går att förväxla.
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
| 0004 | [Inkrementell körning: poolen är tillståndet och adressen är signalen](0004-inkrementell-korning-poolen-ar-tillstandet.md) | accepted |
| 0005 | [Konvertering: pdfplumber och Tesseract, tal bara från textlagret, och kvalitet som den sämsta sidan avgör](0005-konvertering-verktyg-ocr-och-kvalitet.md) | accepted |
| 0006 | [Körningen sker varje natt i GitHub Actions och checkar in data direkt till `main` efter datakontrollerna](0006-schemalagd-korning-i-actions-och-data-direkt-till-main.md) | accepted |
| 0007 | [Poolen är en ögonblicksbild: det som en gång checkats in tas inte bort, och historiken skrivs inte om](0007-poolen-ar-en-ogonblicksbild.md) | accepted |
| 0008 | [Kommunkonfigurationen skrivs i TOML, en fil per kommun, och artigheten per värd står i en gemensam fil](0008-kommunkonfigurationen-i-toml.md) | accepted |
| 0009 | [Tabellernas härkomst är dokumentets, sidnumret står i filnamnet, och CSV skrivs i ett fast format](0009-tabellernas-harkomst-och-csv-format.md) | accepted |
| 0010 | [Kandidaterna hämtas organ för organ i konfigurationens ordning, och inom organet protokoll före handlingar](0010-ordningen-organ-for-organ.md) | accepted |
| 0011 | [Sitevision-adaptern tar organet från sidan, datumet ur filnamnet eller rubriken, och avvikande datum rättas i kommunfilen](0011-sitevision-organ-fran-sidan-datum-och-rattelser.md) | accepted |
| 0012 | [Webbplatsen byggs ur poolen i GitHub Actions och publiceras på GitHub Pages utan att checkas in](0012-webbplatsen-byggs-i-actions-och-publiceras-pa-pages.md) | accepted |
