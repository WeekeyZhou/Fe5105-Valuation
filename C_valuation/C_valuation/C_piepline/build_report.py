import json
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

root = Path(sys.argv[1])
data = json.loads((root / "results.json").read_text())
summary = {r[0]: r[1:] for r in data["summary"]}
rate_grid = data["sensitivity"][:6]
fuel_cases = data["sensitivity"][9:12]
fcff = data["fcff"]
peer = data["peer"]
market = summary["Market close (USD/share)"][0]
base = summary["DCF value (USD/share)"][0]
a = data["assumptions"]
forecast = a["forecast"]
peer_low, peer_mid, peer_high = peer[7:10]
dcf_low, dcf_high = summary["DCF WACC × g range (USD/share)"]
def metric(name):
    return summary[name][0]

def bn(value):
    return f"${value / 1000:,.2f} billion"

def driver(key, format_spec):
    values = forecast[key]
    return f"{values[0]:{format_spec}} in Year 1 and {values[-1]:{format_spec}} in Year 5"

def price_position(low, high):
    if market < low:
        return "below"
    if market > high:
        return "above"
    return "within"

assert all(isinstance(x, (int, float)) for row in rate_grid[1:] for x in row)
assert abs(base - rate_grid[3][3]) < 1e-10
assert abs(base - fuel_cases[1][4]) < 1e-10

# Standalone print-resolution range chart.
image = Image.new("RGB", (1500, 500), "#FFFFFF")
drawing = ImageDraw.Draw(image)
def font(size, bold=False):
    name = "Arial Bold.ttf" if bold else "Arial.ttf"
    fallback = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    font_dir = Path(os.environ.get("C_FONT_DIR", "/System/Library/Fonts/Supplemental"))
    for candidate in (str(font_dir / name), fallback):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)

navy = "#17354B"
teal = "#006F68"
muted = "#516576"
bounds = [dcf_low, dcf_high, market, peer_low[4], peer_high[4], fuel_cases[-1][4], fuel_cases[0][4]]
spread = max(max(bounds) - min(bounds), 1)
step = max(1, math.ceil(spread / 9))
axis_min = math.floor((min(bounds) - spread * .08) / step) * step
axis_max = math.ceil((max(bounds) + spread * .08) / step) * step
def x(value):
    return 366 + int((value - axis_min) / (axis_max-axis_min) * 1045)

drawing.text((35, 20), "Southwest Airlines valuation ranges", fill=navy, font=font(44, True))
drawing.text((37, 79), f"USD per share  |  {data['asOf']}", fill=muted, font=font(27))
for tick in range(axis_min, axis_max + 1, step):
    drawing.line((x(tick), 155, x(tick), 401), fill="#DBE4EA", width=2)
    drawing.text((x(tick), 426), str(tick), fill=muted, anchor="mt", font=font(26))
mx = x(market)
for y in range(151, 409, 15):
    drawing.line((mx,y,mx,y+9), fill="#985117", width=3)
drawing.text((mx, 125), f"Market ${market:.2f}", fill="#985117", anchor="mm", font=font(28, True))
ranges = [
    ("DCF  WACC × growth", *summary["DCF WACC × g range (USD/share)"], base, navy),
    ("Peer EV/EBITDAR", *summary["Peer range (USD/share)"], summary["Peer median (USD/share)"][0], teal),
    ("DCF  two-year fuel shock", fuel_cases[-1][4], fuel_cases[0][4], base, navy),
]
for (label, low, high, mid, color), y in zip(ranges, [200, 281, 362]):
    drawing.text((38, y), label, fill=navy, anchor="lm", font=font(27, True))
    drawing.line((x(low),y,x(high),y), fill=color, width=8)
    for value in (low, high):
        drawing.line((x(value),y-9,x(value),y+9), fill=color, width=3)
    drawing.ellipse((x(mid)-10,y-10,x(mid)+10,y+10), fill="#FFFFFF", outline=color, width=4)
    drawing.text((x(low)-10,y-14), f"{low:.2f}", fill=color, anchor="rb", font=font(24))
    drawing.text((x(high)+10,y-14), f"{high:.2f}", fill=color, anchor="lb", font=font(24))
drawing.text((38, 473), "Circles mark the DCF base case or peer median. Ranges reflect modeled inputs.", fill=muted, font=font(23), anchor="lm")
chart = root / "LUV_Valuation_Range.png"
image.save(chart, dpi=(240,240))

