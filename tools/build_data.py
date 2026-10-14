"""Export aggregate-only, country-sharded results for the REACH static site.
Usage: python tools/build_data.py --db responses.sqlite --followup FollowupData --reference metrics_common.csv
Requires numpy and pandas. Never alters the input database or files.
"""
import argparse,hashlib,itertools,json,sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parents[1]; OUT=(P/'site/data') if (P/'site').is_dir() else (P/'data')
a=argparse.ArgumentParser();a.add_argument('--db',required=True);a.add_argument('--followup',required=True);a.add_argument('--reference',required=True);args=a.parse_args()
(P/'validation').mkdir(exist_ok=True)
(P/'validation').mkdir(exist_ok=True)
con=sqlite3.connect('file:'+str(Path(args.db).resolve())+'?mode=ro',uri=True)
m=json.loads(con.execute("SELECT value FROM metadata WHERE key='catalog'").fetchone()[0]); OUT.mkdir(parents=True,exist_ok=True)
qs=m['questions']; labels=['Unentitled benefits','Fare evasion','Tax cheating','Accepting bribes','Homosexuality','Prostitution','Abortion','Divorce','Suicide','Euthanasia','Casual sex','Death penalty','Public video surveillance','Internet/email monitoring','Personal-data collection']
cats=['Dishonesty & corruption','Sexual & family norms','Life ethics','Surveillance & privacy']; cmap={'부정행위·부패':0,'성·가족 규범':1,'생명 윤리':2,'감시·프라이버시':3}
zones={'Protestant Europe':'Germany|Netherlands|Sweden|Iceland','Catholic Europe':'France|Lithuania|Czechia|Poland','English-speaking':'United States|Great Britain|Australia|New Zealand','Confucian':'Japan|South Korea|China|Mongolia','West & South Asia':'India|Vietnam','Orthodox Europe':'Bulgaria|Ukraine|Georgia|Montenegro','African-Islamic':'Albania|Turkey|Zimbabwe','Latin America':'Uruguay|Puerto Rico|Nicaragua'}
zone={c:z for z,cs in zones.items() for c in cs.split('|')}
cs=sorted(x['id'] for x in m['countries']);codes={c:c.lower().replace(' ','-') for c in cs}
questions=[{'id':q['id'],'label':labels[i],'category':cmap[q['category']],'maximum':q['maximum'],'wording':q['english'],'wvs':q['wvs'],'evs':q['evs']} for i,q in enumerate(qs)]
meta={'version':'2026-10-14','snapshot':m['built_at'],'fingerprint':m['fingerprint'],'humanN':m['human_n'],'llmN':m['synthetic_n'],'models':[{**v,'temperature':1 if 'luna' in v['id'] else .3} for v in m['models']],'countries':[{'name':c,'file':codes[c],'zone':zone[c],**{k:v for k,v in next(s for s in m['human_sources'] if s['country']==c).items() if k in ['source','years','weight','n']}} for c in cs],'questions':questions,'categories':cats,'minimumN':50,'minimumEffectiveN':30}
# Item record = [valid n, effective n, probabilities]; omitted PMF means insufficient public reporting sample.
def aggregate(arr,weights=None):
 result=[]
 for i,q in enumerate(qs):
  x=arr[:,i];k=q['maximum'];ok=np.isfinite(x)&(x>=1)&(x<=k)&(x==np.floor(x))
  if weights is not None:ok &= np.isfinite(weights)&(weights>0)
  v=x[ok].astype(int);w=np.ones(len(v)) if weights is None else weights[ok];n=len(v);eff=float(w.sum()**2/(w@w)) if n else 0
  if n<50 or eff<30:result.append([n,round(eff,4)]);continue
  probs=np.bincount(v,weights=w,minlength=k+1)[1:]/w.sum()
  result.append([n,round(eff,4),*[round(float(x),10) for x in probs]])
 return result
combos=list(itertools.product(range(4),range(3),range(4),range(4)))
def masks(a):
 age,g,p,r=a.T;n=len(a)
 return [[np.ones(n,dtype=bool),(age>=18)&(age<=34),(age>=35)&(age<=54),(age>=55)&(age<=120)], [np.ones(n,dtype=bool),g==1,g==2], [np.ones(n,dtype=bool),(p>=1)&(p<=3),(p>=4)&(p<=7),(p>=8)&(p<=10)], [np.ones(n,dtype=bool),r==1,r==2,r==3]]
