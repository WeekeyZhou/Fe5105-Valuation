"""
FE5105 Group Project — shared style and format config.

Use this file so every chart and every report section looks the same.
It reproduces the style of Part A (Figure 1 and Table 1 in report/sections/A_*.docx).

Quick start (from any script in the repo)
-----------------------------------------
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'shared'))
    import config as cfg

    # --- data ---
    fin = cfg.load_financials()                       # {(ticker, period, item): value}
    ebitdar = fin[('LUV', 'TTM_2026Q3', 'ebitdar')]

    # --- a chart ---
    fig, ax = cfg.new_figure()                        # report size, house style applied
    for t in cfg.TICKERS:
        ax.bar(cfg.SHORT[t], value[t], color=cfg.color_for(t), width=0.6)
    cfg.finish_figure(fig, ax,
        title='Southwest has the lowest leverage in the group',     # a sentence: the finding
        subtitle='Adjusted net debt / EBITDAR, TTM to 30 Sep 2026',
        filename='fig_B_leverage')                     # -> report/figures/fig_B_leverage.png + .svg

    # --- a Word section ---
    doc = cfg.new_report_doc()                        # A4, margins, fonts, 1.5 spacing, heading style
    cfg.add_heading(doc, '3. Financing and Cost of Capital')
    cfg.add_paragraph(doc, 'Body text ...', lead='Capital structure. ')
    cfg.add_table(doc, caption='Table 2. Cost of capital', header=['Item'] + cfg.TICKERS,
                  rows=[['WACC', '8.1%', '8.4%', '8.0%', '9.6%', '9.9%']], note='Source: ...')
    cfg.add_figure(doc, 'fig_B_leverage.png', caption='Figure 2. Leverage vs peers')
    doc.save(cfg.section_path('B_Financing.docx'))    # -> report/sections/B_Financing.docx

Requires: matplotlib, python-docx (pip install python-docx). pandas is optional.

Rules this file enforces (please do not override per chart)
----------------------------------------------------------
- Southwest (LUV) is always the blue accent; peers are grey. Colour marks the target, not each company.
- If you truly need one colour per company, use cfg.color_for(t, categorical=True); never invent colours.
- One y-axis per chart (no dual axes). Direct labels instead of a legend when there are <= 5 points.
- Title = the finding, as a sentence. Subtitle = what is measured + period. Source line at the bottom.
- Figures: PNG at 300 dpi + SVG, saved in report/figures, named fig_<member>_<topic>.
- Report text: Times New Roman 12 pt, 1.5 line spacing, A4, 2.54 cm margins.
  Tables 9.5 pt; table notes 8.5 pt italic; captions bold 11 pt ("Table N." above tables, "Figure N." above figures).
- Numbers: one decimal for %, two for cents, one for multiples ("1.0x"), use the true minus sign "−".
"""
import os, csv, collections

# --------------------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------------------
SHARED_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SHARED_DIR, '..'))
DATA_PROCESSED = os.path.join(ROOT, 'data', 'processed')
FINANCIALS_CSV = os.path.join(DATA_PROCESSED, 'financials.csv')
RATIOS_CSV = os.path.join(ROOT, 'A_ratios', 'output', 'ratios_table.csv')
FIG_DIR = os.path.join(ROOT, 'report', 'figures')
SECTION_DIR = os.path.join(ROOT, 'report', 'sections')

# --------------------------------------------------------------------------------------
# Companies and key dates (must match shared/assumptions.md)
# --------------------------------------------------------------------------------------
TARGET = 'LUV'
TICKERS = ['LUV', 'DAL', 'UAL', 'AAL', 'ALK']          # always this order in tables and charts
NAMES = {'LUV': 'Southwest Airlines', 'DAL': 'Delta Air Lines', 'UAL': 'United Airlines Holdings',
         'AAL': 'American Airlines Group', 'ALK': 'Alaska Air Group'}
SHORT = {'LUV': 'Southwest', 'DAL': 'Delta', 'UAL': 'United', 'AAL': 'American', 'ALK': 'Alaska'}
VALUATION_DATE = '2026-11-13'
LATEST_BS = 'BS_2026-09-30'
TTM = 'TTM_2026Q3'
SOURCE_LINE = 'Source: company 10-K FY2025 and 10-Q Q3 2026 filings; group calculations.'