doc = Document()
doc.core_properties.title = "Southwest Airlines Valuation"
doc.core_properties.author = ""
section = doc.sections[0]
section.top_margin = section.bottom_margin = Inches(.70)
section.left_margin = section.right_margin = Inches(.85)
for name in ["Normal", "Title", "Heading 1", "Caption"]:
    style = doc.styles[name]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style.font.color.rgb = RGBColor.from_string("000000")
    style.paragraph_format.line_spacing = 1.5
    style.paragraph_format.space_after = Pt(5)
doc.styles["Title"].font.bold = True
for border in doc.styles["Title"].element.xpath(".//w:pBdr"):
    border.getparent().remove(border)
doc.styles["Heading 1"].font.bold = True

def paragraph(content):
    doc.add_paragraph(content)

def heading(content):
    doc.add_heading(content, level=1)

def table(headers, rows):
    grid = doc.add_table(rows=1, cols=len(headers))
    grid.alignment = WD_TABLE_ALIGNMENT.CENTER
    grid.autofit = False
    widths = [1.85, *((6.8 - 1.85) / (len(headers) - 1),) * (len(headers) - 1)]
    for col, width in zip(grid.columns, widths):
        col.width = Inches(width)
    for i, row in enumerate([headers, *rows]):
        cells = grid.rows[0].cells if i == 0 else grid.add_row().cells
        for j, item in enumerate(row):
            cell = cells[j]
            cell.width = Inches(widths[j])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.space_before = Pt(1)
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if j else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(str(item))
            run.bold = i == 0
            if i == 0 or i % 2 == 0:
                shade = OxmlElement("w:shd")
                shade.set(qn("w:fill"), "E3EDF3" if i == 0 else "F2F6F8")
                cell._tc.get_or_add_tcPr().append(shade)
        trpr = grid.rows[i]._tr.get_or_add_trPr()
        trpr.append(OxmlElement("w:cantSplit"))
    return grid

doc.add_paragraph("Part II   Southwest Airlines Valuation", style="Title")
paragraph(
    f"As of {data['asOf']}, the base DCF values Southwest Airlines at ${base:.2f} per share, "
    f"a {metric('DCF upside / downside'):+.1%} difference from the ${market:.2f} close. "
    f"The peer median implies ${peer_mid[4]:.2f} per share. The market price sits "
    f"{price_position(dcf_low, dcf_high)} the DCF sensitivity range and "
    f"{price_position(peer_low[4], peer_high[4])} the peer range."
)
heading("Five-year operating forecast")
paragraph(
    f"We use the trailing twelve months to {data['balanceAsOf']} as the opening annual run rate. "
    f"The five forecast periods end on valuation anniversaries in {data['baseYear']+1}–{data['baseYear']+5}. "
    "Revenue equals available seat miles (ASM) times revenue per ASM. "
    f"ASM growth is {driver('asm_growth', '.1%')}. Unit revenue growth is "
    f"{driver('trasm_growth', '.1%')}, reflecting expected gains from assigned seating, "
    "extra-legroom seats and bag fees."
)
paragraph(
    f"Jet fuel is modeled at {driver('fuel_price', '.2f')} dollars per gallon, "
    "allowing for partial normalization of the fuel shock. Fuel efficiency growth is "
    f"{driver('fuel_efficiency_growth', '.1%')}. Nonfuel cost per ASM growth is "
    f"{driver('nonfuel_casm_growth', '.1%')}, allowing for wage and other cost pressure. "
    f"GAAP operating margin moves from {data['historicalMargin']:.1%} in the TTM to {fcff[10][-1]:.1%} in Year 5."
)
paragraph(
    f"Gross cash capex as a share of sales is {driver('capex_to_sales', '.1%')}. "
    "Management’s 2026 net spending guidance includes proceeds from asset sales and sale-leasebacks. "
    f"Reported-basis D&A as a share of sales is {driver('da_to_sales', '.1%')}. "
    f"Incremental operating working capital is {a['incremental_nwc_to_sales']:.1%} of incremental sales. "
    "Advance ticket payments and seasonality make short-run working capital movements an uncertain guide."
)
table(["USD bn unless shown", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"], [
    ["Revenue", *[f"{n/1000:.2f}" for n in fcff[2]]],
    ["EBIT margin", *[f"{n:.1%}" for n in fcff[10]]],
    ["Gross cash capex", *[f"{n/1000:.2f}" for n in fcff[19]]],
    ["Lease-adjusted FCFF", *[f"{n/1000:.2f}" for n in fcff[21]]],
])

