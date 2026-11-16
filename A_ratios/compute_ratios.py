"""
FE5105 — Member A: financial ratio table for LUV and peers.
Input : data/processed/financials.csv, data/raw/revolver_undrawn_2026-09-30.csv
Output: A_ratios/output/ratios_table.csv (long) and ratios_table.xlsx (formatted)
Run   : python A_ratios/compute_ratios.py
"""
import os, csv, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'output'); os.makedirs(OUT, exist_ok=True)

TAX_RATE = 0.24   # PLACEHOLDER (21% federal + ~3% state). Replace with B's rate in shared/assumptions.md, then re-run.
TICK = ['LUV', 'DAL', 'UAL', 'AAL', 'ALK']
PERIODS = ['FY2024', 'FY2025', 'TTM_2026Q3']
BS_END = {'FY2024': 'BS_2024-12-31', 'FY2025': 'BS_2025-12-31', 'TTM_2026Q3': 'BS_2026-09-30'}
BS_BEGIN = {'FY2024': None, 'FY2025': 'BS_2024-12-31', 'TTM_2026Q3': 'BS_2025-12-31'}  # no 2023 balance sheet in dataset

F = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'processed', 'financials.csv'), encoding='utf-8')):
    if r['value'] != '': F[(r['ticker'], r['period'])][r['item']] = float(r['value'])
REV = {r['ticker']: float(r['undrawn_revolver_usd_mn']) for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'raw', 'revolver_undrawn_2026-09-30.csv'), encoding='utf-8'))}

def g(t, p, item):
    return F[(t, p)].get(item) if p else None
def avg(t, p, item):
    a, b = g(t, BS_BEGIN[p], item), g(t, BS_END[p], item)
    return None if a is None or b is None else (a + b) / 2
def div(a, b):
    return None if a is None or b in (None, 0) else a / b
def ic(t, bs):  # invested capital = equity + adjusted net debt
    e, n = g(t, bs, 'equity'), g(t, bs, 'adjusted_net_debt')
    return None if e is None or n is None else e + n

