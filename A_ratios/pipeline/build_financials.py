"""
FE5105 group project — Member A data pipeline.
Builds data/processed/financials.csv from the inline-XBRL 10-K (FY2025) and 10-Q (Q3 2026)
HTML filings in data/raw/html, plus data/raw/market_data_2026-11-13.csv.
Run from anywhere:  python A_ratios/pipeline/build_financials.py
Requires: beautifulsoup4, lxml, openpyxl
"""
import os, sys, csv, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
RAW = os.path.join(ROOT, 'data', 'raw'); OUT = os.path.join(ROOT, 'data', 'processed')
sys.path.insert(0, HERE)
from xbrl_utils import parse, DUR, INST
G='us-gaap:'
FNAME = {'10K': '{t}_10K_FY2025.htm', '10Q': '{t}_10Q_Q3_2026.htm'}
D = {t: {k: parse(os.path.join(RAW, 'html', FNAME[k].format(t=t))) for k in ('10K', '10Q')} for t in ['LUV','DAL','UAL','AAL','ALK']}
TICK = ['LUV','DAL','UAL','AAL','ALK']
SRC = {'10K':'10-K FY2025 (iXBRL)', '10Q':'10-Q Q3 2026 (iXBRL)'}
# periods: name -> (file, start, end)
FLOW_P = {'FY2023':('10K','2023-01-01','2023-12-31'), 'FY2024':('10K','2024-01-01','2024-12-31'),
          'FY2025':('10K','2025-01-01','2025-12-31'), '9M2025':('10Q','2025-01-01','2025-09-30'),
          '9M2026':('10Q','2026-01-01','2026-09-30'), 'Q3_2025':('10Q','2025-07-01','2025-09-30'),
          'Q3_2026':('10Q','2026-07-01','2026-09-30')}
BS_P = {'BS_2024-12-31':('10K','2024-12-31'), 'BS_2025-12-31':('10K','2025-12-31'), 'BS_2026-09-30':('10Q','2026-09-30')}
DUR = dict(DUR); INST = dict(INST)
DUR['receivables'] = None
INST['receivables'] = [G+'AccountsAndOtherReceivablesNetCurrent', G+'ReceivablesNetCurrent', G+'AccountsReceivableNetCurrent']
DUR.pop('receivables')
INST['cash'] = [G+'CashAndCashEquivalentsAtCarryingValue', G+'Cash']
INST['pension_liab'] = [G+'PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent', G+'PensionAndOtherPostretirementAndPostemploymentBenefitPlansLiabilitiesNoncurrent', G+'PensionAndOtherPostretirementAndPostemploymentBenefitPlansLiabilitiesCurrentAndNoncurrent']
for k in ['pension_liab_noncurrent','total_liabilities','inventory','air_traffic_liability_current','air_traffic_liability_noncurrent','oplease_liab_total']: INST.pop(k, None)
DUR.pop('passenger_revenue', None)

def find(fs, tag, start, end, instant, dims=()):
    for f in fs:
        if f['name']==tag and f['end']==end and tuple(sorted(d[1] for d in f['dims']))==tuple(sorted(dims)):
            if instant and f['instant']: return f['value']/1e6
            if not instant and f['start']==start: return f['value']/1e6
    return None

rows=[]
def add(t,p,item,v,src,note=''):
    rows.append(dict(ticker=t, period=p, item=item, value=None if v is None else round(v,3), unit='USD mn', source=src, note=note))