doc.add_page_break()
heading("DCF and peer valuation")
paragraph(
    f"We discount FCFF at Part B’s {rate_grid[3][0]:.2%} WACC using year-end timing and a "
    f"{data['tax']:.1%} marginal tax rate. We add back imputed lease interest after tax, using "
    f"a {a['lease_discount_rate']:.1%} rate on opening operating lease liabilities. Fixed lease cost "
    "less imputed interest proxies for leased-asset amortization. Lease additions replace that amortization "
    "and cover growth in lease balances. Cash capex and lease additions enter as separate investment lines."
)
paragraph(
    f"Terminal growth of {a['terminal_growth']:.2%} and a {a['terminal_roic']:.1%} marginal return on invested "
    f"capital imply that {fcff[26][0]:.1%} of terminal NOPAT is reinvested. Terminal present value is "
    f"{bn(metric('PV of terminal value'))}, or {metric('Terminal value share of EV'):.1%} of enterprise value. "
    f"Explicit FCFF adds {bn(metric('PV of explicit FCFF'))}, for enterprise value of "
    f"{bn(metric('DCF enterprise value'))}. After subtracting {bn(metric('Adjusted net debt'))} in adjusted net debt, "
    f"equity value is {bn(metric('DCF equity value'))}. {data['shares']:,.2f} million shares imply ${base:.2f} per share."
)
paragraph(
    f"The four peers trade at {peer_low[1]:.2f}–{peer_high[1]:.2f}× TTM EBITDAR, with a median of "
    f"{peer_mid[1]:.2f}×. EV includes operating lease liabilities and EBITDAR adds back aircraft rent. "
    f"Applying the peer multiples to LUV’s {bn(peer[4][4])} of TTM EBITDAR gives a range of "
    f"${peer_low[4]:.2f}–${peer_high[4]:.2f} per share. The median implies ${peer_mid[4]:.2f} per share and "
    f"{bn(peer_mid[3])} in equity value, versus {bn(metric('Market equity value'))} in market capitalization. "
    "The median reduces the influence of extreme peer multiples."
)
table(["Multiple", "Delta", "United", "American", "Alaska", "LUV"], [
    ["Market EV / EBITDAR", *[f"{r[5]:.2f}×" for r in peer[:5]]],
])
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(str(chart), width=Inches(6.6))

doc.add_page_break()
heading("Sensitivity and evidence of mispricing")
paragraph(
    f"Across WACC of {rate_grid[1][0]:.2%}–{rate_grid[-1][0]:.2%} and long-run growth of "
    f"{rate_grid[0][1]:.2%}–{rate_grid[0][-1]:.2%}, DCF value ranges from ${dcf_low:.2f} to "
    f"${dcf_high:.2f} per share. Each case recalculates terminal reinvestment. At base growth and "
    f"a {rate_grid[4][0]:.2%} WACC, value is ${rate_grid[4][3]:.2f} per share."
)
grid_headers = ["WACC / growth", *[f"{g:.2%}" for g in rate_grid[0][1:]]]
grid = table(grid_headers, [[f"{r[0]:.2%}", *[f"{x:.2f}" for x in r[1:]]] for r in rate_grid[1:]])
grid.cell(3,3).paragraphs[0].runs[0].bold = True
paragraph(
    f"Moving fuel prices by ${a['fuel_shock_usd_per_gallon']:.2f} per gallon for the first two years "
    f"shifts value by ${abs(base-fuel_cases[-1][4]):.2f} per share in either direction. "
    "The model holds unit revenues, capacity and terminal fuel costs fixed. "
    f"The signed two-year fuel price change needed to match the close is ${data['sensitivity'][13][1]:+.2f} per gallon. "
    "Persistent oil shocks or fare responses could change the result."
)
table(["Two-year fuel case", "Year 1 $/gal", "Year 2 $/gal", "Value $/share", "Vs. close"], [
    [r[0], f"{r[2]:.2f}", f"{r[3]:.2f}", f"{r[4]:.2f}", f"{r[5]:+.1%}"] for r in fuel_cases
])
if price_position(dcf_low, dcf_high) == "within" and price_position(peer_low[4], peer_high[4]) == "within":
    paragraph(
        "Both ranges contain the market price, so the central valuation gap gives limited evidence of mispricing. "
        "The market may price in different fuel costs, commercial execution, capital spending or required returns."
    )
else:
    paragraph(
        "The market-price comparison is conditional on the forecast and peer selection. "
        "Terminal economics and dispersion across peers limit the strength of any inference about mispricing."
    )
paragraph(
    "Sources. Southwest FY2025 Form 10-K, Business, MD&A and Note 7. Southwest Q3 2026 Form 10-Q, MD&A. "
    f"Part A financials and market snapshot, Part B WACC results and Part C assumptions. "
    "Review the operating premises and cited filings before using the model for a new valuation date."
)
doc.save(root / "Part_C_Valuation.docx")
