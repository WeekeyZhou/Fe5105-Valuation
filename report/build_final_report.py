"""
Merge Parts A-D into report/final_report.docx in the group format (shared/config.py).
Text is taken verbatim from each member's section; only numbering, cross-references and layout change.
Run from the repository root:  python report/build_final_report.py
"""
import os, re, sys, copy
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'shared'))
import config as cfg

SRC = {
    'A': os.path.join(ROOT, 'report', 'sections', 'A_Intro_FinancialPerformance.docx'),
    'B': os.path.join(ROOT, 'B_financing_wacc', 'output', 'FE5105_Part_B_2p5pages_Corrected.docx'),
    'C': os.path.join(ROOT, 'C_valuation', 'Part_C_Valuation.docx'),
    'D': os.path.join(ROOT, 'report', 'sections', 'D_Risk_Management.docx'),
}
FIG = {
    1: os.path.join(ROOT, 'report', 'figures', 'fig_unit_cost_vs_revenue.png'),
    2: os.path.join(ROOT, 'C_valuation', 'LUV_Valuation_Range.png'),
    3: os.path.join(ROOT, 'report', 'figures', 'fig_D_liquidity_stress.png'),
    4: os.path.join(ROOT, 'report', 'figures', 'fig_D_hedging_comparison.png'),
}
OUT = os.path.join(ROOT, 'report', 'final_report.docx')

# ------------------------------------------------------------------ editable front/back matter
TITLE = 'Southwest Airlines (LUV): Performance, Financing, Valuation and Risk Management'
SUBTITLE = 'FE5105 Corporate Financing and Risk — Group Project, Semester 1 AY2026/27'
MEMBERS = 'Group members: ZHOU Mo (A), ZHANG Jiaxin (B), RUAN Yalin (C), JING Wanyi (D)'
CONCLUSION = [
    'Southwest pairs the lowest non-fuel unit cost and lowest leverage in its peer group with weak unit revenue and, '
    'since 2025, unhedged fuel exposure; its TTM margin recovered to 4.4% while every peer\'s fell. With a WACC of '
    '7.97%, we recommend a conservative capital structure that preserves borrowing capacity. The DCF ($50.22) and '
    'peer median ($48.87) both exceed the $44.94 close, but the modelled ranges include the market price, so evidence '
    'of undervaluation is weak. The key risk is liquidity under a fuel shock: a 30% price rise implies a USD 1.1 billion '
    'shortfall without refinancing, which a 50% fuel collar would reduce by about USD 0.7 billion.',
]
SOURCES = ('Company filings from SEC EDGAR for LUV, DAL, UAL, AAL and ALK: Form 10-K FY2021–FY2025, Form 10-Q Q3 2026 '
           'and Form 8-K earnings releases. Market data: closing prices on 13 November 2026; U.S. Treasury 10-year '
           'yield; Damodaran (implied equity risk premium, air transport industry beta); ICE BofA option-adjusted '
           'spreads via FRED. All figures are reproducible from the group\'s code repository.')
AI_DECLARATION = ('The group used Claude (Anthropic) and ChatGPT (OpenAI) to assist with coding, data extraction, '
                  'drafting and language editing. All members checked the calculations, interpreted the results '
                  'and reviewed the final text, in line with the NUS policy on the use of AI in academic work.')

# ------------------------------------------------------------------ helpers
def blocks(path):
    """Ordered list of ('p', Paragraph) / ('t', Table) from a source document."""
    d = Document(path); out = []
    from docx.table import Table
    for el in d.element.body.iterchildren():
        tag = el.tag.split('}')[1]
        if tag == 'p': out.append(('p', Paragraph(el, d)))
        elif tag == 'tbl': out.append(('t', Table(el, d)))
    return out

def texts(path):
    return [b[1].text.strip() for b in blocks(path) if b[0] == 'p' and b[1].text.strip()]

def table_rows(path, k):
    d = Document(path); t = d.tables[k]; rows = []
    for r in t.rows:
        cells = []
        for c in r.cells:
            v = ' '.join(c.text.split())
            if not cells or c._tc is not prev: cells.append(v)
            prev = c._tc
        rows.append(cells)
    return rows