# --------------------------------------------------------------------------------------
# Colours (validated reference palette; do not add new hex values)
# --------------------------------------------------------------------------------------
ACCENT = '#2a78d6'        # Southwest / the series that is the point
PEER = '#a3a29b'          # de-emphasised peers
INK = '#0b0b0b'           # titles, key labels
INK_2 = '#52514e'         # body labels, axis titles
MUTED = '#898781'         # tick labels, source line
GRID = '#e1e0d9'          # gridlines
AXIS = '#c3c2b7'          # axis lines / baseline
SURFACE = '#fcfcfb'       # figure background
HIGHLIGHT_FILL = 'FFF4CC'  # Word table: LUV column shading (hex without #)
# Only when every company needs its own colour (max 5 series; prefer emphasis instead):
CATEGORICAL = {'LUV': '#2a78d6', 'DAL': '#eb6834', 'UAL': '#1baf7a', 'AAL': '#6250d6', 'ALK': '#e87ba4'}
# Sequential (magnitude, e.g. sensitivity heat map): light -> dark blue
SEQUENTIAL = ['#e6f0fb', '#b8d3f2', '#86b3e8', '#5593dd', '#2a78d6', '#1f5ca6', '#164276']
# Diverging (above/below a base case, e.g. valuation vs market price): red - grey - blue
DIVERGING = {'neg': '#e34948', 'mid': '#d9d8d2', 'pos': '#2a78d6'}


def color_for(ticker, categorical=False):
    """Emphasis by default: LUV blue, peers grey. categorical=True gives each company a fixed hue."""
    if categorical:
        return CATEGORICAL[ticker]
    return ACCENT if ticker == TARGET else PEER


# --------------------------------------------------------------------------------------
# Figure style (matplotlib)
# --------------------------------------------------------------------------------------
FIG_SIZE = (6.2, 4.2)     # inches; inserted at ~14.8 cm wide in Word
FIG_DPI = 300
FONT = 'DejaVu Sans'      # ships with matplotlib, so every laptop renders identically


def apply_style():
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        'font.family': FONT, 'font.size': 9,
        'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
        'axes.edgecolor': AXIS, 'axes.labelcolor': INK_2, 'axes.titlecolor': INK,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6, 'axes.axisbelow': True,
        'xtick.color': MUTED, 'ytick.color': MUTED, 'xtick.labelsize': 8, 'ytick.labelsize': 8,
        'lines.linewidth': 2, 'lines.markersize': 6, 'legend.frameon': False, 'legend.fontsize': 8,
    })
    return plt


def new_figure(size=FIG_SIZE, nrows=1, ncols=1):
    """Return (fig, ax) in the house style."""
    plt = apply_style()
    fig, ax = plt.subplots(nrows, ncols, figsize=size, dpi=FIG_DPI)
    return fig, ax


def label_point(ax, x, y, text, ticker, dx=8, dy=0):
    """Direct label next to a point (LUV bold black, peers grey)."""
    ax.annotate(text, (x, y), xytext=(dx, dy), textcoords='offset points', va='center', fontsize=8,
                color=INK if ticker == TARGET else INK_2, fontweight='bold' if ticker == TARGET else 'normal')


def bar_labels(ax, bars, fmt='{:.1f}', tickers=None):
    """Value labels on top of bars (use sparingly: only when the exact value matters)."""
    for i, b in enumerate(bars):
        t = tickers[i] if tickers else None
        h = b.get_height()
        ax.annotate(fmt.format(h).replace('-', '−'), (b.get_x() + b.get_width() / 2, h),
                    xytext=(0, 3 if h >= 0 else -10), textcoords='offset points', ha='center', fontsize=8,
                    color=INK if t == TARGET else INK_2, fontweight='bold' if t == TARGET else 'normal')


def finish_figure(fig, ax, title, subtitle='', filename=None, source=SOURCE_LINE, xlabel=None, ylabel=None):
    """Add title (the finding), subtitle (what/when), source line; save PNG + SVG to report/figures."""
    if xlabel is not None: ax.set_xlabel(xlabel)
    if ylabel is not None: ax.set_ylabel(ylabel)
    fig.text(0.01, 0.985, title, fontsize=9.5, fontweight='bold', color=INK, va='top')
    if subtitle:
        fig.text(0.01, 0.935, subtitle, fontsize=7.5, color=INK_2, va='top')
    if source:
        fig.text(0.01, 0.01, source, fontsize=6.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 0.9))
    paths = []
    if filename:
        os.makedirs(FIG_DIR, exist_ok=True)
        base = os.path.join(FIG_DIR, os.path.splitext(filename)[0])
        for ext in ('png', 'svg'):
            fig.savefig(f'{base}.{ext}', dpi=FIG_DPI)
            paths.append(f'{base}.{ext}')
    return paths