# (key, group, label, unit, formula text, function)
RATIOS = [
 ('operating_margin', 'Profitability', 'Operating margin', '%', 'operating_income / revenue_airline',
  lambda t, p: div(g(t, p, 'operating_income'), g(t, p, 'revenue_airline'))),
 ('ebitdar_margin', 'Profitability', 'EBITDAR margin', '%', 'ebitdar / revenue_airline',
  lambda t, p: div(g(t, p, 'ebitdar'), g(t, p, 'revenue_airline'))),
 ('net_margin', 'Profitability', 'Net margin', '%', 'net_income / revenue_airline',
  lambda t, p: div(g(t, p, 'net_income'), g(t, p, 'revenue_airline'))),
 ('roic', 'Profitability', 'ROIC (after-tax, lease-adjusted capital)', '%',
  f'operating_income x (1 - {TAX_RATE:.0%}) / average(equity + adjusted_net_debt)',
  lambda t, p: div(None if g(t, p, 'operating_income') is None else g(t, p, 'operating_income') * (1 - TAX_RATE),
                   None if BS_BEGIN[p] is None or ic(t, BS_BEGIN[p]) is None or ic(t, BS_END[p]) is None else (ic(t, BS_BEGIN[p]) + ic(t, BS_END[p])) / 2)),
 ('roa', 'Profitability', 'ROA', '%', 'net_income / average total_assets',
  lambda t, p: div(g(t, p, 'net_income'), avg(t, p, 'total_assets'))),
 ('trasm', 'Efficiency', 'TRASM (unit revenue)', 'cents', 'revenue_airline / asm x 100',
  lambda t, p: None if div(g(t, p, 'revenue_airline'), g(t, p, 'asm')) is None else 100 * div(g(t, p, 'revenue_airline'), g(t, p, 'asm'))),
 ('casm', 'Efficiency', 'CASM (unit cost)', 'cents', 'total_opex_airline / asm x 100',
  lambda t, p: None if div(g(t, p, 'total_opex_airline'), g(t, p, 'asm')) is None else 100 * div(g(t, p, 'total_opex_airline'), g(t, p, 'asm'))),
 ('casm_ex_fuel', 'Efficiency', 'CASM ex-fuel', 'cents', '(total_opex_airline - fuel_expense) / asm x 100',
  lambda t, p: None if None in (g(t, p, 'total_opex_airline'), g(t, p, 'fuel_expense'), g(t, p, 'asm')) else 100 * (g(t, p, 'total_opex_airline') - g(t, p, 'fuel_expense')) / g(t, p, 'asm')),
 ('load_factor', 'Efficiency', 'Load factor', '%', 'rpm / asm',
  lambda t, p: div(g(t, p, 'rpm'), g(t, p, 'asm'))),
 ('asset_turnover', 'Efficiency', 'Asset turnover', 'x', 'revenue_airline / average total_assets',
  lambda t, p: div(g(t, p, 'revenue_airline'), avg(t, p, 'total_assets'))),
 ('fuel_price', 'Efficiency', 'Fuel cost per gallon', 'USD', 'fuel_expense / fuel_gallons',
  lambda t, p: div(g(t, p, 'fuel_expense'), g(t, p, 'fuel_gallons'))),
 ('asm_per_gallon', 'Efficiency', 'Fuel efficiency (ASM per gallon)', 'ASM', 'asm / fuel_gallons',
  lambda t, p: div(g(t, p, 'asm'), g(t, p, 'fuel_gallons'))),
 ('net_debt_ebitdar', 'Leverage', 'Adjusted net debt / EBITDAR', 'x', 'adjusted_net_debt (period end) / ebitdar',
  lambda t, p: div(g(t, BS_END[p], 'adjusted_net_debt'), g(t, p, 'ebitdar'))),
 ('debt_ebitdar', 'Leverage', 'Adjusted debt / EBITDAR', 'x', 'adjusted_debt (period end) / ebitdar',
  lambda t, p: div(g(t, BS_END[p], 'adjusted_debt'), g(t, p, 'ebitdar'))),
 ('interest_cover', 'Leverage', 'Interest coverage (EBIT / net interest)', 'x', 'operating_income / interest_expense_net',
  lambda t, p: div(g(t, p, 'operating_income'), g(t, p, 'interest_expense_net'))),
 ('interest_cover_gross', 'Leverage', 'Interest coverage (EBIT / gross interest)', 'x', 'operating_income / interest_expense (gross); not available for DAL',
  lambda t, p: div(g(t, p, 'operating_income'), g(t, p, 'interest_expense'))),
 ('fixed_charge_cover', 'Leverage', 'Fixed-charge coverage (EBITDAR / (net interest + rent))', 'x', 'ebitdar / (interest_expense_net + aircraft_rent)',
  lambda t, p: div(g(t, p, 'ebitdar'), None if None in (g(t, p, 'interest_expense_net'), g(t, p, 'aircraft_rent')) else g(t, p, 'interest_expense_net') + g(t, p, 'aircraft_rent'))),
 ('market_leverage', 'Leverage', 'Market leverage D/(D+E)', '%', 'adjusted_debt / (adjusted_debt + market_cap); TTM column only',
  lambda t, p: div(g(t, 'BS_2026-09-30', 'adjusted_debt'), g(t, 'BS_2026-09-30', 'adjusted_debt') + g(t, 'VAL_2026-11-13', 'market_cap')) if p == 'TTM_2026Q3' else None),
 ('current_ratio', 'Liquidity', 'Current ratio', 'x', 'current_assets / current_liabilities (period end)',
  lambda t, p: div(g(t, BS_END[p], 'current_assets'), g(t, BS_END[p], 'current_liabilities'))),
 ('atl_share_cl', 'Liquidity', 'Air traffic liability / current liabilities', '%', 'air_traffic_liability_total / current_liabilities (includes noncurrent loyalty portion; indicative)',
  lambda t, p: div(g(t, BS_END[p], 'air_traffic_liability_total'), g(t, BS_END[p], 'current_liabilities'))),
 ('cash_to_revenue', 'Liquidity', 'Cash & ST investments / revenue', '%', 'cash_and_sti (period end) / revenue_airline',
  lambda t, p: div(g(t, BS_END[p], 'cash_and_sti'), g(t, p, 'revenue_airline'))),
 ('total_liquidity', 'Liquidity', 'Total liquidity (USD mn)', 'USD mn', 'cash_and_sti + undrawn revolver; TTM column only (2026-09-30)',
  lambda t, p: g(t, 'BS_2026-09-30', 'cash_and_sti') + REV[t] if p == 'TTM_2026Q3' else None),
 ('liquidity_to_revenue', 'Liquidity', 'Total liquidity / revenue', '%', 'total liquidity / TTM revenue_airline; TTM column only',
  lambda t, p: div(g(t, 'BS_2026-09-30', 'cash_and_sti') + REV[t], g(t, p, 'revenue_airline')) if p == 'TTM_2026Q3' else None),
 ('ev_ebitdar', 'Valuation inputs (for C)', 'EV / EBITDAR', 'x', 'enterprise_value (2026-11-13) / TTM ebitdar; TTM column only',
  lambda t, p: div(g(t, 'VAL_2026-11-13', 'enterprise_value'), g(t, p, 'ebitdar')) if p == 'TTM_2026Q3' else None),
 ('ev_ebitda', 'Valuation inputs (for C)', 'EV / EBITDA', 'x', 'enterprise_value / TTM ebitda; TTM column only',
  lambda t, p: div(g(t, 'VAL_2026-11-13', 'enterprise_value'), g(t, p, 'ebitda')) if p == 'TTM_2026Q3' else None),
]
NOTES = {
 ('ALK', 'FY2024'): 'Hawaiian consolidated only from 2024-09-18; not comparable with FY2025',
}
def flag(t, p, key, v):
    n = []
    if (t, p) in NOTES: n.append(NOTES[(t, p)])
    if key == 'roic' and p == 'FY2024': n.append('no 2023 balance sheet in dataset')
    if key in ('roa', 'asset_turnover') and p == 'FY2024': n.append('no 2023 balance sheet in dataset')
    if key in ('net_debt_ebitdar', 'debt_ebitdar') and v is not None and g(t, p, 'ebitdar') is not None and g(t, p, 'ebitdar') < 1000 and t == 'ALK' and p == 'TTM_2026Q3':
        n.append('EBITDAR depressed by 2026 fuel shock; multiple inflated')
    if key == 'interest_cover' and v is not None and v < 0 and (g(t, p, 'operating_income') or 0) < 0: n.append('negative operating income')
    if key == 'interest_cover_gross' and t == 'DAL': n.append('Delta reports only net interest expense')
    if key == 'roic' and p == 'TTM_2026Q3': n.append('average of 2025-12-31 and 2026-09-30 capital')
    return '; '.join(n)

