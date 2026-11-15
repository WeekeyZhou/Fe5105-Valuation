"""Writes data/processed outputs: financials.csv (long), financials_wide.xlsx, validation_checks.csv."""
import os, csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

TICK = ['LUV', 'DAL', 'UAL', 'AAL', 'ALK']
NAMES = {'LUV': 'Southwest Airlines (target)', 'DAL': 'Delta Air Lines', 'UAL': 'United Airlines Holdings',
         'AAL': 'American Airlines Group', 'ALK': 'Alaska Air Group'}
PERIODS = {
    'FY2023': ('FY', '2023-01-01', '2023-12-31'), 'FY2024': ('FY', '2024-01-01', '2024-12-31'),
    'FY2025': ('FY', '2025-01-01', '2025-12-31'), '9M2025': ('9M', '2025-01-01', '2025-09-30'),
    '9M2026': ('9M', '2026-01-01', '2026-09-30'), 'Q3_2025': ('Q3', '2025-07-01', '2025-09-30'),
    'Q3_2026': ('Q3', '2026-07-01', '2026-09-30'), 'TTM_2026Q3': ('TTM', '2025-10-01', '2026-09-30'),
    'BS_2024-12-31': ('BS', '', '2024-12-31'), 'BS_2025-12-31': ('BS', '', '2025-12-31'),
    'BS_2026-09-30': ('BS', '', '2026-09-30'), 'VAL_2026-11-13': ('MKT', '', '2026-11-13'),
}
SECTIONS = [
    ('Income statement', ['revenue', 'refinery_sales_third_party', 'revenue_airline', 'fuel_expense', 'labor_expense',
                          'aircraft_rent', 'da', 'total_opex', 'total_opex_airline', 'operating_income', 'ebitda', 'ebitdar',
                          'interest_expense', 'interest_income', 'interest_expense_net', 'pretax_income', 'income_tax', 'net_income']),
    ('Cash flow', ['cfo', 'capex', 'free_cash_flow', 'cfi', 'cff', 'dividends_paid', 'buybacks', 'interest_paid']),
    ('Operating statistics', ['asm', 'rpm', 'fuel_gallons']),
    ('Balance sheet', ['cash', 'st_investments', 'cash_and_sti', 'receivables', 'current_assets', 'total_assets',
                       'accounts_payable', 'air_traffic_liability_total', 'current_liabilities', 'debt_current',
                       'debt_noncurrent', 'total_debt', 'finance_lease_liab', 'oplease_liab_current', 'oplease_liab_noncurrent',
                       'oplease_liab_total', 'adjusted_debt', 'adjusted_net_debt', 'pension_liab', 'total_liabilities',
                       'equity', 'liab_and_equity']),
    ('Market data (valuation date)', ['share_price', 'shares_outstanding', 'market_cap', 'enterprise_value']),
]
ORDER = [i for _, items in SECTIONS for i in items]


