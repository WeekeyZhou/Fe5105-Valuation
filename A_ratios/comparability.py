"""
FE5105 — Member A, step 4: comparability adjustments.
 (1) Special items: GAAP vs company-adjusted operating margin (robustness check; GAAP stays primary).
 (2) Fuel-neutral: TTM operating margin if fuel had cost the FY2025 average price per gallon.
Input : data/processed/financials.csv, data/raw/special_items_operating.csv
Output: A_ratios/output/comparability_adjustments.csv and .xlsx
Run   : python A_ratios/comparability.py
"""
import os, csv, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'output'); os.makedirs(OUT, exist_ok=True)
TICK = ['LUV', 'DAL', 'UAL', 'AAL', 'ALK']
F = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'processed', 'financials.csv'), encoding='utf-8')):
    if r['value'] != '': F[(r['ticker'], r['period'])][r['item']] = float(r['value'])
g = lambda t, p, i: F[(t, p)].get(i)

# ---- special items: amount added back to GAAP operating income (positive = charge) ----
SP = collections.defaultdict(dict); SRC = {}
for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'raw', 'special_items_operating.csv'), encoding='utf-8')):
    t, p = r['ticker'], r['period']; SRC[(t, p)] = r['source']
    if r['adjusted_operating_income_reported']:
        SP[t][p] = float(r['adjusted_operating_income_reported']) - g(t, p, 'operating_income')
    elif r['operating_special_items']:
        SP[t][p] = float(r['operating_special_items'])
for t in TICK:
    if all(k in SP[t] for k in ('FY2025', '9M2026', '9M2025')):
        SP[t]['TTM_2026Q3'] = SP[t]['FY2025'] + SP[t]['9M2026'] - SP[t]['9M2025']

rows = []
def add(t, p, item, v, unit, note=''):
    rows.append(dict(ticker=t, period=p, item=item, value=None if v is None else round(v, 4), unit=unit, note=note))

for t in TICK:
    for p in ('FY2024', 'FY2025', 'TTM_2026Q3'):
        oi, rev = g(t, p, 'operating_income'), g(t, p, 'revenue_airline')
        s = SP[t].get(p)
        add(t, p, 'operating_income_gaap', oi, 'USD mn')
        add(t, p, 'operating_special_items', s, 'USD mn', '' if s is not None else 'pending: Delta Q1/Q2 2026 earnings releases needed')
        add(t, p, 'operating_income_adjusted', None if s is None else oi + s, 'USD mn')
        add(t, p, 'operating_margin_gaap', oi / rev, '%')
        add(t, p, 'operating_margin_adjusted', None if s is None else (oi + s) / rev, '%')
    # ---- fuel-neutral TTM ----
    p0, p1 = 'FY2025', 'TTM_2026Q3'
    price0 = g(t, p0, 'fuel_expense') / g(t, p0, 'fuel_gallons')
    price1 = g(t, p1, 'fuel_expense') / g(t, p1, 'fuel_gallons')
    gal = g(t, p1, 'fuel_gallons'); impact = (price1 - price0) * gal
    oi, rev = g(t, p1, 'operating_income'), g(t, p1, 'revenue_airline')
    add(t, p1, 'fuel_price_FY2025', price0, 'USD/gal')
    add(t, p1, 'fuel_price_TTM', price1, 'USD/gal')
    add(t, p1, 'fuel_gallons_TTM', gal, 'million gallons')
    add(t, p1, 'fuel_price_impact', impact, 'USD mn', 'extra fuel cost vs FY2025 average price = (TTM price - FY2025 price) x TTM gallons')
    add(t, p1, 'operating_income_fuel_neutral', oi + impact, 'USD mn', 'GAAP; revenue held at actual (ignores fare increases that passed fuel through)')
    add(t, p1, 'operating_margin_fuel_neutral', (oi + impact) / rev, '%')
    add(t, p1, 'fuel_impact_pct_of_revenue', impact / rev, '%')
    s = SP[t].get(p1)
    add(t, p1, 'operating_margin_adjusted_fuel_neutral', None if s is None else (oi + s + impact) / rev, '%')

