# Bidra

## Förutsättningar

- Python 3.12 eller senare
- git

## Uppsättning från en tom maskin

```sh
git clone https://github.com/moggleif/kommunhandlingar.git
cd kommunhandlingar
python3 -m venv .venv
. .venv/bin/activate
pip install -e . "ruff==0.16.10" "pip-audit==2.10.1"
```

`pip install -e .` gör paketet i `src/kommunhandlingar/` importerbart, så
att testerna når det. Versionerna av ruff och pip-audit är desamma som i
`.github/workflows/kontroll.yml`; ruffs förhandsregler kan ändras mellan
versioner. Med [uv](https://docs.astral.sh/uv/) går samma ruff att köra
utan installation: `uvx ruff@0.16.10 check .`.

## Allt grönt före incheckning

Samma kontroller körs i CI (`.github/workflows/kontroll.yml`):

```sh
ruff check .
ruff format --check .
python3 scripts/kontrollera_storlek.py
python3 -m unittest discover -s tests -t .
pip-audit .
```

Gränserna för storlek och komplexitet står i "Ren kod – strikt" i
`AGENTS.md`. Ruff kontrollerar parametrar, nästling och komplexitet
(`pyproject.toml`); `scripts/kontrollera_storlek.py` kontrollerar rader per
funktion och fil, som ruff saknar regler för. `pip-audit` letar efter kända
sårbarheter i projektets beroenden, och Dependabot
(`.github/dependabot.yml`) föreslår nya versioner av dem och av Actions. CI
kontrollerar också att inga binärer är incheckade.

## Undantag

- Rader per funktion eller fil: `# undantag: <skäl>` på `def`-raden, eller
  på första raden för en hel fil.
- Ruffs gränser: `# noqa: <regel>  # undantag: <skäl>` på raden ruff pekar ut.

Datakontrollerna, bland dem kontrollen av härkomst i dokumentens front
matter (ADR-0001), kommer med pipelinen, när det finns dokument att
kontrollera. Vilka de är, och vilken som bara körs i den schemalagda
körningen innan den checkar in, står under "Körning och incheckning" i
[03-ARKITEKTUR.md](03-ARKITEKTUR.md) (ADR-0006).
