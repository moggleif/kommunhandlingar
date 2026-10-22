"""Krav: K36, K37 och K38 i docs/02-KRAV.md, ADR-0057, ADR-0058 och ADR-0059.
Test: tests/test_lokalbehov.py, tests/test_initiativ.py,
tests/test_handlingsplaner.py.

Slagen av spår över tid: vad som skiljer lokalbehoven, initiativärendena
och handlingsplanerna åt. Allt annat är gemensamt (`spar.py`, `sparsida.py`).
"""

from kommunhandlingar.webbplats.spar import Slag

DRAG = 'fill="none" stroke="currentColor" stroke-width="1.5"'
CIRKEL = f'<circle cx="8" cy="8" r="6" {DRAG}/>'
FYLLD = '<circle cx="8" cy="8" r="7" fill="currentColor"/>'
RUTER = f'<path d="M8 1.5l6.5 6.5-6.5 6.5-6.5-6.5z" {DRAG}/>'
BOCK = '<path d="M4.5 8.5l2.5 2.5 4.5-5" fill="none" stroke="#fff" stroke-width="2"/>'
KRYSS = '<path d="M5 5l6 6M11 5l-6 6" fill="none" stroke="#fff" stroke-width="2"/>'
RUTA = '<rect x="1.5" y="1.5" width="13" height="13" rx="3" fill="currentColor"/>'
KLART = RUTA + BOCK

LOKALBEHOV = Slag(
    id="lokalbehov",
    kolumn="behov",
    rubrik="Lokalbehov",
    sak="Behov",
    saker="Behoven",
    antal="behov",
    faser={
        "lokalbehov": (CIRKEL, "i nämndens lokalbehov"),
        "prioritet": (FYLLD, "prioriterat"),
        "lokalplan": (
            f'<rect x="2" y="2" width="12" height="12" {DRAG}/>',
            "i lokalplanen",
        ),
        "startbeslut": (
            '<path d="M4 2.5v11l9-5.5z" fill="currentColor"/>',
            "startbeslut",
        ),
        "pagar": (
            RUTER + '<path d="M8 1.5v13l-6.5-6.5z" fill="currentColor"/>',
            "på gång",
        ),
        "utfort": (KLART, "utfört"),
    },
    inledning=(
        "<p>Nämndens lokalbehov år för år: när de står i nämndens lokalbehov, "
        "hur de prioriteras, om de kommer in i kommunens lokalplan, får "
        "startbeslut och blir utförda. Varje ikon länkar till sidan i dokumentet "
        "som visar steget.</p>"
    ),
    metod=(
        "<p>Stegen är lästa ur poolens dokument, från vilket organ som helst: "
        "nämndens egna, budgeten, besluten om att starta projekt och "
        "redovisningen från det organ som bygger. Varje steg har en text som "
        "står på källans sida, och bygget prövar det.</p>"
        "<p>Ett behov har ett namn på sidan även när källorna kallar det olika. "
        "Där källan inte själv säger att det gäller behovet är kopplingen en "
        "bedömning och ikonen har en streckad ram. Ett år utan ikon betyder att "
        "inget steg står i poolen det året, inte att inget hände. Sidan visar "
        "vad som står var och värderar inte behoven.</p>"
    ),
    adr="0057-lokalbehoven-foljs-steg-for-steg-ur-alla-organs-dokument.md",
    varden={
        "prioritet": (r".+", "en prioritet"),
        "lokalplan": (r"\d+", "ett löpnummer"),
    },
    siffra="prioritet",
    aktuell="lokalbehov",
)