def find(lst, start):
    for t in lst:
        if t.startswith(start): return t
    raise KeyError(start)

def h2(doc, text):
    p = doc.add_paragraph(); p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(2)
    cfg._set_run_font(p.add_run(text), cfg.REPORT['body_pt'], bold=True, italic=True)

def para(doc, text, leads=()):
    for lead in leads:
        if text.startswith(lead):
            return cfg.add_paragraph(doc, text[len(lead):].lstrip(), lead=lead.strip() + ' ')
    return cfg.add_paragraph(doc, text)

def figure(doc, n, caption, width_cm):
    cfg.add_caption(doc, f'Figure {n}. {caption}')
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4); p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(FIG[n], width=Cm(width_cm))

def copy_math(doc, src_par):
    new = copy.deepcopy(src_par._p)
    anchor = doc.add_paragraph()._p          # inserted before the section properties
    anchor.addprevious(new); anchor.getparent().remove(anchor)
    p = Paragraph(new, doc); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0

def page_number_footer(doc):
    p = doc.sections[0].footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(); cfg._set_run_font(run, 9)
    for kind, text in (('begin', None), (None, 'PAGE'), ('end', None)):
        if kind:
            el = OxmlElement('w:fldChar'); el.set(qn('w:fldCharType'), kind)
        else:
            el = OxmlElement('w:instrText'); el.set(qn('xml:space'), 'preserve'); el.text = text
        run._r.append(el)

# ------------------------------------------------------------------ source text
A, B, C, D = (texts(SRC[k]) for k in 'ABCD')
FIX = [  # (part, old, new): numbering / cross-reference / typo fixes only
    ('B', 'Table B1', 'Table 2'), ('B', 'Table B2', 'Table 3'),
    ('C', '6.60× to12.23× ,', '6.60× to 12.23×,'),
    ('D', 'Figure D1', 'Figure 3'), ('D', 'Figure D2', 'Figure 4'), ('D', 'Table D1', 'Table 8'),
]
def fx(part, s):
    for p, o, n in FIX:
        if p == part: s = s.replace(o, n)
    return s
A = [fx('A', s) for s in A]; B = [fx('B', s) for s in B]; C = [fx('C', s) for s in C]; D = [fx('D', s) for s in D]

# ------------------------------------------------------------------ build
doc = cfg.new_report_doc()
page_number_footer(doc)
t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER; t.paragraph_format.space_after = Pt(0)
cfg._set_run_font(t.add_run(TITLE), 14, bold=True)
for line in (SUBTITLE + '  |  ' + MEMBERS,):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0; cfg._set_run_font(p.add_run(line), 10.5, italic=True)

# 1-2  Part A
cfg.add_heading(doc, '1. Introduction')
para(doc, find(A, 'Southwest Airlines (LUV) is'))
para(doc, find(A, 'Financial data come from').replace(" Delta's third-party refinery sales are removed from both revenue and cost so that unit metrics reflect airline operations.", ''))
cfg.add_heading(doc, '2. Financial Performance Relative to Peers')
a_rows = table_rows(SRC['A'], 0)
rows = []
for r in a_rows[1:]:
    rows.append([r[0]] if len(set(r)) == 1 or all(c == '' for c in r[1:]) else r)
cfg.add_table(doc, 'Table 1. Key financial ratios, Southwest vs peers', a_rows[0], rows,
              note=find(A, 'TTM = twelve months'), first_col_cm=6.4)
LA = ('Profitability.', 'Cost and revenue model.', 'Leverage and liquidity.')
para(doc, find(A, 'Profitability.'), LA); para(doc, find(A, 'Cost and revenue model.'), LA)
para(doc, find(A, 'Leverage and liquidity.'), LA)
figure(doc, 1, 'Unit cost excluding fuel vs unit revenue, TTM to 30 Sep 2026', 9.8)

