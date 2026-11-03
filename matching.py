from difflib import SequenceMatcher
from datetime import date

def explain_match(a: dict,b: dict) -> dict:
    if a.get('type')==b.get('type'): return {'score':0,'reasons':['Reports must be opposite types.']}
    cat=1.0 if a.get('category','').casefold()==b.get('category','').casefold() else 0.0
    name=SequenceMatcher(None,a.get('item_name','').casefold(),b.get('item_name','').casefold()).ratio()
    words=lambda x:set(w.casefold() for w in x.split() if len(w)>2)
    aw,bw=words(a.get('description','')),words(b.get('description',''))
    desc=len(aw&bw)/len(aw|bw) if aw|bw else 0
    loc=SequenceMatcher(None,a.get('location','').casefold(),b.get('location','').casefold()).ratio()
    try: days=abs((date.fromisoformat(a['event_date'])-date.fromisoformat(b['event_date'])).days); proximity=max(0,1-days/31)
    except (ValueError,KeyError,TypeError): days=None; proximity=0
    score=round(35*cat+30*name+20*desc+10*loc+5*proximity)
    reasons=[]
    if cat: reasons.append('Same item category')
    if name>=.55: reasons.append('Similar item names')
    if desc>0: reasons.append(f'{len(aw&bw)} shared description keyword(s)')
    if loc>=.45: reasons.append('Similar reported location')
    if days is not None and days<=14: reasons.append(f'Reports are {days} day(s) apart')
    return {'score':max(0,min(100,score)),'reasons':reasons or ['Few details overlap; verify manually.']}

def find_matches(source:dict,candidates:list[dict],limit=5):
    out=[]
    for item in candidates:
        score=explain_match(source,item)
        out.append({**item,**score})
    return sorted(out,key=lambda x:(-x['score'],x['id']))[:limit]