for t in TICK:
    for p,(fk,s,e) in FLOW_P.items():
        fs = D[t][fk]
        for item,tags in DUR.items():
            v=None; used=None
            for tag in tags:
                v=find(fs,tag,s,e,False)
                if v is not None: used=tag; break
            note=''
            if item=='capex' and v is None:
                comps=[G+'PaymentsForFlightEquipment',G+'PaymentsToAcquireOtherProductiveAssets',G+'PaymentsToAcquireOtherPropertyPlantAndEquipment',G+'PaymentsToAcquirePropertyPlantAndEquipment']
                vals=[find(fs,c,s,e,False) for c in comps]
                if any(x is not None for x in vals): v=sum(x or 0 for x in vals); used='sum of '+'+'.join(c.split(':')[1] for c,x in zip(comps,vals) if x is not None)
            if item=='aircraft_rent' and v is None:
                v=find(fs,G+'OperatingLeaseCost',s,e,False,dims=('us-gaap:AirTransportationEquipmentMember',))
                if v is not None: used='OperatingLeaseCost[AirTransportationEquipment] (lease note)'
            if item=='interest_expense' and v is None and t=='DAL':
                nv=find(fs,G+'InterestIncomeExpenseNonoperatingNet',s,e,False)
                if nv is not None: add(t,p,'interest_expense_net',-nv,SRC[fk]+' InterestIncomeExpenseNonoperatingNet','Delta reports interest expense net of interest income only')
                continue
            if item in ('dividends_paid','buybacks') and v is None:
                v=0.0; used=None; note='tag not reported in filing; assumed 0'
            if item=='interest_income' and v is None and t=='DAL': continue
            if v is None: continue
            add(t,p,item,v,SRC[fk]+(' '+used.split(':')[-1] if used and ':' in used else (' '+used if used else '')),note)
        if t=='DAL':
            v=find(fs,G+'RevenueFromContractWithCustomerExcludingAssessedTax',s,e,False,dims=('dal:ProductAndServiceOtherRefineryMember',))
            if v is None:
                # dimension member name may differ; search
                for f in fs:
                    if f['name']==G+'RevenueFromContractWithCustomerExcludingAssessedTax' and f['start']==s and f['end']==e and len(f['dims'])==1 and 'Refinery' in f['dims'][0][1] and 'ProductAndService' in f['dims'][0][1]:
                        v=f['value']/1e6; break
            if v is not None: add(t,p,'refinery_sales_third_party',v,SRC[fk]+' revenue[Refinery product member]','Delta: exclude from revenue AND opex for airline-only TRASM/CASM')
    for p,(fk,e) in BS_P.items():
        fs=D[t][fk]
        for item,tags in INST.items():
            v=None; used=None
            for tag in tags:
                v=find(fs,tag,None,e,True)
                if v is not None: used=tag; break
            note=''
            if item=='st_investments' and v is None: v=0.0; note='no short-term investments line on balance sheet; set to 0'
            if v is None: continue
            add(t,p,item,v,SRC[fk]+(' '+used.split(':')[-1] if used else ''),note)
        # air traffic liability total (current + noncurrent, incl. loyalty)
        v=find(fs,G+'ContractWithCustomerLiability',None,e,True)
        note='ContractWithCustomerLiability (total)'
        if v is None and t=='UAL':
            tags=['ContractWithCustomerLiabilityCurrentAdvanceTicketSales','ContractWithCustomerLiabilityCurrentFrequentFlyer','ContractWithCustomerLiabilityNoncurrentFrequentFlyer']
            vals=[find(fs,'ual:'+x,None,e,True) for x in tags]
            if all(x is not None for x in vals): v=sum(vals); note='advance ticket sales + frequent flyer current + noncurrent'
        if v is None:
            mem={}
            for f in fs:
                if f['end']==e and f['instant'] and len(f['dims'])==1 and 'LegalEntity' not in f['dims'][0][0] and f['name'] in (G+'ContractWithCustomerLiability',G+'ContractWithCustomerLiabilityCurrent',G+'ContractWithCustomerLiabilityNoncurrent'):
                    mem.setdefault(f['dims'][0][1],{})[f['name'].split(':')[1]]=f['value']/1e6
            if mem:
                v=sum(d.get('ContractWithCustomerLiability', d.get('ContractWithCustomerLiabilityCurrent',0)+d.get('ContractWithCustomerLiabilityNoncurrent',0)) for d in mem.values())
                note='sum by member: '+', '.join(k.split(':')[-1] for k in mem)
            else:
                tags=['ContractWithCustomerLiabilityCurrentAdvanceTicketSales','ContractWithCustomerLiabilityCurrentFrequentFlyer','ContractWithCustomerLiabilityNoncurrentFrequentFlyer']
                vals=[find(fs,'ual:'+x,None,e,True) or find(fs,G+x,None,e,True) for x in tags]
                if any(x is not None for x in vals): v=sum(x or 0 for x in vals); note='advance ticket sales + frequent flyer current + noncurrent'
        if v is not None: add(t,p,'air_traffic_liability_total',v,SRC[fk],note+'; operating liability, NOT treated as debt')

