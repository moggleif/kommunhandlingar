---
status: proposed
date: 2026-10-09
decision-makers: projektägaren
consulted: AI-agenten
---

# Poolens text escapas vid konverteringen så att den är riktig Markdown, och CI kör Markdown-lint

## Context and Problem Statement

Texten under front matter
([ADR-0014](0014-markdown-texten-och-steg-2.md)) skrivs rad för rad som
den står i PDF:en. Den innehåller rader som en Markdown-läsare tolkar
som struktur: 2026-10-09 började omkring 26 000 rader med ett tal och en
punkt och blev numrerade listor, 12 000 började med `- ` och blev
punktlistor, 650 hade `<…>` som blev HTML eller försvann, och 560 rader
med bara `-` gjorde raden ovanför till rubrik. Filerna visas därför fel
på GitHub, och webbplatsen
([#55](https://github.com/moggleif/kommunhandlingar/issues/55)) kan inte
använda en vanlig Markdown-läsare
([#65](https://github.com/moggleif/kommunhandlingar/issues/65)).

Hur blir texten riktig Markdown, hur rättas de filer som redan finns,
och hur hålls den riktig?

## Decision Drivers

* **Texten visas som den stod.** En Markdown-läsare ska inte göra listor,
  rubriker, länkar eller HTML av text ur PDF:en.
* **Råfilen ska gå att läsa**, för människor och program (#56). Bara det
  som annars ändrar betydelse escapas.
* **Ett format, en ägare.** Konverteringen skriver texten; ingen mellanform
  i poolen.
* **Bara text lagras** (ADR-0001). Rättningen av befintliga filer får inte
  kräva att PDF:erna hämtas igen.
* **Omkonverteringen** ([ADR-0019](0019-omkonvertering-efter-poolens-version.md))
  ska fortfarande se vilka dokument som lästs av en äldre version.

## Considered Options

* A – Konverteringen escapar det som annars ändrar betydelse; de
  befintliga filerna rättas en gång med samma regel; CI kör Markdown-lint
* B – Konverteringen escapar varje tecken som kan ha betydelse i Markdown
* C – Ett eget steg efter hämtningen gör texten till Markdown
* D – Varje sida blir ett kodblock

## Decision Outcome

Valt: A, eftersom det ger riktig Markdown med minst ändring i råfilen och
en enda ägare av formatet. Den exakta regeln står i
[ARKITEKTUR](../03-ARKITEKTUR.md#markdown-texten) och i
`src/kommunhandlingar/konvertering/markdown.py`.

* **Läsaren** som texten ska vara riktig för är CommonMark med GFM:s
  tabeller och genomstrykning, och GitHubs formler med `$`.
* **Escapningen** görs per rad, i löptexten och i OCR-texten, och per
  cell i tabellerna. Raden skrivs utan indrag. Kodblocket
  `osaker-tabell` får ett staket som är längre än varje följd av
  backticks i blocket.
* **Radbrytningarna** är mjuka, som förut. Råfilen bär uppställningen;
  den som visar texten och vill behålla rader och mellanrum gör det med
  `white-space: pre-wrap`, som webbplatsen (#55).
* **Versionen** höjs till 0.4.0, eftersom konverteringen skriver något
  annat.
* **De befintliga filerna** rättas en gång, av ett skript i samma pull
  request, utan att PDF:erna hämtas. Sidkommentarerna och tabellänkarna
  står kvar, och pipe-tabellerna byggs om ur sina CSV:er. Skriptet stannar
  om en tabell inte stämmer med sin CSV eller om den renderade texten inte
  är den som stod. `pipeline` rörs inte, så omkonverteringen ser
  fortfarande vilka dokument som lästs av en äldre version. Escapningen tål
  inte att köras två gånger, så skriptet körs bara på filer som inte är
  rättade, och tas bort när poolen är rättad.
* **Markdown-lint** (markdownlint-cli2, MIT) körs i CI på varje
  `.md` som en pull request lägger till eller ändrar. Reglerna står i
  `.markdownlint-cli2.jsonc`; regler om stil och radlängd är avstängda,
  eftersom texten är PDF:ens rader.

### Consequences

* Bra, eftersom varje fil visas som den stod på GitHub, och webbplatsen
  kan använda en vanlig Markdown-läsare.
* Bra, eftersom lint fångar trasig Markdown i allt som når `main`,
  också text som skrivs för hand, som tolkade figurer (ADR-0017).
* Dåligt, eftersom råfilen får `\` på omkring 40 000 rader, mest `1\.`
  och `\-` i radens början.
* Dåligt, eftersom raderna i ett stycke flyter ihop när texten visas på
  GitHub; uppställningen syns bara i råfilen och där den som visar texten
  behåller den.
* Dåligt, eftersom ett dokument som rättats har escapad text men en
  äldre version i `pipeline`. Det står så tills dokumentet konverteras om.
* Neutralt, eftersom lint inte märker när en rad ur PDF:en råkar bli en
  lista: den ser en riktig lista. Det prövar testerna, som renderar
  escapad text och kräver att den visas som den stod.
* Neutralt, eftersom CI behöver Node för lint. Det finns redan på
  GitHubs maskiner, och lint körs med `npx` på en låst version.

### Confirmation

* `tests/test_markdown.py` renderar escapade rader, stycken och
  tabellceller med markdown-it-py och kräver att de visas som de stod,
  utan annan struktur än stycken, och att vanlig text inte ändras.
* CI kör markdownlint-cli2 på de `.md` en pull request ändrar.

## Pros and Cons of the Options

### A – Escapa det som ändrar betydelse, rätta en gång, lint i CI

* Bra, eftersom råfilen ändras så lite som möjligt.
* Bra, eftersom formatet har en ägare.
* Dåligt, eftersom regeln måste känna till varje sätt en rad kan bli
  struktur; testerna och lint är skyddet.

### B – Escapa varje tecken som kan ha betydelse

* Bra, eftersom regeln blir enkel och säker.
* Dåligt, eftersom varje punkt, parentes, bindestreck och understreck
  får `\`, och råfilen blir svår att läsa för människor och program.

### C – Ett eget steg efter hämtningen

* Bra, eftersom konverteringen inte rörs.
* Dåligt, eftersom formatet får två ägare, och poolen har en mellanform
  som inte är Markdown tills steget körts.

### D – Varje sida som ett kodblock

* Bra, eftersom ingenting behöver escapas och uppställningen syns.
* Dåligt, eftersom texten slutar vara text i Markdown: den går inte att
  söka i som löptext på webbplatsen, raderna bryts inte, och säkra
  tabeller och tolkningar kan inte stå i blocket.

## More Information

### Diskussionen som ledde fram till beslutet

1. **Issuet (projektägaren).** Texten ska vara riktig Markdown, rättningen
   görs i konverteringen, och de befintliga filerna rättas en gång utan
   att PDF:erna hämtas. Frågor om radbrytningar, mellanrummen i raden,
   versionen och ett beroende för att pröva resultatet.
2. **Agentens rekommendation.** Escapa bara det som ändrar betydelse.
   Behåll mjuka radbrytningar, så att råfilen förblir ren; den som visar
   texten behåller rader och mellanrum med `pre-wrap`. Höj versionen men
   låt engångsrättningen lämna `pipeline` orörd, så att omkonverteringen
   inte luras. markdown-it-py (MIT) som testberoende.
3. **Beslutet (projektägaren).** Ja, med två tillägg: konverteringen ska
   escapa direkt, så att nya dokument blir riktiga från början, och
   Markdown-lint ska köras.
4. **Lint (agenten).** pymarkdownlnt, som är Python, provades först men
   tog över tio minuter för poolens 3,3 miljoner rader.
   markdownlint-cli2 läser 220 000 rader på 18 sekunder. Lint körs därför
   bara på de filer en pull request ändrar, och med Node, som redan finns
   i CI. Lint hittade också en trasig länk i ARKITEKTUR och några fel i
   dokumentationen, som rättades i samma ändring.
5. **Omprövas** om webbplatsen eller #56 behöver hårda radbrytningar i
   råfilen.
