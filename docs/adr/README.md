# Arkitekturbeslut (ADR)

Varje betydelsefullt beslut som är svårt att ändra får en numrerad ADR:
sammanhanget beslutet fattades i, alternativen som vägdes, diskussionen som
ledde fram till valet, beslutet och konsekvenserna vi accepterade. Poängen är
att den som kommer efter (människa eller AI) ser *varför* saker är som de är
utan att behöva ta om diskussionen.

Regler:

- En arkitekturändring kommer **med en ny ADR i samma pull request**.
- ADR:er är historik: en accepterad ADR skrivs inte om. Ändras beslutet,
  skriv en ny ADR som ersätter den gamla och länka åt båda hållen.
- **Diskussionen hör hemma i ADR:en.** Hur resonemanget gick, vem som sa
  vad och vad som avgjorde – inte bara slutsatsen.
- En rekommendation från en AI-agent märks som sådan. Beslutet fattas av en
  människa.

Mall: [0000-mall.md](0000-mall.md). Filnamn `NNNN-kort-rubrik.md`.

## Index

| #    | Beslut                                                                     | Status     |
| ---- | -------------------------------------------------------------------------- | ---------- |
| 0001 | [Ett repo, bara text: PDF:en raderas efter konvertering](0001-var-datapoolen-ska-bo.md) | Accepterad |