# Southwest TTM/9M aircraft rent not disclosed quarterly
OPS = {  # asm, rpm, fuel_gallons (millions); source tables in data/raw extracted xlsx
 'LUV': {'FY2024':(177250,142515,2194),'FY2025':(180046,139443,2169),'9M2025':(133994,103875,1624),'9M2026':(134535,104711,1607),'Q3_2025':(45567,36362,554),'Q3_2026':(45393,36214,548)},
 'DAL': {'FY2024':(288394,246145,4114),'FY2025':(298045,249578,4269),'9M2025':(225099,189717,3226),'9M2026':(227145,191369,3256),'Q3_2025':(79054,67621,1138),'Q3_2026':(79288,68133,1146)},
 'UAL': {'FY2023':(291333,244435,4205),'FY2024':(311185,258503,4444),'FY2025':(330284,271619,4663),'9M2025':(246919,203374,3488),'9M2026':(253516,210428,3555),'Q3_2025':(87417,73769,1233),'Q3_2026':(88538,74278,1243)},
 'AAL': {'FY2024':(292948,248795,4391),'FY2025':(299411,250294,4488),'9M2025':(224939,188698,3375),'9M2026':(234533,193934,3473),'Q3_2025':(77400,66580,1169),'Q3_2026':(80680,67265,1204)},
 'ALK': {'FY2024':(76167,63871,925),'FY2025':(92962,77110,1146),'9M2025':(69724,58174,859),'9M2026':(70907,58045,870),'Q3_2025':(24447,20739,303),'Q3_2026':(25031,20733,308)},
}
OPS_SRC = {'FY2023':'10-K FY2025 MD&A operating statistics','FY2024':'10-K FY2025 MD&A operating statistics','FY2025':'10-K FY2025 MD&A operating statistics','9M2025':'10-Q Q3 2026 MD&A operating statistics','9M2026':'10-Q Q3 2026 MD&A operating statistics','Q3_2025':'10-Q Q3 2026 MD&A operating statistics','Q3_2026':'10-Q Q3 2026 MD&A operating statistics'}
for t,d in OPS.items():
    for p,(a,r,g) in d.items():
        n = 'ALK FY2024 as reported: includes Hawaiian only from 2024-09-18' if (t=='ALK' and p=='FY2024') else ''
        for item,v in (('asm',a),('rpm',r),('fuel_gallons',g)):
            rows.append(dict(ticker=t,period=p,item=item,value=v,unit='millions' if item!='fuel_gallons' else 'million gallons',source=OPS_SRC[p],note=n))

# TTM
import collections
idx=collections.defaultdict(dict)
for r in rows: idx[(r['ticker'],r['item'])][r['period']]=r
flow_items=set(list(DUR.keys())+['interest_expense_net','refinery_sales_third_party','asm','rpm','fuel_gallons'])
for (t,item),pp in list(idx.items()):
    if item not in flow_items: continue
    if all(k in pp and pp[k]['value'] is not None for k in ('FY2025','9M2026','9M2025')):
        v=pp['FY2025']['value']+pp['9M2026']['value']-pp['9M2025']['value']
        rows.append(dict(ticker=t,period='TTM_2026Q3',item=item,value=round(v,3),unit=pp['FY2025']['unit'],source='derived: FY2025 + 9M2026 - 9M2025',note=''))
    elif item=='aircraft_rent' and 'FY2025' in pp:
        rows.append(dict(ticker=t,period='TTM_2026Q3',item=item,value=pp['FY2025']['value'],unit='USD mn',source='derived: FY2025 value carried forward',note='not disclosed in 10-Q; TTM assumed equal to FY2025'))

# ---------------- derived items, market data, checks ----------------
V=collections.defaultdict(dict)
for r in rows: V[(r['ticker'],r['period'])][r['item']]=r['value']
def add(t,p,item,v,src,note='',unit='USD mn'):
    rows.append(dict(ticker=t,period=p,item=item,value=None if v is None else round(v,3),unit=unit,source=src,note=note)); V[(t,p)][item]=v
