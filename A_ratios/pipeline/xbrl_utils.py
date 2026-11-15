import re, sys, json
from bs4 import BeautifulSoup
def parse(path):
    s = BeautifulSoup(open(path, encoding='utf-8', errors='ignore').read(), 'lxml')
    ctx = {}
    for c in s.find_all(re.compile(r'xbrli:context', re.I)):
        cid = c.get('id')
        dims = c.find_all(re.compile(r'xbrldi:explicitmember|xbrldi:typedmember', re.I))
        st = c.find(re.compile('xbrli:startdate', re.I)); en = c.find(re.compile('xbrli:enddate', re.I)); ins = c.find(re.compile('xbrli:instant', re.I))
        ctx[cid] = dict(dims=[(d.get('dimension'), d.get_text(strip=True)) for d in dims],
                        start=st.text.strip() if st else None, end=en.text.strip() if en else (ins.text.strip() if ins else None),
                        instant=bool(ins))
    facts = []
    for f in s.find_all(re.compile(r'ix:nonfraction', re.I)):
        c = ctx.get(f.get('contextref'))
        if not c: continue
        txt = f.get_text(strip=True).replace(',', '')
        if f.get('xsi:nil') == 'true': continue
        try: v = float(txt) if txt not in ('', '-', '—', '—') else 0.0
        except: v = 0.0
        v *= 10 ** int(f.get('scale', '0') or 0)
        if f.get('sign') == '-': v = -v
        facts.append(dict(name=f.get('name'), unit=f.get('unitref'), value=v, start=c['start'], end=c['end'],
                          instant=c['instant'], dims=c['dims']))
    return facts

# standard item -> (statement, candidate tags in priority order). 'sum:' means add tags.
G='us-gaap:'
DUR = {  # flow items
 'revenue':            [G+'RevenueFromContractWithCustomerExcludingAssessedTax', G+'Revenues'],
 'passenger_revenue':  [G+'PassengerRevenue'],
 'fuel_expense':       [G+'FuelCosts', G+'AircraftFuelAndRelatedTaxes', 'luv:AircraftFuelAndRelatedTaxes', G+'AircraftFuel'],
 'labor_expense':      [G+'LaborAndRelatedExpense'],
 'aircraft_rent':      [G+'AircraftRental', G+'OperatingLeaseCost'],
 'da':                 [G+'DepreciationDepletionAndAmortization', G+'DepreciationAndAmortization', G+'DepreciationAmortizationAndAccretionNet', G+'CostDepreciationAmortizationAndDepletion'],
 'total_opex':         [G+'OperatingExpenses', G+'OperatingCostsAndExpenses', G+'CostsAndExpenses'],
 'operating_income':   [G+'OperatingIncomeLoss'],
 'interest_expense':   [G+'InterestExpenseNonoperating', G+'InterestExpense', G+'InterestExpenseDebt'],
 'interest_income':    [G+'InvestmentIncomeInterest', G+'InterestIncomeOther', G+'InvestmentIncomeInterestAndDividend'],
 'pretax_income':      [G+'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', G+'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments'],
 'income_tax':         [G+'IncomeTaxExpenseBenefit'],
 'net_income':         [G+'NetIncomeLoss', G+'ProfitLoss'],
 'cfo':                [G+'NetCashProvidedByUsedInOperatingActivities'],
 'capex':              [G+'PaymentsToAcquireProductiveAssets', G+'PaymentsToAcquirePropertyPlantAndEquipment', G+'PaymentsToAcquireFlightEquipment'],
 'cfi':                [G+'NetCashProvidedByUsedInInvestingActivities'],
 'cff':                [G+'NetCashProvidedByUsedInFinancingActivities'],
 'dividends_paid':     [G+'PaymentsOfDividends', G+'PaymentsOfDividendsCommonStock'],
 'buybacks':           [G+'PaymentsForRepurchaseOfCommonStock'],
 'interest_paid':      [G+'InterestPaidNet', G+'InterestPaid'],
}
INST = {  # balance sheet items
 'cash':                 [G+'CashAndCashEquivalentsAtCarryingValue'],
 'st_investments':       [G+'ShortTermInvestments', G+'AvailableForSaleSecuritiesDebtSecuritiesCurrent', G+'MarketableSecuritiesCurrent'],
 'receivables':          [G+'AccountsReceivableNetCurrent', G+'ReceivablesNetCurrent', G+'AccountsNotesAndLoansReceivableNetCurrent', G+'AccountsAndOtherReceivablesNetCurrent'],
 'current_assets':       [G+'AssetsCurrent'],
 'total_assets':         [G+'Assets'],
 'accounts_payable':     [G+'AccountsPayableCurrent', G+'AccountsPayableTradeCurrent'],
 'air_traffic_liability_current': [G+'ContractWithCustomerLiabilityCurrent'],
 'air_traffic_liability_noncurrent': [G+'ContractWithCustomerLiabilityNoncurrent'],
 'current_liabilities':  [G+'LiabilitiesCurrent'],
 'debt_current':         [G+'LongTermDebtAndCapitalLeaseObligationsCurrent', G+'LongTermDebtCurrent', G+'DebtCurrent'],
 'debt_noncurrent':      [G+'LongTermDebtAndCapitalLeaseObligations', G+'LongTermDebtNoncurrent', G+'LongTermDebtAndFinanceLeasesNoncurrent'],
 'finance_lease_liab':   [G+'FinanceLeaseLiability'],
 'oplease_liab_current': [G+'OperatingLeaseLiabilityCurrent'],
 'oplease_liab_noncurrent': [G+'OperatingLeaseLiabilityNoncurrent'],
 'oplease_liab_total':   [G+'OperatingLeaseLiability'],
 'pension_liab_noncurrent': [G+'PensionAndOtherPostretirementAndPostemploymentBenefitPlansLiabilitiesNoncurrent', G+'DefinedBenefitPensionPlanLiabilitiesNoncurrent', G+'LiabilityForFuturePolicyBenefits', G+'OtherPostretirementDefinedBenefitPlanLiabilitiesNoncurrent'],
 'total_liabilities':    [G+'Liabilities'],
 'equity':               [G+'StockholdersEquity', G+'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'],
 'liab_and_equity':      [G+'LiabilitiesAndStockholdersEquity'],
 'inventory':            [G+'InventoryNet', G+'AircraftMaintenanceMaterialsAndRepairs', G+'OtherInventorySupplies'],
}
