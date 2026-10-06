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
