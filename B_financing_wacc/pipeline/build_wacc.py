"""Reproduce Part B numerical outputs and report with Python 3 standard library."""
import csv
import hashlib
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parent
DATA = ROOT / 'data/processed/financials.csv'
PARAMS = BASE / 'wacc_inputs.json'
OUT = BASE / 'output'
SOURCES = BASE / 'sources'

def write_csv(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def calculate(debt, equity, rf, erp, bu, tax, spread, shield=None):
    if equity <= 0 or debt < 0:
        raise ValueError('Market equity must be positive; debt must be nonnegative.')
    if not 0 <= tax < 1 or spread < 0:
        raise ValueError('Invalid tax rate or credit spread.')
    wd = debt / (debt + equity)
    beta = bu * (1 + (1-tax)*debt/equity)
    ke = rf + beta*erp
    kd = rf + spread
    cash_shield = tax if shield is None else shield
    return dict(debt_equity_ratio=debt/equity, debt_weight=wd,
                equity_beta=beta, cost_of_equity=ke, pretax_cost_of_debt=kd,
                aftertax_cost_of_debt=kd*(1-cash_shield),
                wacc=(1-wd)*ke + wd*kd*(1-cash_shield))

def main():
    cfg = json.loads(PARAMS.read_text(encoding='utf-8'))
    with DATA.open(encoding='utf-8-sig', newline='') as f:
        data = list(csv.DictReader(f))
    used = {}
    def get(ticker, period, item):
        key = ticker, period, item
        matches = [r for r in data if (r['ticker'],r['period'],r['item']) == key]
        if len(matches) != 1:
            raise ValueError(f'{key}: expected one row, found {len(matches)}')
        row = matches[0]
        if row['unit'] != 'USD mn':
            raise ValueError(f'{key}: unexpected unit {row["unit"]}')
        v = float(row['value'])
        if not math.isfinite(v):
            raise ValueError(f'{key}: nonfinite input')
        used[key] = row
        return v

    c = cfg['common']
    rf, erp, bu, tax = [float(c[k]) for k in ('risk_free_rate','equity_risk_premium','unlevered_beta','tax_rate')]
    if not all(math.isfinite(v) for v in [rf,erp,bu,tax]) or erp < 0 or bu < 0:
        raise ValueError('Invalid market assumptions')
    firms = cfg['companies']
    if len(firms) != 5 or {f['ticker'] for f in firms} != {'LUV','DAL','UAL','AAL','ALK'}:
        raise ValueError('Exactly one input for each of the five airlines is required')
    bs, mv = 'BS_'+cfg['balance_sheet_date'], 'VAL_'+cfg['valuation_date']
    results, financing, sensitivity = [], [], []
    for firm in firms:
        t = firm['ticker']
        d, e = get(t,bs,'adjusted_debt'), get(t,mv,'market_cap')
        debt, leases = get(t,bs,'total_debt'), get(t,bs,'oplease_liab_total')
        if abs(d-debt-leases) > .01:
            raise ValueError(f'{t}: adjusted debt fails reconciliation')
        spread = float(firm['spread'])
        if not math.isfinite(spread):
            raise ValueError(f'{t}: nonfinite credit spread')
        calc = calculate(d,e,rf,erp,bu,tax,spread)
        results.append(dict(ticker=t, valuation_date=cfg['valuation_date'],
            debt_date=cfg['balance_sheet_date'], debt_usd_mn=d,equity_usd_mn=e,
            risk_free_rate=rf,erp=erp,unlevered_beta=bu,tax_rate=tax,
            credit_spread=spread,spread_group=firm['spread_group'], **calc,
            rating=firm['rating'],rating_type=firm['rating_type'],
            rating_evidence_date=firm['source_date'],rating_source=firm['url'],
            spread_source=firm['spread_source_url']))
        financing.append(dict(ticker=t, date=cfg['balance_sheet_date'],
            total_debt_including_finance_leases_usd_mn=debt,
            operating_leases_usd_mn=leases,adjusted_debt_usd_mn=d,
            cash_and_sti_usd_mn=get(t,bs,'cash_and_sti'),
            reported_pension_and_other_benefit_liabilities_usd_mn=get(t,bs,'pension_liab'),
            air_traffic_and_loyalty_liabilities_usd_mn=get(t,bs,'air_traffic_liability_total'),
            financing_sources=firm['financing'],filing=firm['filing_path'],
            locator=firm['filing_locator'],
            treatment='Operating leases included in D once. Pension/benefit and traffic/loyalty liabilities excluded from D; scope differs by issuer.'))
        for name, sp, sh in [('Base',spread,None),('Spread minus 100bp',max(0,spread-.01),None),
                             ('Spread plus 100bp',spread+.01,None),('No immediate debt tax shield',spread,0)]:
            v = calculate(d,e,rf,erp,bu,tax,sp,sh)
            sensitivity.append(dict(ticker=t,scenario=name,credit_spread=sp,
                cash_interest_tax_shield=tax if sh is None else sh,
                wacc=v['wacc'],change_vs_base_bp=(v['wacc']-calc['wacc'])*10000,
                note='Equity beta and Ke held at base for cash-tax-shield scenario; partial sensitivity, not a full repricing.'))

    OUT.mkdir(exist_ok=True)
    SOURCES.mkdir(exist_ok=True)
    write_csv(OUT/'wacc_results.csv',results)
    write_csv(OUT/'financing_leverage.csv',financing)
    write_csv(OUT/'wacc_sensitivity.csv',sensitivity)
    write_csv(SOURCES/'financial_inputs.csv',list(used.values()))
    registry = []
    for key,s in cfg['sources'].items():
        registry.append(dict(source_id=key,data_date=s['date'],locator=s['location'],
            url_or_path=s['url'],treatment=s['note']))
    for f in firms:
        registry.extend([
            dict(source_id=f['ticker']+'_RATING',data_date=f['source_date'],
                locator=f['agency']+' '+f['rating']+'; '+f['rating_type']+'; '+f['location'],
                url_or_path=f['url'],treatment=f['limitation']),
            dict(source_id=f['ticker']+'_FILING',data_date=cfg['balance_sheet_date'],
                locator=f['filing_locator'],url_or_path=f['filing_path'],
                treatment='Source filing retained in the group repository. Monetary inputs inherited from A; exact tags in financial_inputs.csv.')])
    write_csv(SOURCES/'source_register.csv',registry)
    hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [DATA,PARAMS,Path(__file__).resolve()]}
    (SOURCES/'run_manifest.json').write_text(json.dumps(dict(
        valuation_date=cfg['valuation_date'],accessed_date=cfg['accessed_date'],
        sha256=hashes),indent=2)+'\n',encoding='utf-8')

    table = ['| Firm | D / E | Equity beta | Ke | Kd before tax | WACC |',
             '|---|---:|---:|---:|---:|---:|']
    for r in results:
        table.append(f"| {r['ticker']} | {r['debt_equity_ratio']:.2f} | {r['equity_beta']:.4f} | {r['cost_of_equity']:.2%} | {r['pretax_cost_of_debt']:.2%} | {r['wacc']:.2%} |")
    luv = next(r for r in results if r['ticker']=='LUV')
    lf = next(r for r in financing if r['ticker']=='LUV')
    hid = ['| Firm | Operating leases | Benefit liabilities | Traffic / loyalty liabilities |',
           '|---|---:|---:|---:|']
    for r in financing:
        hid.append(f"| {r['ticker']} | {r['operating_leases_usd_mn']:,.0f} | {r['reported_pension_and_other_benefit_liabilities_usd_mn']:,.0f} | {r['air_traffic_and_loyalty_liabilities_usd_mn']:,.0f} |")
    report = f'''# Financing and cost of capital

## Financing and supplementary obligations

LUV primarily combines unsecured borrowing with aircraft leases and sale-and-leasebacks. DAL uses unsecured and aircraft-secured debt together with SkyMiles-backed financing. UAL combines senior notes and term borrowing with aircraft and route/slot/gate financing. AAL relies heavily on EETCs, equipment loans and AAdvantage-backed borrowing. ALK combines aircraft financing, loyalty-backed debt, unsecured notes and government support programme notes. Revolving facilities support liquidity; undrawn capacity is not outstanding debt. [1]

Operating leases create fixed payments and are included once in adjusted debt. Pension and other benefit obligations constrain future cash flows but remain outside WACC debt under the group convention. The reported benefit-liability amounts have different scopes across issuers; they are not comparable measures of total net pension deficits. Traffic and loyalty liabilities are service obligations, not conventional borrowing, although cash received in advance exposes airlines to redemption and refund demands. Loans secured by loyalty assets are separately recorded as debt. [1]

USD millions, {cfg['balance_sheet_date']}:

{chr(10).join(hid)}

## Cost of capital

The valuation date is {cfg['valuation_date']}. Following A's common dataset, D is September adjusted book debt, including finance and operating leases, and E is November market capitalisation. Book debt approximates market debt; cash is not deducted in WACC weights. Intervening debt transactions are not rolled forward. [1]

CAPM uses a {rf:.2%} 10-year Treasury proxy, {erp:.2%} implied equity risk premium and {bu:.2f} industry unlevered beta. The beta is the US Air Transport estimate, without cash correction. B selects a normalised marginal tax rate of {tax:.0%}; this is a modelling assumption, not the reported effective tax rate of each airline. State-tax reconciliation entries support review but do not directly identify marginal tax rates. [2–4]

βL = βU × [1 + (1 − T) × D/E]; Ke = Rf + βL × ERP.

Kd = Rf + rating-group spread; WACC = E/(D+E) × Ke + D/(D+E) × Kd × (1−T).

Broad BBB, BB and B credit spreads are respectively 1.11%, 1.86% and 3.44%. LUV and DAL use BBB proxies, UAL and ALK BB, and AAL B. The source register identifies each rating's agency, date and whether it is issuer-level or issue-level evidence. [5–6]

{chr(10).join(table)}

These are retrospective estimates. November 13 FRED observations were published November 16. Index option-adjusted spreads plus a 10-year yield approximate financing costs rather than company bond yields. Dated ratings are not continuous rating verification; broad groups suppress notch and security differences. CAPM assumes negligible debt beta, especially restrictive for AAL. Tax shields require usable deductions. Lower WACC therefore does not imply lower financial risk.

## LUV capital structure recommendation

LUV's debt weight is {luv['debt_weight']:.1%}, with adjusted debt of ${luv['debt_usd_mn']:,.0f} million and cash plus short-term investments of ${lf['cash_and_sti_usd_mn']:,.0f} million. Its lower market leverage relative to UAL, AAL and ALK gives financing flexibility. It does not establish an optimal borrowing target. Aircraft commitments, demand volatility and fixed lease payments argue for preserving liquidity and investment-grade access before funding additional distributions with debt.

Retain moderate leverage and use internal cash generation first for committed investment. Match long-lived aircraft with suitable financing maturities and compare leases with borrowing on an after-tax present-value basis. Additional debt can create tax benefits, but higher spreads and distress costs may offset them. Do not infer an optimum by holding Kd and Ke fixed while increasing debt weights. Coordinate any borrowing or buyback decision with D's liquidity stress test.

For C, the LUV base WACC is {luv['wacc']:.2%}. Test roughly {luv['wacc']-.01:.2%}–{luv['wacc']+.01:.2%} alongside terminal growth; this is a modelling range, not a statistical confidence interval. The accompanying sensitivity table separately isolates spread changes and loss of an immediate debt tax shield. FCFF must be consistent with leases treated as debt: reflect the after-tax lease-interest addback and leased-asset reinvestment, then subtract lease liabilities once in the equity bridge.

## Sources

[1] A's `data/processed/financials.csv`; five Q3 2026 Forms 10-Q in `data/raw/html/`. Exact row sources and tags: `sources/financial_inputs.csv`.

[2] [US Treasury, 13 November 2026, 10 Yr](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202611&type=daily_treasury_yield_curve).

[3] [Damodaran implied ERP, 1 November 2026](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/home.htm), trailing 12 months with adjusted payout.

[4] [Damodaran US sector betas, January 2026](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/Betas.html), Air Transport, unlevered beta. Tax assumption: B; supporting company tax-note screenshots retained in `sources/tax/`.

[5] ICE BofA OAS via FRED, 13 November 2026: [BBB](https://fred.stlouisfed.org/series/BAMLC0A4CBBB), [BB](https://fred.stlouisfed.org/series/BAMLH0A1HYBB), [B](https://fred.stlouisfed.org/series/BAMLH0A2HYB).

[6] Dated company/agency rating evidence and financing-note locators: `sources/source_register.csv`. Sources accessed {cfg['accessed_date']}.
'''
    (OUT/'report.md').write_text(report,encoding='utf-8')
    (OUT/'shared_assumptions.md').write_text(f'''# Part B — shared cost-of-capital assumptions

Valuation date: {cfg['valuation_date']}. Debt date: {cfg['balance_sheet_date']}.
All monetary inputs use A's common data and USD millions.

| Input | Selected value |
|---|---:|
| Treasury proxy | {rf:.2%} |
| Equity risk premium | {erp:.2%} |
| Industry unlevered beta | {bu:.2f} |
| Normalised marginal tax rate | {tax:.0%} |

{chr(10).join(table)}

Tax is B's selected base case, not a statement of team approval. D includes
finance leases and operating leases once. Market equity, not book equity, is
used in D/E. AAL's negative book equity does not invalidate this market D/E.
Cash is not netted from WACC debt. Pension/benefit and traffic/loyalty obligations
remain outside D. Lease financing uses the same Kd and tax treatment as debt.

C should use LUV WACC {luv['wacc']:.2%}, with a ±1 percentage-point sensitivity
and lease-consistent FCFF and equity bridge. The range is not a confidence interval.

Sources, evidence dates and limitations: `B_financing_wacc/output/report.md`
and `B_financing_wacc/sources/source_register.csv`.

Integrate these values into the cost-of-capital section of shared/assumptions.md
after notifying the group; retain the other existing shared conventions.
''',encoding='utf-8')
    print('Firm     Beta       Ke       Kd     WACC')
    for r in results:
        print(f"{r['ticker']:<5} {r['equity_beta']:>7.4f} {r['cost_of_equity']:>8.2%} {r['pretax_cost_of_debt']:>8.2%} {r['wacc']:>8.2%}")
    print('Rebuilt CSV, Markdown and source manifest. Excel companion is a separately editable input snapshot.')

if __name__ == '__main__':
    main()