# --------------------------------------------------------------------------------------
# Number formatting (use in tables and text so everyone writes numbers the same way)
# --------------------------------------------------------------------------------------
MINUS = '−'


def fmt_pct(x, d=1):          # 0.0439 -> '4.4%'
    return '–' if x is None else f'{x * 100:.{d}f}%'.replace('-', MINUS)


def fmt_mult(x, d=1):         # 1.0 -> '1.0x'
    return '–' if x is None else f'{x:.{d}f}x'.replace('-', MINUS)


def fmt_cents(x, d=2):        # 17.47 -> '17.47'
    return '–' if x is None else f'{x:.{d}f}'.replace('-', MINUS)


def fmt_usd_mn(x, d=0):       # 22002.7 -> '22,003'
    return '–' if x is None else f'{x:,.{d}f}'.replace('-', MINUS)


def fmt_usd_bn(x_mn, d=1):    # 22002.7 (USD mn) -> '22.0'
    return '–' if x_mn is None else f'{x_mn / 1000:,.{d}f}'.replace('-', MINUS)


# --------------------------------------------------------------------------------------
# Data helpers
# --------------------------------------------------------------------------------------
def load_financials(as_dataframe=False):
    """data/processed/financials.csv. Dict {(ticker, period, item): float} or a long pandas DataFrame."""
    if as_dataframe:
        import pandas as pd
        return pd.read_csv(FINANCIALS_CSV)
    out = {}
    with open(FINANCIALS_CSV, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['value'] != '':
                out[(r['ticker'], r['period'], r['item'])] = float(r['value'])
    return out


def load_ratios(as_dataframe=False):
    """A_ratios/output/ratios_table.csv. Dict {(ratio, ticker, period): float} or DataFrame."""
    if as_dataframe:
        import pandas as pd
        return pd.read_csv(RATIOS_CSV)
    out = {}
    with open(RATIOS_CSV, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['value'] != '':
                out[(r['ratio'], r['ticker'], r['period'])] = float(r['value'])
    return out


# --------------------------------------------------------------------------------------
# Word report format (python-docx)
# --------------------------------------------------------------------------------------
REPORT = {
    'page': 'A4', 'margin_cm': 2.54,
    'body_font': 'Times New Roman', 'body_pt': 12, 'line_spacing': 1.5, 'space_after_pt': 6,
    'heading_pt': 13, 'title_pt': 14,
    'caption_pt': 11, 'table_pt': 9.5, 'note_pt': 8.5,
    'figure_width_cm': 14.8,
    'east_asia_font': 'SimSun',   # only used for Chinese review drafts
}


def _set_run_font(run, size_pt=None, bold=None, italic=None, color=None):
    from docx.shared import Pt, RGBColor
    from docx.oxml.ns import qn
    run.font.name = REPORT['body_font']
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), REPORT['east_asia_font'])
    if size_pt: run.font.size = Pt(size_pt)
    if bold is not None: run.bold = bold
    if italic is not None: run.italic = italic
    if color: run.font.color.rgb = RGBColor.from_string(color)


def new_report_doc():
    """A python-docx Document with the group's page set-up and styles."""
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.oxml.ns import qn
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    for side in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'):
        setattr(s, side, Cm(REPORT['margin_cm']))
    normal = doc.styles['Normal']
    normal.font.name = REPORT['body_font']; normal.font.size = Pt(REPORT['body_pt'])
    normal.element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), REPORT['east_asia_font'])
    normal.paragraph_format.line_spacing = REPORT['line_spacing']
    normal.paragraph_format.space_after = Pt(REPORT['space_after_pt'])
    h = doc.styles['Heading 1']
    h.font.name = REPORT['body_font']; h.font.size = Pt(REPORT['heading_pt']); h.font.bold = True
    h.font.color.rgb = None
    h.element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), REPORT['east_asia_font'])
    h.paragraph_format.space_before = Pt(12); h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    return doc


def add_heading(doc, text):
    p = doc.add_paragraph(style='Heading 1')
    _set_run_font(p.add_run(text), REPORT['heading_pt'], bold=True, color='000000')
    return p


def add_paragraph(doc, text, lead=None):
    """Justified body paragraph. lead = optional bold run-in heading, e.g. 'Profitability. '."""
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if lead: _set_run_font(p.add_run(lead), REPORT['body_pt'], bold=True)
    _set_run_font(p.add_run(text), REPORT['body_pt'])
    return p


def add_caption(doc, text):
    from docx.shared import Pt
    p = doc.add_paragraph(); p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.0
    _set_run_font(p.add_run(text), REPORT['caption_pt'], bold=True)
    return p


