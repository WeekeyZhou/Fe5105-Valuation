import fs from 'node:fs/promises';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';
const target = process.argv[2];
const {financials, wacc, assumptions: a} = JSON.parse(await fs.readFile(target+'/inputs.json', 'utf8'));
const valuationDate = new Date(wacc.valuation_date+'T00:00:00Z');
const balanceDate = new Date(wacc.debt_date+'T00:00:00Z');
const displayDate = date => date.toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric',timeZone:'UTC'});
const asOf = displayDate(valuationDate);
const balanceAsOf = displayDate(balanceDate);
const baseYear = valuationDate.getUTCFullYear();
const quarter = Math.floor(balanceDate.getUTCMonth()/3)+1;
const ttm = 'TTM_'+balanceDate.getUTCFullYear()+'Q'+quarter;
const bs = 'BS_'+wacc.debt_date;
const market = 'VAL_'+wacc.valuation_date;

function finVal(ticker, period, item, unit='USD mn'){
  const rows=financials.filter(row=>row.ticker===ticker && row.period===period && row.item===item);
  if(rows.length!==1 || rows[0].unit!==unit || !rows[0].value.trim() || !Number.isFinite(Number(rows[0].value))){
    throw new Error(`Missing, duplicate or invalid input: ${ticker} / ${period} / ${item} (${unit})`);
  }
  return Number(rows[0].value);
}
const wb=Workbook.create();
const [sum,forecast,sens,peers,inputs]=['Valuation','FCFF','Sensitivity','Peers','Inputs'].map(n=>wb.worksheets.add(n));
const dark='#17354B', blue='#195DA4', pale='#E8F2F6', green='#D8EBE5';
const money='#,##0.0;(#,##0.0);0.0', price='0.00;(0.00);0.00', pct='0.0%', rate='0.00%';
function v(s,a,x){s.getRange(a).values=[[x]]}
function f(s,a,x){s.getRange(a).formulas=[['='+x]]}
function row(s,n,vals){vals.forEach((x,i)=>typeof x==='string'&&x.startsWith('=')?f(s,String.fromCharCode(65+i)+n,x.slice(1)):v(s,String.fromCharCode(65+i)+n,x))}
function fmt(s,a,n=money){s.getRange(a).setNumberFormat(n)}
function band(s,a){let q=s.getRange(a);q.format.fill=dark;q.format.font.color='#FFFFFF';q.format.font.bold=true;}
function strong(s,a){let q=s.getRange(a);q.format.fill=green;q.format.font.bold=true;}
function editable(s,a){const q=s.getRange(a);q.format.font.color=blue;q.format.fill=pale;}
function frame(s,last,cols,title,subtitle){const area=s.getRange('A1:'+cols+last);area.format.font.name='Arial';area.format.font.size=11;area.format.rowHeight=18;s.getRange('A:A').format.columnWidth=38;s.getRange('B:'+cols).format.columnWidth=15;v(s,'A1',title);band(s,'A1:'+cols+'1');s.getRange('A1:'+cols+'1').format.rowHeight=26;v(s,'A2',subtitle);s.getRange('A2:'+cols+'2').merge();}
frame(inputs,41,'F','LUV historical inputs and forecast assumptions','Blue cells are editable. USD millions, millions of shares, ASM or gallons, unless stated.');
row(inputs,4,['Historical line','FY2023','FY2024','FY2025',ttm]);band(inputs,'A4:E4');
const actualKeys=['revenue','total_opex','fuel_expense','da','capex','operating_income','asm','fuel_gallons','ebitdar'];
const actualLabels=['Revenue','Total operating expense','Aircraft fuel and taxes','D&A','Gross cash capex','GAAP EBIT','Available seat miles','Fuel consumed','EBITDAR'];
actualKeys.forEach((k,i)=>row(inputs,5+i,[actualLabels[i],...['FY2023','FY2024','FY2025',ttm].map(p=>k==='asm'||k==='fuel_gallons' ? (p==='FY2023'?null:finVal('LUV',p,k,k==='asm'?'millions':'million gallons')):finVal('LUV',p,k))]));
fmt(inputs,'B5:E13');editable(inputs,'B5:E13');
row(inputs,15,['Forecast drivers','Year 1','Year 2','Year 3','Year 4','Year 5']);band(inputs,'A15:F15');
const forecastLabels = {
  asm_growth: 'ASM growth',
  trasm_growth: 'TRASM growth',
  fuel_efficiency_growth: 'Fuel efficiency growth',
  fuel_price: 'Fuel price (USD per gallon)',
  nonfuel_casm_growth: 'Nonfuel CASM growth',
  da_to_sales: 'D&A / revenue',
  capex_to_sales: 'Gross cash capex / revenue'
};
const drivers = Object.entries(forecastLabels).map(([key,label])=>[label,...a.forecast[key]]);
drivers.forEach((r,i)=>row(inputs,16+i,r));fmt(inputs,'B16:F22',rate);fmt(inputs,'B19:F19',price);editable(inputs,'B16:F22');
const controls=[
 ['WACC',Number(wacc.wacc)],['Tax rate',Number(wacc.tax_rate)],['Terminal nominal growth',a.terminal_growth],['Terminal marginal ROIC',a.terminal_roic],
 ['Incremental operating NWC / sales',a.incremental_nwc_to_sales],['Operating lease discount rate',a.lease_discount_rate],['Fixed operating lease cost proxy',a.fixed_operating_lease_cost_usd_mn],
 ['Operating lease liabilities',finVal('LUV',bs,'oplease_liab_total')],['Debt incl. finance leases',finVal('LUV',bs,'total_debt')],
 ['Cash and short-term investments',finVal('LUV',bs,'cash_and_sti')],['Shares outstanding (millions)',finVal('LUV',market,'shares_outstanding','million shares')],
 ['Closing price (USD/share)',finVal('LUV',market,'share_price','USD')],['WACC grid step',a.wacc_grid_step],['Terminal growth grid step',a.growth_grid_step],['Fuel shock (USD per gallon)',a.fuel_shock_usd_per_gallon]];
