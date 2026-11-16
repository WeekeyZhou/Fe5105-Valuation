"""Figure for the report: unit cost vs unit revenue (TTM). Run: python A_ratios/make_figures.py"""
import os, csv
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'report', 'figures'); os.makedirs(OUT, exist_ok=True)
R = {(r['ratio'], r['ticker'], r['period']): r['value'] for r in csv.DictReader(open(os.path.join(HERE, 'output', 'ratios_table.csv'), encoding='utf-8'))}
NAMES = {'LUV': 'Southwest', 'DAL': 'Delta', 'UAL': 'United', 'AAL': 'American', 'ALK': 'Alaska'}
ACCENT, PEER, INK, INK2, MUTED, GRID, SURF = '#2a78d6', '#a3a29b', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#fcfcfb'
P = 'TTM_2026Q3'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
fig, ax = plt.subplots(figsize=(6.2, 4.2), dpi=300); fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
# offsets for labels (points) chosen to avoid collisions
OFF = {'LUV': (8, -10), 'DAL': (8, 4), 'UAL': (8, -10), 'AAL': (8, 4), 'ALK': (8, 4)}
for t in NAMES:
    x, y = float(R[('casm_ex_fuel', t, P)]), float(R[('trasm', t, P)])
    m = float(R[('operating_margin', t, P)])
    col = ACCENT if t == 'LUV' else PEER
    ax.scatter(x, y, s=70 if t == 'LUV' else 46, color=col, edgecolor=SURF, linewidth=1.5, zorder=3)
    ax.annotate(f"{NAMES[t]}\n{m:+.1%} op. margin".replace('+-', '−'), (x, y), xytext=OFF[t], textcoords='offset points',
                fontsize=8, color=INK if t == 'LUV' else INK2, fontweight='bold' if t == 'LUV' else 'normal', va='center')
ax.set_xlabel('Unit cost excluding fuel — CASM ex-fuel (US cents)', color=INK2)
ax.set_ylabel('Unit revenue — TRASM (US cents)', color=INK2)
ax.set_xlim(11.8, 15.9); ax.set_ylim(15.5, 22.2)
ax.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
for s in ('left', 'bottom'): ax.spines[s].set_color('#c3c2b7')
ax.tick_params(colors=MUTED, labelsize=8)
fig.text(0.01, 0.985, 'Southwest: low unit cost, but network carriers earn far more per seat-mile', fontsize=9.5, fontweight='bold', color=INK, va='top')
fig.text(0.01, 0.935, 'Twelve months to 30 Sep 2026. Delta excludes third-party refinery sales. Special items not removed.', fontsize=7.5, color=INK2, va='top')
fig.text(0.01, 0.01, 'Source: company 10-K FY2025 and 10-Q Q3 2026 filings; group calculations.', fontsize=6.5, color=MUTED)
fig.tight_layout(rect=(0, 0.03, 1, 0.9))
for ext in ('png', 'svg'): fig.savefig(os.path.join(OUT, f'fig_unit_cost_vs_revenue.{ext}'), facecolor=SURF)
print('saved', OUT)