# 3  Part B
cfg.add_heading(doc, '3. Financing and Cost of Capital')
h2(doc, '3.1 Financing Sources and Hidden Leverage')
for s in ('The five airlines rely', 'Beyond conventional loans', 'Table 2 shows'): para(doc, find(B, s))
b1 = table_rows(SRC['B'], 0)
cfg.add_table(doc, 'Table 2. Supplementary obligations as of 30 September 2026 (USD millions)', b1[0], b1[1:],
              note=find(B, 'Note: Operating leases'), first_col_cm=4.0, highlight_col=None)
h2(doc, '3.2 Estimating the Cost of Capital')
for s in ('In the following formula', 'CAPM uses'): para(doc, find(B, s))
EQS = [  # B's four equations, typed as text so they render identically in Word, LibreOffice and PDF
    [('β', ''), ('L', 'sub'), (' = β', ''), ('U', 'sub'), (' × [1 + (1 − T) × D/E]', '')],
    [('K', ''), ('e', 'sub'), (' = R', ''), ('f', 'sub'), (' + β', ''), ('L', 'sub'), (' × ERP', '')],
    [('K', ''), ('d', 'sub'), (' = R', ''), ('f', 'sub'), (' + Credit spread', '')],
    [('WACC = E/(D + E) × K', ''), ('e', 'sub'), (' + D/(D + E) × K', ''), ('d', 'sub'), (' × (1 − T)', '')],
]
for k, eq in enumerate(EQS):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.15; p.paragraph_format.space_after = Pt(4 if k == len(EQS) - 1 else 0)
    p.paragraph_format.keep_with_next = True
    for text, kind in eq:
        r = p.add_run(text); cfg._set_run_font(r, cfg.REPORT['body_pt'], italic=True)
        if kind == 'sub': r.font.subscript = True
b2 = table_rows(SRC['B'], 1)
cfg.add_table(doc, 'Table 3. Estimated costs of capital as of 13 November 2026', b2[0], b2[1:],
              first_col_cm=3.0, highlight_col=None)
for s in ('LUV, DAL, UAL and ALK have', 'One limitation is'): para(doc, find(B, s))
h2(doc, '3.3 Capital Structure Recommendation for LUV')
for s in ('LUV has $6,871', 'For LUV, keeping', 'Therefore, LUV should'): para(doc, find(B, s))

# 4  Part C
cfg.add_heading(doc, '4. Valuation')
para(doc, find(C, 'As of November 13, 2026'))
h2(doc, '4.1 Five-Year Operating Forecast')
c1 = table_rows(SRC['C'], 0)
cfg.add_table(doc, 'Table 4. Five-year operating forecast', c1[0], c1[1:], first_col_cm=4.5, highlight_col=None)
for s in ('We use the trailing twelve months', 'Gross cash capex starts'): para(doc, find(C, s))
h2(doc, '4.2 DCF and Peer Valuation')
for s in ('We discount FCFF', 'Terminal growth of 2.25%', 'The four peers'): para(doc, find(C, s))
c2 = table_rows(SRC['C'], 1)
cfg.add_table(doc, 'Table 5. Peer valuation multiples (TTM to 30 Sep 2026)', c2[0], c2[1:], first_col_cm=4.5)
figure(doc, 2, 'Southwest valuation ranges, USD per share', 12.5)
h2(doc, '4.3 Sensitivity and Evidence of Undervaluation')
para(doc, find(C, 'Across WACC'))
c3 = table_rows(SRC['C'], 2)
cfg.add_table(doc, 'Table 6. DCF value per share (USD): WACC vs terminal growth', c3[0], c3[1:], first_col_cm=4.5, highlight_col=None)
para(doc, find(C, 'Moving fuel prices'))
c4 = table_rows(SRC['C'], 3)
cfg.add_table(doc, 'Table 7. DCF value under alternative two-year fuel price paths', c4[0], c4[1:], first_col_cm=4.5, highlight_col=None)
para(doc, find(C, 'The market price can be reconciled'))

# 5  Part D
cfg.add_heading(doc, '5. Financial Planning and Risk Management')
para(doc, find(D, 'This section evaluates'))
h2(doc, '5.1 Liquidity and Near-Term Cash Requirements')
d1 = table_rows(SRC['D'], 0)
cfg.add_table(doc, 'Table 8. Southwest liquidity indicators', d1[0], d1[1:],
              note=find(D, 'Source: Southwest FY2025'), first_col_cm=8.0, highlight_col=None)