def add_note(doc, text):
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0; p.paragraph_format.space_after = Pt(8)
    _set_run_font(p.add_run(text), REPORT['note_pt'], italic=True)
    return p


def _cell_border(cell, top=False, bottom=False):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    tcPr = cell._element.get_or_add_tcPr()
    borders = OxmlElement('w:tcBorders')
    for edge, on in (('top', top), ('left', False), ('bottom', bottom), ('right', False)):
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), 'single' if on else 'nil')
        if on: el.set(qn('w:sz'), '8'); el.set(qn('w:color'), '000000')
        borders.append(el)
    tcPr.append(borders)


def _cell_fill(cell, hex_fill):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hex_fill)
    cell._element.get_or_add_tcPr().append(shd)


def add_table(doc, caption, header, rows, note=None, first_col_cm=6.0, highlight_col='LUV'):
    """Three-rule academic table like Table 1 in Part A.
    header: ['Ratio', 'LUV', 'DAL', ...]; rows: list of lists of strings.
    A row with a single element is a group label (bold italic, e.g. ['Profitability']).
    The column whose header equals highlight_col is shaded and bold."""
    from docx.shared import Pt, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    add_caption(doc, caption)
    ncol = len(header)
    t = doc.add_table(rows=0, cols=ncol); t.autofit = False
    other = (16.0 - first_col_cm) / (ncol - 1)
    widths = [Cm(first_col_cm)] + [Cm(other)] * (ncol - 1)
    hi = header.index(highlight_col) if highlight_col in header else None

    def fill_row(values, top=False, bottom=False, bold_all=False, group=False):
        cells = t.add_row().cells
        if group:
            m = cells[0].merge(cells[-1]); m.width = Cm(16.0)
            p = m.paragraphs[0]; p.paragraph_format.line_spacing = 1.0; p.paragraph_format.space_after = Pt(0)
            _set_run_font(p.add_run(values[0]), REPORT['table_pt'], bold=True, italic=True)
            _cell_border(m, top, bottom)
            return
        for i, v in enumerate(values):
            c = cells[i]; c.width = widths[i]
            p = c.paragraphs[0]; p.paragraph_format.line_spacing = 1.0; p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            _set_run_font(p.add_run(str(v)), REPORT['table_pt'], bold=bold_all or (hi is not None and i == hi))
            if hi is not None and i == hi: _cell_fill(c, HIGHLIGHT_FILL)
            _cell_border(c, top, bottom)

    fill_row(header, top=True, bottom=True, bold_all=True)
    for k, r in enumerate(rows):
        fill_row(r, bottom=(k == len(rows) - 1), group=(len(r) == 1))
    _fix_widths(t, widths)
    if note: add_note(doc, note)
    return t


def _fix_widths(table, widths):
    """Word and LibreOffice read column widths from the table grid, not only from cells."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    tbl = table._tbl
    tblPr = tbl.tblPr
    layout = OxmlElement('w:tblLayout'); layout.set(qn('w:type'), 'fixed'); tblPr.append(layout)
    tblW = tblPr.find(qn('w:tblW'))
    if tblW is None: tblW = OxmlElement('w:tblW'); tblPr.append(tblW)
    tblW.set(qn('w:w'), str(sum(int(w.twips) for w in widths))); tblW.set(qn('w:type'), 'dxa')
    grid = tbl.tblGrid
    for i, gc in enumerate(grid.findall(qn('w:gridCol'))):
        gc.set(qn('w:w'), str(int(widths[i].twips)))
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            tcW = cell._element.get_or_add_tcPr().get_or_add_tcW()
            span = cell._element.grid_span
            tcW.type = 'dxa'; tcW.w = sum(int(w.twips) for w in widths[i:i + span]) if span > 1 else int(widths[i].twips)


def add_figure(doc, png_name_or_path, caption):
    """Caption above, image centred at the standard width."""
    from docx.shared import Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    path = png_name_or_path if os.path.isabs(png_name_or_path) else os.path.join(FIG_DIR, png_name_or_path)
    add_caption(doc, caption)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Cm(REPORT['figure_width_cm']))
    return p


def section_path(filename):
    os.makedirs(SECTION_DIR, exist_ok=True)
    return os.path.join(SECTION_DIR, filename)


if __name__ == '__main__':
    print('ROOT        ', ROOT)
    print('financials  ', os.path.exists(FINANCIALS_CSV), FINANCIALS_CSV)
    print('ratios      ', os.path.exists(RATIOS_CSV), RATIOS_CSV)
    print('figures dir ', FIG_DIR)
    print('sections dir', SECTION_DIR)
