# Bidra

## Förutsättningar

- Python 3.12 eller senare
- git
- Tesseract med svensk modell, för OCR och testerna
  (`apt-get install tesseract-ocr tesseract-ocr-swe`)

## Uppsättning från en tom maskin

```sh
git clone https://github.com/moggleif/kommunhandlingar.git
cd kommunhandlingar
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[utveckling]"
```

`pip install -e .` gör paketet i `src/kommunhandlingar/` importerbart, så
att testerna når det, och drar in markdown-it-py, som webbplatsen och
testerna renderar Markdown med. `[utveckling]` tar med ruff och
pip-audit, i de versioner som
står i `pyproject.toml`, samma som CI installerar; ruffs förhandsregler
kan ändras mellan versioner. Med
[uv](https://docs.astral.sh/uv/) går samma ruff att köra utan
installation: `uvx ruff@<versionen i pyproject.toml> check .`.

## Allt grönt före incheckning

Samma kontroller körs i CI (`.github/workflows/kontroll.yml`):

```sh
ruff check .
ruff format --check .
python3 scripts/kontrollera_storlek.py
python3 -m unittest discover -s tests -t .
npx markdownlint-cli2@<versionen i kontroll.yml> <ändrade .md-filer>
pip-audit .
```

Gränserna för storlek och komplexitet står i "Ren kod – strikt" i
`AGENTS.md`. Ruff kontrollerar parametrar, nästling och komplexitet
(`pyproject.toml`); `scripts/kontrollera_storlek.py` kontrollerar rader per
funktion och fil, som ruff saknar regler för. Markdown-lint (ADR-0021)
körs med [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2)
och Node på de `.md` som ändrats, med reglerna i
`.markdownlint-cli2.jsonc`; hela poolen tar en halvtimme. `pip-audit`
letar efter kända sårbarheter i projektets beroenden, och Dependabot
(`.github/dependabot.yml`) föreslår nya versioner av beroendena, av ruff
och pip-audit och av Actions. CI
kontrollerar också att inga binärer är incheckade.

## Webbplatsen

Webbplatsen byggs lokalt, från repots rot, till en katalog som öppnas i
webbläsaren (K14, K18, ADR-0012, ADR-0023). Med hela poolen tar det ett
par minuter:

```sh
python3 -m kommunhandlingar.webbplats _site https://github.com/moggleif/kommunhandlingar
```

`_site/` checkas inte in; `.github/workflows/webbplats.yml` bygger och
publicerar på GitHub Pages vid varje push till `main`.

## Upptäckten

Kandidatlistan för en kommun skrivs till en katalog utanför repot (steg 1,
ADR-0013). Kommunens källsidor hämtas artigt, så det tar några minuter:

```sh
python3 -m kommunhandlingar.upptack kommuner/kungsbacka.toml /tmp/kommunhandlingar
```

Arkivets lista (K16, ADR-0018) tas fram med `--arkiv` och hämtas med
samma flagga till steg 2. `web.archive.org` svarar inte alltid och nås inte
från alla miljöer; från GitHub Actions gör den det:

```sh
python3 -m kommunhandlingar.upptack kommuner/kungsbacka.toml /tmp/kommunhandlingar --arkiv
```

## Hämtning och konvertering

Steg 2 läser kandidatlistan från samma arbetskatalog och skriver i `data/`
(ADR-0014). Varje fil hämtas med intervallet i `hamtning.toml` emellan, så
en hel kommun tar timmar:

```sh
python3 -m kommunhandlingar.hamta kommuner/kungsbacka.toml /tmp/kommunhandlingar
```

PDF-fixturerna i `tests/fixtures/pdf/` skapas av `skapa.py`, som behöver
reportlab, pypdf och Pillow, och `skapa_skarvar.py`, som behöver
reportlab. De är inte projektets beroenden.

## Facit för konverteringen

Ett urval sidor ur riktiga handlingar konverteras och jämförs med ett
facit (K20). Kör det före och efter en ändring av konverteringen:

```sh
python3 -m kommunhandlingar.facit            # måtten och en not per avvikelse
python3 -m kommunhandlingar.facit --spara    # och raden i matt.csv
```

Ändrar en ändring måtten skrivs raden om med `--spara` i samma ändring.
Hur måtten räknas och hur ett nytt dokument läggs till i urvalet står under
"Facit för konverteringen" i [03-ARKITEKTUR.md](03-ARKITEKTUR.md).

## Figurerna

Sidor med figurer tolkas för hand av en Claude-session, i omgångar, enligt
`.claude/skills/tolka-figurer/SKILL.md` (K15, ADR-0017). Kommandona och
formatet står under "Tolkade figurer" i [03-ARKITEKTUR.md](03-ARKITEKTUR.md).

## Undantag

- Rader per funktion: `# undantag: <skäl>` på `def`-raden. En fil har
  inget undantag; blir den för lång delas den.
- Ruffs gränser: `# noqa: <regel>  # undantag: <skäl>` på raden ruff pekar ut.

## Avvikelser i källan

Den som hittar en avvikelse i hur kommunen publicerat en handling, en
människa eller AI-agenten, skapar ett eget issue med mallen "Avvikelse i
källan" ([ADR-0041](decisions/0041-avvikelser-ett-issue-per-avvikelse.md)).
Mallen sätter etiketten `avvikelse`; statusen har inga egna etiketter
utan står på en rad i issuets text. Varje nytt steg läggs till på raden
med datum (ÅÅÅÅ-MM-DD), så att de tidigare står kvar:

1. `att undersöka`, när issuet skapas.
2. `undersökt – inget fel`, och issuet stängs, eller `undersökt – fel
   hos kommunen`.
3. `e-post skickad`, när en människa har mejlat kommunen med beläggen ur
   issuet.
4. `rättat i källan`, och issuet stängs, eller `rättas inte`, med skälet,
   när kommunen inte rättar eller handlingen bara finns i ett arkiv, och
   issuet stängs.

Belägg anges med sökväg i poolen och sidnummer, inte med citat: inga
personnamn och inga personuppgifter i issuet. Personuppgifter i en
handling blir aldrig ett issue
([ADR-0022](decisions/0022-personuppgifter-maskas-vid-konverteringen.md)).
Dokumentet i poolen rättas inte efter avvikelsen. De öppna avvikelserna
står, grupperade efter status, på webbplatsens sida
[Avvikelser](https://moggleif.github.io/kommunhandlingar/avvikelser.html)
(K33).

## Datakontrollerna

CI och den schemalagda körningen prövar allt under `data/` (K11):

```sh
python3 -m kommunhandlingar.datakontroll data
```

Vilka kontrollerna är, och vilken som bara körs i den schemalagda
körningen innan den checkar in, står under "Körning och incheckning" i
[03-ARKITEKTUR.md](03-ARKITEKTUR.md) (ADR-0006, ADR-0015).

## Den schemalagda körningen

`.github/workflows/nattkorning.yml` går varje natt och kan startas för
hand under Actions. Den pushar en gren `nattkorning/<datum>-<id>` när
något ändrats, öppnar en PR från den och slår på automatisk merge, så att
GitHub mergar när "Ren kod och tester" gått igenom (ADR-0052). Det kräver
två saker i repot, som en ägare ordnar en gång:

1. En finkornig token (Settings → Developer settings → Fine-grained
   tokens) för bara det här repot, med *Contents* och *Pull requests*
   som läs och skriv. Den läggs som hemligheten `NATTKORNING_TOKEN`
   under Settings → Secrets and variables → Actions.
2. *Allow auto-merge* påslaget under Settings → General.

Faller jobbet "PR med automatisk merge" har token gått ut, saknar
behörighet, eller är automatisk merge avslagen; rätta det i
inställningarna. Grenen är pushad ändå, och står PR:en redan öppen kan
den mergas för hand.

Utan hemligheten öppnar en människa eller agent PR:en från grenen
(ADR-0015). En PR vars kontroll fallit står kvar omergad tills någon
rättar felet. Ligger flera grenar omergade, merga den nyaste och ta bort
de äldre, vilket också stänger deras PR:er; det de hade utöver den hämtas
igen nästa natt.
En gren som skrivits av en version före 0.5.0 maskas först med
`python3 -m kommunhandlingar.maska_poolen data`; annars faller
datakontrollen på dess personuppgifter (ADR-0022).