with open(os.path.join(OUT, 'comparability_adjustments.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# ---- Excel ----
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.comments import Comment
V = {(r['ticker'], r['period'], r['item']): r for r in rows}
hdr = PatternFill('solid', fgColor='1F3D6D'); luv = PatternFill('solid', fgColor='FFF4CC'); sec = PatternFill('solid', fgColor='DDE6F2')
wb = Workbook(); ws = wb.active; ws.title = 'Special items'
ws.append(['(1) Special items: GAAP vs company-adjusted operating margin']); ws['A1'].font = Font(bold=True, size=12)
ws.append(['GAAP is the primary measure in the report; adjusted figures use each company\'s own non-GAAP definition (not fully comparable). Positive special items = charges added back.'])
ws.append([])
for p in ('FY2024', 'FY2025', 'TTM_2026Q3'):
    ws.append([p] + TICK); r0 = ws.max_row
    for c in ws[r0]: c.font = Font(bold=True, color='FFFFFF'); c.fill = hdr
    for item, lab, fmt in [('operating_income_gaap', 'Operating income, GAAP (USD mn)', '#,##0'),
                           ('operating_special_items', 'Operating special items (USD mn)', '#,##0;(#,##0)'),
                           ('operating_income_adjusted', 'Operating income, adjusted (USD mn)', '#,##0'),
                           ('operating_margin_gaap', 'Operating margin, GAAP', '0.0%'),
                           ('operating_margin_adjusted', 'Operating margin, adjusted', '0.0%')]:
        ws.append([lab] + [V[(t, p, item)]['value'] for t in TICK])
        for i, t in enumerate(TICK):
            c = ws.cell(ws.max_row, 2 + i); c.number_format = fmt
            if t == 'LUV': c.fill = luv
            if c.value is None:
                c.value = 'pending'; c.alignment = Alignment(horizontal='center')
                c.comment = Comment('Needs Delta Q1 and Q2 2026 earnings releases (8-K Exhibit 99.1)', 'A')
    ws.append([])
ws.column_dimensions['A'].width = 40
for col in 'BCDEF': ws.column_dimensions[col].width = 12
w2 = wb.create_sheet('Fuel-neutral TTM')
w2.append(['(2) Fuel-neutral: TTM operating margin if fuel had cost the FY2025 average price']); w2['A1'].font = Font(bold=True, size=12)
w2.append(['Fuel price = fuel expense / gallons. Revenue held at actual, so this overstates the "pure fuel" effect for airlines that raised fares in response.'])
w2.append([])
w2.append(['Item'] + TICK)
for c in w2[4]: c.font = Font(bold=True, color='FFFFFF'); c.fill = hdr
for item, lab, fmt in [('fuel_price_FY2025', 'Fuel cost per gallon, FY2025 (USD)', '0.00'),
                       ('fuel_price_TTM', 'Fuel cost per gallon, TTM (USD)', '0.00'),
                       ('fuel_gallons_TTM', 'Gallons consumed, TTM (mn)', '#,##0'),
                       ('fuel_price_impact', 'Extra fuel cost from higher price (USD mn)', '#,##0'),
                       ('fuel_impact_pct_of_revenue', 'Extra fuel cost as % of revenue', '0.0%'),
                       ('operating_income_gaap', 'Operating income, GAAP (USD mn)', '#,##0'),
                       ('operating_income_fuel_neutral', 'Operating income, fuel-neutral (USD mn)', '#,##0'),
                       ('operating_margin_gaap', 'Operating margin, GAAP', '0.0%'),
                       ('operating_margin_fuel_neutral', 'Operating margin, fuel-neutral', '0.0%'),
                       ('operating_margin_adjusted_fuel_neutral', 'Operating margin, adjusted + fuel-neutral', '0.0%')]:
    w2.append([lab] + [V[(t, 'TTM_2026Q3', item)]['value'] for t in TICK])
    for i, t in enumerate(TICK):
        c = w2.cell(w2.max_row, 2 + i); c.number_format = fmt
        if t == 'LUV': c.fill = luv
        if c.value is None: c.value = 'pending'; c.alignment = Alignment(horizontal='center')
w2.column_dimensions['A'].width = 44
for col in 'BCDEF': w2.column_dimensions[col].width = 12
w3 = wb.create_sheet('Sources')
w3.append(['ticker', 'period', 'source']); [w3.append([t, p, s]) for (t, p), s in sorted(SRC.items())]
w3.column_dimensions['C'].width = 110
wb.save(os.path.join(OUT, 'comparability_adjustments.xlsx'))
print('rows', len(rows), 'pending', sum(r['value'] is None for r in rows))