columns=','.join('r'+str(i) for i in range(15)); ref=pd.read_csv(args.reference);errs=[];checks=[];eligible=0
for c in cs:
 h=np.asarray(con.execute('SELECT age,gender,politics,religion,weight,'+columns+' FROM human WHERE country=?',(c,)).fetchall(),dtype=float)
 datasets=[h]+[np.asarray(con.execute('SELECT age,gender,politics,religion,1,'+columns+' FROM synthetic WHERE run=?',(con.execute('SELECT id FROM runs WHERE country=? AND model=?',(c,md['id'])).fetchone()[0],)).fetchall(),dtype=float) for md in m['models']]
 mm=[masks(d[:,:4]) for d in datasets]; payload={}
 for combo in combos:
  subset=[d[np.logical_and.reduce([ms[j][idx] for j,idx in enumerate(combo)])] for d,ms in zip(datasets,mm)]
  payload[''.join(map(str,combo))]={'h':{'w':aggregate(subset[0][:,5:],subset[0][:,4]),'u':aggregate(subset[0][:,5:])},'m':[aggregate(d[:,5:]) for d in subset[1:]]}
 for mi,md in enumerate(m['models']):
  for qi,q in enumerate(qs):
   hrow=payload['0000']['h']['w'][qi];lrow=payload['0000']['m'][mi][qi];hp=np.array(hrow[2:]);lp=np.array(lrow[2:]);k=q['maximum'];x=np.arange(1,k+1)
   def stat(p):
    mean=p@x;return mean,np.sqrt(p@((x-mean)**2)),-sum(p[p>0]*np.log2(p[p>0]))
   hv=stat(hp);lv=stat(lp);w1=np.abs(np.cumsum(lp-hp)[:-1]).sum()/(k-1)
   rr=ref[(ref.country==c)&(ref.model==md['id'])&(ref.topic==q['id'])].iloc[0]
   e=max(abs(w1-rr.w1_norm),*[abs(v-rr[col]) for v,col in zip(hv,['human_mean','human_sd','human_entropy'])],*[abs(v-rr[col]) for v,col in zip(lv,['model_mean','model_sd','model_entropy'])]);errs.append(e)
 OUT.joinpath(codes[c]+'.js').write_text('window.REACH_COUNTRIES=window.REACH_COUNTRIES||{};window.REACH_COUNTRIES['+json.dumps(c)+']='+json.dumps(payload,separators=(',',':'),allow_nan=False)+';\n')
 eligible+=sum(1 for r in payload.values() if any(len(x)>2 for x in r['h']['w']))
 print(c,'exported',flush=True)
# Remove obsolete earlier approaches; keep current REACH-adj identity explicit.
f=Path(args.followup);matched=pd.read_csv(f/'matched_gpt_methods.csv');matchids={'direct':'Direct','vs':'VS','voyager':'VOYAGER (adapted)','author_regression':'Supervised regression','human_empirical':'Human empirical','exact_ot':'National OT','group_ot_anchored':'REACH-adj'}
matched=matched[matched.method.isin(matchids)].copy();matched['label']=matched.method.map(matchids)
budget=pd.read_csv(f/'budget_summary.csv').rename(columns={'budget':'sampleSize'});contrast=pd.read_csv(f/'contrast_summary.csv').rename(columns={'budget':'sampleSize'})
follow={'matched':matched.to_dict('records'),'sampleSize':budget.to_dict('records'),'contrast':contrast.to_dict('records')}
OUT.joinpath('catalog.js').write_text('window.REACH_META='+json.dumps(meta,separators=(',',':'),ensure_ascii=True)+';\nwindow.REACH_FOLLOWUP='+json.dumps(follow,separators=(',',':'),allow_nan=False)+';\n')
assert len(errs)==2100 and max(errs)<1e-6,max(errs)
report={'passed':True,'country_item_model_checks':len(errs),'max_abs_metric_difference':max(errs),'countries':28,'filter_combinations_per_country':len(combos),'eligible_human_cohorts':eligible,'source_database_sha256':hashlib.sha256(Path(args.db).read_bytes()).hexdigest(),'release':'Aggregates only; no respondent records, profile identifiers, local file paths or credentials','thresholds':{'valid_n':50,'effective_n':30},'source_snapshot':m['built_at']}
P.joinpath('validation/data_checks.json').write_text(json.dumps(report,indent=2));print(report)