LD = ('Liquidity.', 'Cash conversion.', 'Debt and investment needs.', 'Funding stress.', 'Recommendation and firm value.')
for s in ('Liquidity.', 'Cash conversion.', 'Debt and investment needs.'): para(doc, find(D, s), LD)
h2(doc, '5.2 Adverse Scenario: Jet Fuel Price Shock')
para(doc, find(D, 'We model illustrative')); para(doc, find(D, 'Funding stress.'), LD)
figure(doc, 3, 'Liquidity sensitivity to fuel prices and refinancing assumptions', 9.0)
h2(doc, '5.3 Major Risks and Existing Risk Management')
for s in ('Fuel-price volatility', 'Southwest discontinued'): para(doc, find(D, s))
h2(doc, '5.4 Proposed Hedge and Implications for Firm Value')
for s in ('We evaluate a selective', 'Under a 30% fuel-price shock'): para(doc, find(D, s))
para(doc, find(D, 'Recommendation and firm value.'), LD)
figure(doc, 4, 'Illustrative free cash flow under alternative fuel hedging strategies', 9.0)
cfg.add_note(doc, find(D, 'Sources: Southwest Airlines FY2025'))

# 6  Conclusion + back matter
cfg.add_heading(doc, '6. Conclusion')
for s in CONCLUSION: para(doc, s)
h2(doc, 'Data Sources and Declaration of AI Use'); cfg.add_note(doc, SOURCES); cfg.add_note(doc, AI_DECLARATION)

# keep every table on one page; small gap after tables
from docx.table import Table as _T
body = doc.element.body
for tbl in list(body.iterchildren(qn('w:tbl'))):
    T = _T(tbl, doc)
    for i, row in enumerate(T.rows):
        trPr = row._tr.get_or_add_trPr(); cs = OxmlElement('w:cantSplit'); trPr.append(cs)
        if i < len(T.rows) - 1:
            for c in row.cells:
                for pp in c.paragraphs: pp.paragraph_format.keep_with_next = True
    nxt = tbl.getnext()
    is_note = nxt is not None and nxt.tag == qn('w:p') and any(r.get(qn('w:val')) is None and False for r in [])
    np_ = Paragraph(nxt, doc) if nxt is not None and nxt.tag == qn('w:p') else None
    if np_ is not None and not (np_.runs and np_.runs[0].italic):
        sp = OxmlElement('w:p'); tbl.addnext(sp)
        spp = Paragraph(sp, doc); spp.paragraph_format.space_after = Pt(0); spp.paragraph_format.line_spacing = Pt(6)

# house style: $ + million/billion in text, US spelling, day-month-year dates
import re as _re
_MON = 'January|February|March|April|May|June|July|August|September|October|November|December'
_UNIT = {'bn': 'billion', 'mn': 'million', 'billion': 'billion', 'million': 'million'}
def _style(txt, in_table):
    def money(m):
        neg, num, unit = m.group(1), m.group(2), m.group(3)
        u = unit if in_table and unit in ('bn', 'mn') else _UNIT[unit]
        return ('\u2212' if neg else '') + '$' + num + ' ' + u
    txt = _re.sub(r'USD\s?(-)?([\d][\d,.]*)\s?(bn|mn|billion|million)\b', money, txt)
    txt = _re.sub(r'\b(' + _MON + r') (\d{1,2}), (\d{4})', r'\2 \1 \3', txt)
    for o, n in (('capitalisation', 'capitalization'), ('Capitalisation', 'Capitalization'),
                 ('modelled', 'modeled'), ('modelling', 'modeling')):
        txt = txt.replace(o, n)
    return txt
for t_el in doc.element.body.iter(qn('w:t')):
    inside = any(a.tag == qn('w:tbl') for a in t_el.iterancestors())
    if t_el.text: t_el.text = _style(t_el.text, inside)

doc.save(OUT)
print('saved', OUT)