for (t,p),d in list(V.items()):
    if p.startswith('BS_'):
        if {'debt_current','debt_noncurrent'}<=d.keys(): add(t,p,'total_debt',d['debt_current']+d['debt_noncurrent'],'derived: debt_current + debt_noncurrent','includes finance leases (and UAL other financial liabilities) as presented on balance sheet')
        if {'oplease_liab_current','oplease_liab_noncurrent'}<=d.keys(): add(t,p,'oplease_liab_total',d['oplease_liab_current']+d['oplease_liab_noncurrent'],'derived: current + noncurrent')
        d=V[(t,p)]
        if {'total_debt','oplease_liab_total'}<=d.keys(): add(t,p,'adjusted_debt',d['total_debt']+d['oplease_liab_total'],'derived: total_debt + oplease_liab_total','group definition: debt + finance leases + operating lease liabilities (ASC 842)')
        if {'cash','st_investments'}<=d.keys(): add(t,p,'cash_and_sti',d['cash']+d['st_investments'],'derived: cash + st_investments')
        d=V[(t,p)]
        if {'adjusted_debt','cash_and_sti'}<=d.keys(): add(t,p,'adjusted_net_debt',d['adjusted_debt']-d['cash_and_sti'],'derived: adjusted_debt - cash_and_sti')
        if {'liab_and_equity','equity'}<=d.keys(): add(t,p,'total_liabilities',d['liab_and_equity']-d['equity'],'derived: liab_and_equity - equity')
    else:
        if {'operating_income','da'}<=d.keys(): add(t,p,'ebitda',d['operating_income']+d['da'],'derived: operating_income + da')
        d=V[(t,p)]
        if {'ebitda','aircraft_rent'}<=d.keys(): add(t,p,'ebitdar',d['ebitda']+d['aircraft_rent'],'derived: ebitda + aircraft_rent')
        if t!='DAL' and {'interest_expense','interest_income'}<=d.keys(): add(t,p,'interest_expense_net',d['interest_expense']-d['interest_income'],'derived: interest_expense - interest_income')
        if {'cfo','capex'}<=d.keys(): add(t,p,'free_cash_flow',d['cfo']-d['capex'],'derived: cfo - capex')
        if 'revenue' in d:
            ref=d.get('refinery_sales_third_party',0) if t=='DAL' else 0
            add(t,p,'revenue_airline',d['revenue']-ref,'derived: revenue - third-party refinery sales (DAL only)')
            if 'total_opex' in d: add(t,p,'total_opex_airline',d['total_opex']-ref,'derived: total_opex - third-party refinery sales (DAL only)')
# market data at valuation date
mk={r['ticker']:r for r in csv.DictReader(open(os.path.join(RAW,'market_data_2026-11-13.csv')))}
for t,m in mk.items():
    P='VAL_2026-11-13'
    add(t,P,'share_price',float(m['close_price_2026-11-13']),'close 2026-11-13: '+m['price_source'],unit='USD')
    add(t,P,'shares_outstanding',int(m['shares_outstanding'])/1e6,f"10-Q Q3 2026 cover page (as of {m['shares_as_of']})",unit='million shares')
    mc=int(m['shares_outstanding'])*float(m['close_price_2026-11-13'])/1e6
    add(t,P,'market_cap',mc,'derived: share_price x shares_outstanding')
    nd=V[(t,'BS_2026-09-30')].get('adjusted_net_debt')
    if nd is not None: add(t,P,'enterprise_value',mc+nd,'derived: market_cap + adjusted_net_debt at 2026-09-30','balance sheet at latest 10-Q; market cap at valuation date')
# validation
chk=[]
for (t,p),d in V.items():
    if p.startswith('BS_') and {'total_assets','liab_and_equity'}<=d.keys(): chk.append((t,p,'assets = liabilities + equity',d['total_assets'],d['liab_and_equity']))
    if not p.startswith(('BS_','VAL_')) and {'revenue','total_opex','operating_income'}<=d.keys(): chk.append((t,p,'revenue - opex = operating income',d['revenue']-d['total_opex'],d['operating_income']))
    if not p.startswith(('BS_','VAL_')) and {'pretax_income','income_tax','net_income'}<=d.keys(): chk.append((t,p,'pretax - tax = net income',d['pretax_income']-d['income_tax'],d['net_income']))
bad=[c for c in chk if abs(c[3]-c[4])>1.01]
print('checks',len(chk),'failures',len(bad)); [print(b) for b in bad]

import write_outputs; write_outputs.write(rows, V, chk, OUT)