rows = []
for key, grp, label, unit, formula, fn in RATIOS:
    for t in TICK:
        for p in PERIODS:
            try: v = fn(t, p)
            except (TypeError, KeyError): v = None
            nm = ''
            if key in ('interest_cover', 'fixed_charge_cover'):
                ni = g(t, p, 'interest_expense_net')
                den = None if ni is None else (ni if key == 'interest_cover' else ni + (g(t, p, 'aircraft_rent') or 0))
                if den is not None and den <= 0:
                    v = None; nm = 'n.m.: interest income exceeds interest expense (net interest is income)'
            rows.append(dict(ratio=key, group=grp, label=label, unit=unit, ticker=t, period=p,
                             value=None if v is None else round(v, 6), formula=formula, note='; '.join(x for x in (nm, flag(t, p, key, v)) if x)))
with open(os.path.join(OUT, 'ratios_table.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# formatted Excel
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter
V = {(r['ratio'], r['ticker'], r['period']): r for r in rows}
wb = Workbook(); ws = wb.active; ws.title = 'Ratios'
hdr = PatternFill('solid', fgColor='1F3D6D'); sec = PatternFill('solid', fgColor='DDE6F2'); luv = PatternFill('solid', fgColor='FFF4CC')
ws.append(['Financial ratios — Southwest (LUV, target) vs peers']); ws['A1'].font = Font(bold=True, size=13)
ws.append([f'TTM to 2026-09-30; balance sheet at period end; market data 2026-11-13. Tax rate for ROIC = {TAX_RATE:.0%} placeholder. Cells with a red corner carry a note.'])
ws.append([])
top = ['Ratio', 'Unit'] + [f'{t}' for t in TICK for _ in PERIODS]
sub = ['', ''] + [p.replace('TTM_2026Q3', 'TTM') for _ in TICK for p in PERIODS]
ws.append(top); ws.append(sub)
for c in list(ws[4]) + list(ws[5]):
    c.font = Font(bold=True, color='FFFFFF'); c.fill = hdr; c.alignment = Alignment(horizontal='center')
for i, t in enumerate(TICK):
    c1 = 3 + i * 3; ws.merge_cells(start_row=4, start_column=c1, end_row=4, end_column=c1 + 2)
fmt = {'%': '0.0%', 'cents': '0.00', 'x': '0.0"x"', 'USD': '"$"0.00', 'ASM': '#,##0', 'USD mn': '#,##0'}
last = None
for key, grp, label, unit, formula, fn in RATIOS:
    if grp != last:
        ws.append([grp]); r = ws.max_row
        for col in range(1, 3 + 3 * len(TICK)): ws.cell(r, col).fill = sec
        ws.cell(r, 1).font = Font(bold=True); last = grp
    ws.append([label, unit] + [V[(key, t, p)]['value'] for t in TICK for p in PERIODS])
    r = ws.max_row
    ws.cell(r, 1).comment = Comment(formula, 'A')
    for i, t in enumerate(TICK):
        for j, p in enumerate(PERIODS):
            c = ws.cell(r, 3 + i * 3 + j); c.number_format = fmt[unit]
            if t == 'LUV': c.fill = luv
            n = V[(key, t, p)]['note']
            if n: c.comment = Comment(n, 'A')
            if c.value is None:
                c.value = 'n.m.' if n.startswith('n.m.') else '–'; c.alignment = Alignment(horizontal='center')
ws.column_dimensions['A'].width = 46; ws.column_dimensions['B'].width = 7
for col in range(3, 3 + 3 * len(TICK)): ws.column_dimensions[get_column_letter(col)].width = 9
ws.freeze_panes = 'C6'
# TTM-only compact sheet for the report
w2 = wb.create_sheet('TTM_compact')
w2.append(['Ratio', 'Unit'] + TICK + ['Formula'])
for c in w2[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = hdr
for key, grp, label, unit, formula, fn in RATIOS:
    w2.append([label, unit] + [V[(key, t, 'TTM_2026Q3')]['value'] for t in TICK] + [formula])
    for i in range(len(TICK)): w2.cell(w2.max_row, 3 + i).number_format = fmt[unit]
w2.column_dimensions['A'].width = 46; w2.column_dimensions['H'].width = 70
wb.save(os.path.join(OUT, 'ratios_table.xlsx'))
print('ratios:', len(RATIOS), 'rows:', len(rows), 'missing:', sum(r['value'] is None for r in rows))