INITIATIV = Slag(
    id="initiativ",
    kolumn="arende",
    rubrik="Initiativärenden",
    sak="Ärende",
    saker="Ärendena",
    antal="ärenden",
    faser={
        "vackt": (CIRKEL, "väckt"),
        "beredning": (f'<path d="M3 2h10L3 14h10z" {DRAG}/>', "beredning"),
        "bifall": (FYLLD + BOCK, "bifall"),
        "avslag": (FYLLD + KRYSS, "avslag"),
        "besvarat": (f'<path d="M2 2.5h12v8H7.5L4 14v-3.5H2z" {DRAG}/>', "besvarat"),
        "uppfoljning": (RUTER, "uppföljning"),
        "genomfort": (KLART, "genomfört"),
    },
    inledning=(
        "<p>Nämndens initiativärenden år för år: vem som väckte dem, hur de "
        "bereddes, vad nämnden beslutade, hur besluten följdes upp och om "
        "förslaget blev genomfört. Varje ikon länkar till sidan i dokumentet "
        "som visar steget.</p>"
    ),
    metod=(
        "<p>Stegen är lästa ur poolens dokument, från vilket organ som helst. "
        "Avsändaren står som källan skriver den: ett parti, flera partier "
        "eller Alliansen. Varje steg har en text som står på källans sida, "
        "och bygget prövar det.</p>"
        "<p>Ett ärende har ett namn på sidan även när källorna kallar det "
        "olika. Där källan inte själv säger att det gäller initiativet är "
        "kopplingen en bedömning och ikonen har en streckad ram. Ett år utan "
        "ikon betyder att inget steg står i poolen det året, inte att inget "
        "hände; poolen saknar en del protokoll. Sidan visar vad som står var "
        "och värderar inte ärendena.</p>"
    ),
    adr="0058-initiativarenden-foljs-som-lokalbehoven.md",
    varden={"vackt": (r".+", "en avsändare")},
    avsandare="vackt",
)

HANDLINGSPLANER = Slag(
    id="handlingsplaner",
    kolumn="plan",
    rubrik="Handlingsplaner",
    sak="Plan",
    saker="Planerna",
    antal="planer",
    faser={
        "uppdrag": (CIRKEL, "förslag, uppdrag eller arbete"),
        "yttrande": (f'<path d="M2 2.5h12v8H7.5L4 14v-3.5H2z" {DRAG}/>', "yttrande"),
        "plan": (
            f'<path d="M3.5 1.5h6l3 3v10h-9z" {DRAG}/>'
            '<path d="M5.5 7.5h5M5.5 10h5" stroke="currentColor"/>',
            "själva planen",
        ),
        "antagen": (FYLLD + BOCK, "antagen eller framtagen"),
        "uppfoljning": (RUTER, "uppföljning"),
        "revidering": (f'<path d="M3 2h10L3 14h10z" {DRAG}/>', "revidering"),
        "avslutad": (KLART, "avslutad"),
    },
    inledning=(
        "<p>Nämndens handlingsplaner år för år: vem som föreslog dem, när de "
        "antogs, hur de följdes upp och reviderades och när de avslutades. "
        "Varje ikon länkar till sidan i dokumentet som visar steget, och "
        "finns själva planen i poolen länkar kortet till den.</p>"
    ),
    metod=(
        "<p>En plan står med när den har ett eget steg i nämndens protokoll "
        "eller handlingar: ett uppdrag, ett beslut, ett yttrande, en "
        "återrapport eller en uppföljning. Nämndens egna planer står med, och "
        "kommunens planer där nämnden har ett eget steg. Planer som bara nämns "
        "och den interna kontrollplanen står inte med. Avsändaren står när "
        "planen kommer ur en motion eller ett initiativ, som källan skriver "
        "den. Varje steg har en text som står på källans sida, och bygget "
        "prövar det.</p>"
        "<p>En plan har ett namn på sidan även när källorna kallar den olika. "
        "Där källan inte själv säger att det gäller planen är kopplingen en "
        "bedömning och ikonen har en streckad ram. Ett år utan ikon betyder "
        "att inget steg står i poolen det året, inte att inget hände; poolen "
        "saknar en del protokoll. Sidan visar vad som står var och värderar "
        "inte planerna.</p>"
    ),
    adr="0059-handlingsplanerna-foljs-som-initiativen.md",
    avsandare="uppdrag",
    planen="plan",
)

SLAGEN = (LOKALBEHOV, INITIATIV, HANDLINGSPLANER)