row(inputs,24,['Valuation controls','Value','Source / convention']);band(inputs,'A24:F24');
const sourceNotes=['Part B wacc_results.csv, full precision','Part B normalized marginal rate','Analyst assumption, nominal USD','Analyst assumption, marginal terminal reinvestment','Neutral forecast, excludes seasonal working-capital releases','LUV FY2025 10-K Note 7 weighted-average operating lease rate','FY2025 Note 7, aircraft 291 plus other fixed leases 72',`A financials.csv, ${bs}`,`A financials.csv, ${bs}`,`A financials.csv, ${bs}`,'A financials.csv, shares outstanding',`A financials.csv, close ${asOf}`,'Shared assumptions, approximately ±1 percentage point total','Analyst assumption, ±1 percentage point total','Analyst assumption, two-year shock'];
controls.forEach((r,i)=>{row(inputs,25+i,[...r,sourceNotes[i]]);inputs.getRange('C'+(25+i)+':F'+(25+i)).merge();});
fmt(inputs,'B25:B30',rate);fmt(inputs,'B31:B35');fmt(inputs,'B36:B36',price);fmt(inputs,'B37:B38',rate);fmt(inputs,'B39:B39',price);editable(inputs,'B25:B39');
row(inputs,41,['Historical source']);inputs.getRange('B41:F41').merge();v(inputs,'B41','data/processed/financials.csv, keys and definitions in DATA_DICTIONARY.md');
frame(forecast,34,'F','Five-year FCFF and terminal value',`Five valuation anniversaries. End-year discounting from ${asOf}.`);
row(forecast,4,['USD mn unless stated',...Array.from({length:5},(_,i)=>baseYear+i+1)]);band(forecast,'A4:F4');
const fl=['Available seat miles (millions)','TRASM (USD per ASM)','Revenue','Fuel efficiency (ASM per gallon)','Fuel consumed (million gal)','Fuel price (USD per gallon)','Fuel expense','Nonfuel CASM (USD per ASM)','Nonfuel operating cost','GAAP EBIT','GAAP EBIT margin','Opening operating lease balance','Imputed operating lease interest','Fixed operating lease cost','Lease principal / amort. proxy','Ending operating lease balance','Lease asset additions','Lease-adjusted NOPAT','Reported-basis D&A','Gross cash capex','Change in operating NWC','FCFF before financing','Discount period','Present value of FCFF'];
fl.forEach((x,i)=>v(forecast,'A'+(5+i),x));
for(let i=0;i<5;i++){
 const c='BCDEF'[i],p='ABCDE'[i];
 const q=[
  `${i?p+'5':'Inputs!E11'}*(1+Inputs!${c}16)`,`${i?p+'6':'(Inputs!E5/Inputs!E11)'}*(1+Inputs!${c}17)`,`${c}5*${c}6`,
  `${i?p+'8':'(Inputs!E11/Inputs!E12)'}*(1+Inputs!${c}18)`,`${c}5/${c}8`,`Inputs!${c}19`,`${c}9*${c}10`,
  `${i?p+'12':'((Inputs!E6-Inputs!E7)/Inputs!E11)'}*(1+Inputs!${c}20)`,`${c}12*${c}5`,
  `${c}7-${c}11-${c}13`,`${c}14/${c}7`,i?p+'20':'Inputs!$B$32',`${c}16*Inputs!$B$30`,
  `Inputs!$B$31*${c}5/Inputs!$E$11`,`${c}18-${c}17`,`Inputs!$B$32*${c}5/Inputs!$E$11`,
  `${c}19+${c}20-${c}16`,`(${c}14+${c}17)*(1-Inputs!$B$26)`,`${c}7*Inputs!${c}21`,`${c}7*Inputs!${c}22`,
  `(${c}7-${i?p+'7':'Inputs!E5'})*Inputs!$B$29`,`${c}22+${c}23+${c}19-${c}24-${c}21-${c}25`,String(i+1),`${c}26/(1+Inputs!$B$25)^${c}27`];
 q.forEach((x,j)=>f(forecast,c+(5+j),x));
}
fmt(forecast,'B5:F28');for(const r of [6,12])fmt(forecast,`B${r}:F${r}`,'0.0000');fmt(forecast,'B10:F10',price);fmt(forecast,'B15:F15',pct);fmt(forecast,'B27:F27','0');strong(forecast,'A26:F26');
row(forecast,30,['Terminal year NOPAT','=F22*(1+Inputs!B27)']);
row(forecast,31,['Terminal reinvestment rate','=Inputs!B27/Inputs!B28']);
row(forecast,32,['Terminal year FCFF','=B30*(1-B31)']);
row(forecast,33,['Terminal EV at Year 5','=B32/(Inputs!B25-Inputs!B27)']);
row(forecast,34,['Present value of terminal EV','=B33/(1+Inputs!B25)^F27']);
fmt(forecast,'B30:B34');fmt(forecast,'B31:B31',pct);strong(forecast,'A34:B34');
frame(peers,16,'G','Peer EV / EBITDAR cross-check',`USD millions except multiples and per-share values. Market snapshot ${asOf}.`);
row(peers,4,['Airline','Market cap','Adj. net debt','Market EV','TTM EBITDAR','EV / EBITDAR']);band(peers,'A4:F4');
['DAL','UAL','AAL','ALK','LUV'].forEach((tick,i)=>{const n=i+5;row(peers,n,[tick,finVal(tick,market,'market_cap'),finVal(tick,bs,'adjusted_net_debt'),`=B${n}+C${n}`,finVal(tick,ttm,'ebitdar'),`=D${n}/E${n}`]);});
f(peers,'B9','Inputs!B35*Inputs!B36');f(peers,'C9','Valuation!B9');f(peers,'E9','Inputs!E13');
fmt(peers,'B5:E9');fmt(peers,'F5:F9','0.00"x"');editable(peers,'B5:C8');editable(peers,'E5:E8');
row(peers,11,['Implied LUV valuation','Multiple','Enterprise EV','Equity value','USD/share']);band(peers,'A11:E11');
['MIN','MEDIAN','MAX'].forEach((fn,i)=>{const n=i+12;row(peers,n,[['Peer minimum','Peer median','Peer maximum'][i],`=${fn}(F5:F8)`,`=B${n}*$E$9`,`=C${n}-Valuation!$B$9`,`=D${n}/Inputs!$B$35`]);});
fmt(peers,'B12:B14','0.00"x"');fmt(peers,'C12:D14');fmt(peers,'E12:E14',price);strong(peers,'A13:E13');
peers.getRange('A16:G16').merge();v(peers,'A16',`Source: Part A financials.csv (${ttm}; balance sheets ${balanceAsOf}).`);
frame(sum,17,'E','Southwest Airlines valuation',`USD millions except per-share values. Valuation as of ${asOf}.`);
const outputs=[
 ['Market close (USD/share)','=Inputs!B36'],['Market equity value','=Peers!B9'],['PV of explicit FCFF','=SUM(FCFF!B28:F28)'],
 ['PV of terminal value','=FCFF!B34'],['DCF enterprise value','=B6+B7'],['Adjusted net debt','=Inputs!B32+Inputs!B33-Inputs!B34'],
 ['DCF equity value','=B8-B9'],['DCF value (USD/share)','=B10/Inputs!B35'],['DCF upside / downside','=B11/B4-1'],
 ['Terminal value share of EV','=B7/B8'],['Peer median (USD/share)','=Peers!E13'],['Peer range (USD/share)','=Peers!E12','=Peers!E14'],
 ['DCF WACC × g range (USD/share)','=MIN(Sensitivity!B5:F9)','=MAX(Sensitivity!B5:F9)']];
