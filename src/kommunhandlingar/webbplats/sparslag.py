"""Krav: K36, K37, K38, K42 och K44 i docs/02-KRAV.md, ADR-0057,
ADR-0058, ADR-0059, ADR-0065 och ADR-0067. Test: tests/test_lokalbehov.py,
tests/test_initiativ.py, tests/test_handlingsplaner.py,
tests/test_redovisningar.py, tests/test_detaljplaner.py.

Slagen av spår över tid: vad som skiljer lokalbehoven, initiativärendena,
handlingsplanerna, redovisningarna och detaljplanerna åt, och listan
över alla slag. Filen är längre än målet för att varje slag är data i
ett stycke. Granskningarna står i `granskningsslag.py` för att filen
annars går över den hårda gränsen. Allt annat är gemensamt (`spar.py`,
`sparsida.py`, `sparformer.py`).
"""

from kommunhandlingar.webbplats.granskningsslag import GRANSKNINGAR
from kommunhandlingar.webbplats.spar import Slag
from kommunhandlingar.webbplats.sparformer import (
    BOCK,
    BUBBLA,
    CIRKEL,
    DRAG,
    FYLLD,
    KLART,
    KRYSS,
    RUTER,
    TIMGLAS,
)

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
        "beredning": (TIMGLAS, "beredning"),
        "bifall": (FYLLD + BOCK, "bifall"),
        "avslag": (FYLLD + KRYSS, "avslag"),
        "besvarat": (BUBBLA, "besvarat"),
        "uppfoljning": (RUTER, "uppföljning"),
        "genomfort": (KLART, "genomfört"),
    },
    inledning=(
        "<p>Initiativärenden och motioner år för år: vem som väckte dem, hur "
        "de bereddes, vad som beslutades, hur besluten följdes upp och om "
        "förslaget blev genomfört. Varje ikon länkar till sidan i dokumentet "
        "som visar steget.</p>"
    ),
    metod=(
        "<p>Stegen är lästa ur poolens dokument, från vilket organ som helst. "
        "Avsändaren står som källan skriver den: ett parti, flera partier, "
        "Alliansen, eller partilös där källan skriver (-). Varje steg har en "
        "text som står på källans sida, och bygget prövar det.</p>"
        "<p>Ett ärende har ett namn på sidan även när källorna kallar det "
        "olika. Där källan inte själv säger att det gäller ärendet är "
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
        "yttrande": (BUBBLA, "yttrande"),
        "plan": (
            f'<path d="M3.5 1.5h6l3 3v10h-9z" {DRAG}/>'
            '<path d="M5.5 7.5h5M5.5 10h5" stroke="currentColor"/>',
            "själva planen",
        ),
        "antagen": (FYLLD + BOCK, "antagen eller framtagen"),
        "uppfoljning": (RUTER, "uppföljning"),
        "revidering": (TIMGLAS, "revidering"),
    },
    inledning=(
        "<p>Handlingsplaner, program och policyer år för år: vem som "
        "föreslog dem, när de antogs och hur de följdes upp och reviderades. "
        "Varje ikon länkar till sidan i dokumentet som visar steget, och "
        "finns själva planen i poolen länkar kortet till den.</p>"
    ),
    metod=(
        "<p>En plan står med när den har ett eget steg i nämndens eller "
        "fullmäktiges protokoll eller handlingar: ett uppdrag, ett beslut, ett "
        "yttrande, en återrapport eller en uppföljning. Organets egna planer "
        "står med, och kommunens planer där organet har ett eget steg. "
        "Planer som bara nämns, den interna kontrollplanen och planer för "
        "enskilda elever står inte med. Avsändaren står när planen kommer "
        "ur en motion eller ett initiativ, som källan skriver den. Varje steg "
        "har en text som står på källans sida, och bygget prövar det.</p>"
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

REDOVISNINGAR = Slag(
    id="redovisningar",
    kolumn="redovisning",
    rubrik="Redovisningar",
    sak="Redovisning",
    saker="Redovisningarna",
    antal="redovisningar",
    faser={
        "direktiv": (CIRKEL, "beställd som direktiv eller uppdrag"),
        "redovisad": (FYLLD, "redovisad"),
        "aterkommande": (RUTER, "återkommande redovisning"),
    },
    inledning=(
        "<p>Det som redovisas för nämnden eller fullmäktige år för år: "
        "redovisningar som beställts som direktiv eller uppdrag, och när de "
        "kom tillbaka, och redovisningar som återkommer enligt lag eller "
        "årshjulet. Varje ikon länkar till sidan i dokumentet "
        "som visar steget.</p>"
    ),
    metod=(
        "<p>Ett direktiv i budgeten står här i stället för bland målen när "
        "rubriken börjar med Redovisning, Utredning eller Information, och "
        "ett uppdrag från fullmäktige står här när det redovisas tillbaka. "
        "Redovisningen är paragrafen i nämndens eller fullmäktiges protokoll. "
        "Uppföljningar av målen står på sidan om mål och direktiv, och "
        "förvaltningens stående information står inte med. Varje steg har "
        "en text som står på källans sida, och bygget prövar det.</p>"
        "<p>Där källan inte själv säger att paragrafen svarar på direktivet "
        "är kopplingen en bedömning och ikonen har en streckad ram. Ett år "
        "utan ikon betyder att inget steg står i poolen det året, inte att "
        "inget hände; poolen saknar en del protokoll. Sidan visar vad som "
        "står var och värderar inte redovisningarna.</p>"
    ),
    adr="0065-redovisningarna-foljs-som-handlingsplanerna.md",
)

DETALJPLANER = Slag(
    id="detaljplaner",
    kolumn="detaljplan",
    rubrik="Detaljplaner",
    sak="Plan",
    saker="Planerna",
    antal="planer",
    faser={
        "planbesked": (CIRKEL, "planbesked"),
        "uppdrag": (f'<path d="M4 2.5v11l9-5.5z" {DRAG}/>', "planuppdrag"),
        "samrad": (BUBBLA, "samråd"),
        "granskning": (RUTER, "granskning"),
        "godkannande": (FYLLD, "godkänd för fullmäktige"),
        "antagande": (FYLLD + BOCK, "antagen"),
        "overklagande": (TIMGLAS, "överklagad"),
        "avslutad": (FYLLD + KRYSS, "planuppdraget avslutat"),
    },
    inledning=(
        "<p>Detaljplanerna som nämnden arbetar med år för år: planbeskedet, "
        "uppdraget att ta fram planen, samrådet, granskningen, godkännandet, "
        "antagandet och "
        "ett överklagande eller ett avslutat planuppdrag. Varje ikon länkar "
        "till sidan i dokumentet som visar steget.</p>"
    ),
    metod=(
        "<p>Ett steg är ett beslut i nämndens, arbetsutskottets, "
        "kommunstyrelsens eller fullmäktiges protokoll; från "
        "kommunstyrelsen planbeskedet och projektbeställningen. Beredningen av "
        "nämndens ärenden, informationen och avstämningarna står inte med, "
        "och ett planbesked bara när det blev en plan på sidan. Varje steg "
        "har en text som står på källans sida, och bygget prövar det.</p>"
        "<p>En plan har ett namn på sidan, med fastighetsbeteckningen, även "
        "när källorna kallar den olika. Där källan inte själv säger att det "
        "gäller planen är kopplingen en bedömning och ikonen har en streckad "
        "ram. Ett år utan ikon betyder att inget "
        "steg står i poolen det året, inte att inget hände; poolen saknar en "
        "del protokoll. Sidan visar vad som står var och värderar inte "
        "planerna.</p>"
    ),
    adr="0067-detaljplanerna-foljs-som-redovisningarna.md",
)

SLAGEN = (
    LOKALBEHOV,
    INITIATIV,
    HANDLINGSPLANER,
    REDOVISNINGAR,
    DETALJPLANER,
    GRANSKNINGAR,
)