def write(rows, V, chk, out):
    os.makedirs(out, exist_ok=True)
    pk = list(PERIODS)
    rows = sorted(rows, key=lambda r: (TICK.index(r['ticker']), ORDER.index(r['item']) if r['item'] in ORDER else 999,
                                       pk.index(r['period'])))
    # 1) long CSV
    with open(os.path.join(out, 'financials.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['ticker', 'period', 'period_type', 'period_start', 'period_end', 'item', 'value', 'unit', 'source', 'note'])
        for r in rows:
            pt, ps, pe = PERIODS[r['period']]
            w.writerow([r['ticker'], r['period'], pt, ps, pe, r['item'], r['value'], r['unit'], r['source'], r['note']])
    # 2) checks CSV
    with open(os.path.join(out, 'validation_checks.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['ticker', 'period', 'check', 'lhs', 'rhs', 'difference', 'pass'])
        for t, p, name, a, b in sorted(chk):
            w.writerow([t, p, name, round(a, 3), round(b, 3), round(a - b, 3), abs(a - b) <= 1.01])
    # 3) wide Excel
    lookup = {(r['ticker'], r['period'], r['item']): r for r in rows}
    wb = Workbook(); ws0 = wb.active; ws0.title = 'README'
    bold = Font(bold=True); hdr = PatternFill('solid', fgColor='1F3D6D'); sec = PatternFill('solid', fgColor='DDE6F2')
    note_fill = PatternFill('solid', fgColor='FFF4CC')
    info = [
        ['FE5105 Group Project — processed financial data (Member A)'],
        ['All amounts USD millions unless the Unit column says otherwise. Costs are positive numbers; capex is a positive outflow.'],
        ['Sources: FY2025 10-K and Q3 2026 10-Q inline XBRL (parent-company, non-dimensional facts); operating statistics from MD&A tables; market data 2026-11-13.'],
        ['TTM_2026Q3 = FY2025 + 9M2026 - 9M2025. BS_ = balance sheet date. VAL_ = valuation date 2026-11-13.'],
        ['Yellow cells carry a note (hover the item name or see the long CSV). Full definitions: DATA_DICTIONARY.md.'],
        ['Machine-readable version for code: financials.csv (long format).'],
    ]
    for r in info: ws0.append(r)
    ws0['A1'].font = Font(bold=True, size=13); ws0.column_dimensions['A'].width = 140
    for t in TICK:
        ws = wb.create_sheet(t)
        ws.append([f'{t} — {NAMES[t]}']); ws['A1'].font = Font(bold=True, size=12)
        ws.append(['Item'] + pk + ['Unit'])
        for c in ws[2]: c.font = Font(bold=True, color='FFFFFF'); c.fill = hdr; c.alignment = Alignment(horizontal='center', wrap_text=True)
        for sname, items in SECTIONS:
            ws.append([sname]); ws.cell(ws.max_row, 1).font = bold
            for col in range(1, len(pk) + 3): ws.cell(ws.max_row, col).fill = sec
            for it in items:
                vals = [lookup.get((t, p, it)) for p in pk]
                if not any(vals): continue
                unit = next(v['unit'] for v in vals if v)
                ws.append([it] + [v['value'] if v else None for v in vals] + [unit])
                notes = [f"{p}: {v['note']}" for p, v in zip(pk, vals) if v and v['note']]
                for p, v in zip(pk, vals):
                    if v and v['note']:
                        ws.cell(ws.max_row, 2 + pk.index(p)).fill = note_fill
                if notes:
                    from openpyxl.comments import Comment
                    ws.cell(ws.max_row, 1).comment = Comment('\n'.join(sorted(set(notes)))[:1500], 'A')
        ws.column_dimensions['A'].width = 30
        for col in range(2, len(pk) + 3): ws.column_dimensions[get_column_letter(col)].width = 13
        for row in ws.iter_rows(min_row=3):
            for c in row[1:-1]:
                if isinstance(c.value, (int, float)): c.number_format = '#,##0;(#,##0);"–"'
        ws.freeze_panes = 'B3'
    # comparison sheet
    ws = wb.create_sheet('Compare_latest', 1)
    ws.append(['Peer comparison — TTM to 2026-09-30, balance sheet at 2026-09-30, market data at 2026-11-13'])
    ws['A1'].font = Font(bold=True, size=12)
    ws.append(['Item', 'Period'] + TICK + ['Unit'])
    for c in ws[2]: c.font = Font(bold=True, color='FFFFFF'); c.fill = hdr
    for sname, items in SECTIONS:
        per = 'BS_2026-09-30' if sname == 'Balance sheet' else ('VAL_2026-11-13' if sname.startswith('Market') else 'TTM_2026Q3')
        ws.append([sname]); ws.cell(ws.max_row, 1).font = bold
        for col in range(1, len(TICK) + 4): ws.cell(ws.max_row, col).fill = sec
        for it in items:
            vals = [lookup.get((t, per, it)) for t in TICK]
            if not any(vals): continue
            unit = next(v['unit'] for v in vals if v)
            ws.append([it, per] + [v['value'] if v else None for v in vals] + [unit])
    ws.column_dimensions['A'].width = 30; ws.column_dimensions['B'].width = 16
    for col in range(3, 9): ws.column_dimensions[get_column_letter(col)].width = 13
    for row in ws.iter_rows(min_row=3):
        for c in row[2:-1]:
            if isinstance(c.value, (int, float)): c.number_format = '#,##0.##;(#,##0.##);"–"'
    ws.freeze_panes = 'C3'
    wc = wb.create_sheet('Checks')
    wc.append(['ticker', 'period', 'check', 'lhs', 'rhs', 'difference', 'pass'])
    for c in wc[1]: c.font = bold
    for t, p, name, a, b in sorted(chk): wc.append([t, p, name, round(a, 1), round(b, 1), round(a - b, 1), abs(a - b) <= 1.01])
    wc.column_dimensions['C'].width = 34
    wb.save(os.path.join(out, 'financials_wide.xlsx'))
    print('wrote', len(rows), 'rows;', sum(abs(a - b) <= 1.01 for *_, a, b in chk), '/', len(chk), 'checks passed')