outputs.forEach((r,i)=>row(sum,4+i,r));fmt(sum,'B4:C16');for(const r of [4,11,14,15,16])fmt(sum,`B${r}:C${r}`,price);fmt(sum,'B12:B13',pct);strong(sum,'A11:B11');strong(sum,'A14:B14');
frame(sens,18,'F','Sensitivity of DCF value per share','Each WACC × growth case recalculates terminal reinvestment. Fuel shock applies to Years 1 and 2.');
v(sens,'A4','WACC / growth');band(sens,'A4:F4');
for(let j=0;j<5;j++){const c='BCDEF'[j];f(sens,c+'4',`Inputs!$B$27+(${j-2})*Inputs!$B$38`);}
for(let i=0;i<5;i++){const r=i+5;f(sens,'A'+r,`Inputs!$B$25+(${i-2})*Inputs!$B$37`);
 for(const c of 'BCDEF'){
  const pv=[...'BCDEF'].map(k=>`FCFF!${k}26/(1+$A${r})^FCFF!${k}27`).join('+');
  f(sens,c+r,`(${pv}+FCFF!$F$22*(1+${c}$4)*(1-${c}$4/Inputs!$B$28)/($A${r}-${c}$4)/(1+$A${r})^FCFF!$F$27-Valuation!$B$9)/Inputs!$B$35`);
 }}
