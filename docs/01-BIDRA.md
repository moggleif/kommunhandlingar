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
pip install -e ".[utveckling]"
```

`pip install -e .` gör paketet i `src/kommunhandlingar/` importerbart, så
att testerna når det. `[utveckling]` tar med ruff och pip-audit i de
versioner som står i `pyproject.toml`, samma som CI installerar; ruffs
förhandsregler kan ändras mellan versioner. Med
[uv](https://docs.astral.sh/uv/) går samma ruff att köra utan
installation: `uvx ruff@<versionen i pyproject.toml> check .`.

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
(`.github/dependabot.yml`) föreslår nya versioner av beroendena, av ruff
och pip-audit och av Actions. CI
kontrollerar också att inga binärer är incheckade.

## Webbplatsen

Webbplatsen byggs lokalt, från repots rot, till en katalog som öppnas i
webbläsaren (K14, ADR-0012):

```sh
python3 -m kommunhandlingar.webbplats _site https://github.com/moggleif/kommunhandlingar
```

`_site/` checkas inte in; `.github/workflows/webbplats.yml` bygger och
publicerar på GitHub Pages vid varje push till `main`.

## Upptäckten

Kandidatlistan för en kommun tas fram från repots rot (steg 1, ADR-0013).
Den hämtar kommunens källsidor artigt, så det tar några minuter:

```sh
python3 -m kommunhandlingar.upptack kommuner/kungsbacka.toml /tmp/kommunhandlingar
```

## Undantag

- Rader per funktion eller fil: `# undantag: <skäl>` på `def`-raden, eller
  på första raden för en hel fil.
- Ruffs gränser: `# noqa: <regel>  # undantag: <skäl>` på raden ruff pekar ut.

Datakontrollerna, bland dem kontrollen av härkomst i dokumentens front
matter (ADR-0001), kommer med pipelinen, när det finns dokument att
kontrollera. Vilka de är, och vilken som bara körs i den schemalagda
körningen innan den checkar in, står under "Körning och incheckning" i
[03-ARKITEKTUR.md](03-ARKITEKTUR.md) (ADR-0006).
