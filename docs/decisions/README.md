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
- `decision-makers` är människor. En rekommendation från en AI-agent märks
  med vem som gav den, och agenten står under `consulted`.
- En accepterad ADR skrivs inte om. Ändras beslutet skrivs en ny ADR, och
  den gamla får `status: "superseded by ADR-NNNN"`.

## Index

| #    | Beslut                                                                        | Status   |
| ---- | ----------------------------------------------------------------------------- | -------- |
| 0001 | [Ett repo med bara text – PDF:en raderas efter konvertering](0001-ett-repo-bara-text.md) | accepted |
| 0002 | [Kort AGENTS.md, faserna som skills och en egen granskningsagent](0002-kort-agentfil-faser-som-skills-och-egen-granskare.md) | accepted |
| 0003 | [Dokumentet identifieras av sin plats i modellen och en källnyckel; sha256 är versionen](0003-dokumentets-identitet-och-datamodell.md) | accepted |
| 0004 | [Inkrementell körning: poolen är tillståndet och adressen är signalen](0004-inkrementell-korning-poolen-ar-tillstandet.md) | accepted |
| 0005 | [Konvertering: verktyg, OCR och kvalitet som den sämsta sidan avgör](0005-konvertering-verktyg-ocr-och-kvalitet.md) | proposed |
