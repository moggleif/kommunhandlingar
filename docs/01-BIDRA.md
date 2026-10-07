# Bidra

## Förutsättningar

- Python 3.12 eller senare
- [ruff](https://docs.astral.sh/ruff/), samma version som i
  `.github/workflows/kontroll.yml` (förhandsregler kan ändras mellan versioner)

## Allt grönt före incheckning

Samma kontroller körs i CI (`.github/workflows/kontroll.yml`):

```sh
ruff check .
ruff format --check .
python3 scripts/kontrollera_storlek.py
python3 -m unittest discover -s tests -t .
```

Gränserna för storlek och komplexitet står i "Ren kod – strikt" i
`AGENTS.md`. Ruff kontrollerar parametrar, nästling och komplexitet
(`pyproject.toml`); `scripts/kontrollera_storlek.py` kontrollerar rader per
funktion och fil, som ruff saknar regler för. CI kontrollerar också att
inga binärer är incheckade.

## Undantag

- Rader per funktion eller fil: `# undantag: <skäl>` på `def`-raden, eller
  på första raden för en hel fil.
- Ruffs gränser: `# noqa: <regel>  # undantag: <skäl>` på raden ruff pekar ut.

Datakontrollerna, bland dem kontrollen av härkomst i dokumentens front
matter (ADR-0001), kommer med pipelinen, när det finns dokument att
kontrollera. Vilka de är, och vilka som bara körs i den schemalagda
körningen innan den checkar in, står under "Körning och incheckning" i
[03-ARKITEKTUR.md](03-ARKITEKTUR.md) (ADR-0006).
