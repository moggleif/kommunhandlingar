"""Krav: K36–K38, K42–K44 i docs/02-KRAV.md. Test: tests/test_lokalbehov.py
och de andra testerna för spår över tid.

Formerna som slagen av spår ritar sina faser med (`sparslag.py`,
`granskningsslag.py`). Faserna skiljs åt med form, inte bara färg.
"""

DRAG = 'fill="none" stroke="currentColor" stroke-width="1.5"'
CIRKEL = f'<circle cx="8" cy="8" r="6" {DRAG}/>'
FYLLD = '<circle cx="8" cy="8" r="7" fill="currentColor"/>'
RUTER = f'<path d="M8 1.5l6.5 6.5-6.5 6.5-6.5-6.5z" {DRAG}/>'
BOCK = '<path d="M4.5 8.5l2.5 2.5 4.5-5" fill="none" stroke="#fff" stroke-width="2"/>'
KRYSS = '<path d="M5 5l6 6M11 5l-6 6" fill="none" stroke="#fff" stroke-width="2"/>'
RUTA = '<rect x="1.5" y="1.5" width="13" height="13" rx="3" fill="currentColor"/>'
KLART = RUTA + BOCK
BUBBLA = f'<path d="M2 2.5h12v8H7.5L4 14v-3.5H2z" {DRAG}/>'
TIMGLAS = f'<path d="M3 2h10L3 14h10z" {DRAG}/>'
KVADRAT = f'<rect x="2" y="2" width="12" height="12" {DRAG}/>'
PELARE = f'<path d="M2 6.5l6-4.5 6 4.5zM3.5 8v5M8 8v5M12.5 8v5M2 14h12" {DRAG}/>'