fmt(sens,'B4:F4',rate);fmt(sens,'A5:A9',rate);fmt(sens,'B5:F9',price);strong(sens,'D7');
row(sens,12,['Two-year oil scenario','Shift ($/gal)','Year 1 price','Year 2 price','USD/share','Vs. close']);band(sens,'A12:F12');
for(const [r,label,factor] of [[13,'Lower fuel cost',-1],[14,'Base',0],[15,'Higher fuel cost',1]]){
 row(sens,r,[label,`=${factor}*Inputs!B39`,`=FCFF!B10+B${r}`,`=FCFF!C10+B${r}`,`=Valuation!$B$11-B${r}*(1-Inputs!$B$26)*(FCFF!$B$9/(1+Inputs!$B$25)^FCFF!$B$27+FCFF!$C$9/(1+Inputs!$B$25)^FCFF!$C$27)/Inputs!$B$35`,`=E${r}/Inputs!$B$36-1`]);
}
fmt(sens,'B13:E15',price);fmt(sens,'F13:F15',pct);strong(sens,'A14:F14');
row(sens,17,['Fuel shift to reach market ($/gal)','=IF(Inputs!B39=0,0,(Valuation!B11-Inputs!B36)*Inputs!B39/(E14-E15))']);fmt(sens,'B17:B17',price);
wb.recalculate();
const extract=(s,a)=>s.getRange(a).values;
const results={summary:extract(sum,'A4:C16'),fcff:extract(forecast,'B5:F34'),peer:extract(peers,'A5:F14'),sensitivity:extract(sens,'A4:F17')};
function checkClose(actual, expected){
 if(typeof actual!=='number'||Math.abs(actual-expected)>1e-8) throw Error('Recalculation mismatch '+actual+' vs '+expected);
}
for(const group of Object.values(results)) for(const line of group) for(const entry of line)
 if(typeof entry==='string' && /^#(NUM!|REF!|VALUE!|DIV\/0!|NAME\?|N\/A)/.test(entry)) throw Error(entry);
checkClose(results.summary[7][1],results.sensitivity[3][3]);
checkClose(results.summary[7][1],results.sensitivity[10][4]);
const [year1Fuel,year2Fuel] = a.forecast.fuel_price;
v(inputs,'B19',year1Fuel+a.fuel_shock_usd_per_gallon);
v(inputs,'C19',year2Fuel+a.fuel_shock_usd_per_gallon);
wb.recalculate();
checkClose(extract(sum,'B11')[0][0],results.sensitivity[11][4]);
v(inputs,'B19',year1Fuel);
v(inputs,'C19',year2Fuel);
wb.recalculate();
checkClose(extract(sum,'B11')[0][0],results.summary[7][1]);

const file=await SpreadsheetFile.exportXlsx(wb);
await file.save(target+'/LUV_Valuation_Model.xlsx');
await fs.writeFile(target+'/results.json',JSON.stringify({
  ...results,
  assumptions:a,
  asOf,
  balanceAsOf,
  baseYear,
  tax:Number(wacc.tax_rate),
  shares:finVal('LUV',market,'shares_outstanding','million shares'),
  historicalMargin:finVal('LUV',ttm,'operating_income')/finVal('LUV',ttm,'revenue')
},null,2));
