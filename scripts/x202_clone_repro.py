"""
X202 — reproduce sensitive X200 clone-pairs and test clean clones (fixed phase + fixed edge).
Pre-reg: reports/2026-11-05-x202-clone-repro-plan.md
Reuses field_track/X198 params. CPU.
"""
from __future__ import annotations
import argparse, json, math, statistics, subprocess, sys, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PY=sys.executable; TRACK=ROOT/"scripts/field_track.py"; L1=ROOT/"morphogenesis/experiments/L1_field"; POND=ROOT/"morphogenesis/experiments/E09_pond"
FLOW="0.030"; STEPS=400; GRID=96; SCALE=12.0; SCAN=200000
COMMON=["--steps","400","--grid","96","--dt","1.0","--Du","0.16","--Dv","0.08","--k","0.06","--eps","0.0",
 "--hetero-scale","12.0","--hetero-period","0.0","--hetero-amp","0.5","--hetero-signal","lab/streams/const_ones.json",
 "--sample-every","10","--threshold","0.2","--freq-dep","0.0","--bin-width","0.2","--beta","0.0","--s-ref","1.0","--mutation","0.15",
 "--overlap","0.5","--split-new-uid","--init-jitter"]

def jitter(seed):
    jr=np.random.default_rng(int(seed)+9187); return tuple(int(v) for v in jr.integers(-GRID//4, GRID//4+1, size=2))
def phase_edge(radius,sep,seed):
    jx,jy=jitter(seed); cx,cy=GRID/2.0+jx, GRID/2.0+jy; x0,x1=cx-sep/2.0,cx+sep/2.0
    b0=(int(round(x0)),int(round(cy))); b1=(int(round(x1)),int(round(cy)))
    ph=tuple(sorted(((b0[0]%12,b0[1]%12),(b1[0]%12,b1[1]%12))))
    edge=min(b0[0],b0[1],GRID-1-b0[0],GRID-1-b0[1],b1[0],b1[1],GRID-1-b1[0],GRID-1-b1[1])
    return ph,edge
def seed_from_file(fname):
    p=L1/fname if not fname.endswith('.json') else L1/fname
    if not p.exists(): p=L1/(fname+'.json')
    d=json.loads(p.read_text(encoding='utf-8')); return int(d['params']['seed'])
def run_track(tag,radius,gap,seed,device):
    sep=2*radius+gap; out=L1/f"{tag}.json"
    if out.exists() and out.stat().st_size>0:
        d=json.loads(out.read_text(encoding='utf-8')); series=d.get('series') or []
        fus=None
        if series:
            counts=[len(r[1]) if isinstance(r,list) and len(r)>1 and isinstance(r[1],list) else 0 for r in series]
            fus=int(min(counts)==1)
        return {"tag":tag,"seed":seed,"status":"skipped","fused":fus}
    cmd=[PY,str(TRACK),*COMMON,"--device",device,"--F",FLOW,"--seed",str(seed),"--out",str(out),"--init-spots",f"{radius:g}:{sep:g}"]
    t0=time.time(); p=subprocess.run(cmd,cwd=str(ROOT),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=3600)
    fus=None
    if p.returncode==0 and out.exists():
        d=json.loads(out.read_text(encoding='utf-8')); series=d.get('series') or []
        if series:
            counts=[len(r[1]) if isinstance(r,list) and len(r)>1 and isinstance(r[1],list) else 0 for r in series]
            fus=int(min(counts)==1)
    rec={"tag":tag,"seed":seed,"status":"ok" if p.returncode==0 else "failed","fused":fus,"sec":round(time.time()-t0,1)}
    if rec['status']=='failed': rec['tail']=(p.stderr or p.stdout or '')[-250]
    return rec
def find_edge_fixed(radius,sep,target_ph,edge_val,exclude,need=2):
    out=[]
    for seed in range(SCAN):
        if seed in exclude: continue
        ph,e=phase_edge(radius,sep,seed)
        if ph==target_ph and e==edge_val:
            out.append(seed); exclude.add(seed)
            if len(out)>=need: break
    return out

def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('--device',default='cpu'); ap.add_argument('--write',action='store_true'); args=ap.parse_args(argv)
    d=json.loads((POND/'l1_field_x200_clone_pairs.json').read_text(encoding='utf-8'))
    # reproducible disagreeing worlds (same edge -> same outcome across copies)
    worlds=[]
    for w in d['p1_disagreeing_worlds']:
        if w['cell'] not in ([3.9,10,0.03],[3.9,9,0.03]): continue
        by={}
        for e,o,f in zip(w['edge'],w['outcomes'],w['files']):
            by.setdefault(e,[]).append((o,f))
        if any(len(set(v for v,_ in vs))>1 for vs in by.values()): continue
        # pick one representative file per edge
        reps=[(e,vs[0][1],vs[0][0]) for e,vs in sorted(by.items())]
        worlds.append({'cell':w['cell'],'phase':tuple(tuple(p) for p in w['phase']),'reps':reps,'by':{e:[v for v,_ in vs] for e,vs in by.items()}})
    worlds=worlds[:6]
    print(f"[x202] selected {len(worlds)} reproducible worlds")
    results=[]
    for wi,w in enumerate(worlds):
        radius,sep_gap,_F=w['cell']; radius=float(radius); sep=2*radius+sep_gap
        # repro: rerun original seeds
        orig=[]
        for e,fname,hist in w['reps']:
            seed=seed_from_file(fname)
            tag=f"x202_w{wi}_edge{e}_orig_s{seed}"
            rec=run_track(tag,radius,sep_gap,seed,args.device); rec.update({'world':wi,'phase':w['phase'],'edge':e,'hist':hist,'kind':'orig'})
            results.append(rec); orig.append(rec)
            print(f"[x202] w{wi} edge{e} seed={seed} hist={hist} -> {rec['fused']} {rec['status']}")
        # clean clone: same (phase,edge) as first member, different seeds
        e0=w['reps'][0][0]; used={r['seed'] for r in orig}
        alts=find_edge_fixed(radius,sep,w['phase'],e0,used,need=2)
        for ai,seed in enumerate(alts):
            tag=f"x202_w{wi}_edge{e0}_alt{ai}_s{seed}"
            rec=run_track(tag,radius,sep_gap,seed,args.device); rec.update({'world':wi,'phase':w['phase'],'edge':e0,'hist':None,'kind':'alt'})
            results.append(rec); print(f"[x202] w{wi} alt edge{e0} seed={seed} -> {rec['fused']}")
        if not alts: print(f"[x202] w{wi} no edge-fixed alternates for edge {e0} (R1)")
    # analysis
    ok=[r for r in results if r.get('fused') is not None]
    # per world repro
    wstats=[]
    for wi in range(len(worlds)):
        o=[r for r in ok if r['world']==wi and r['kind']=='orig']
        a=[r for r in ok if r['world']==wi and r['kind']=='alt']
        repro_dis= len(o)>=2 and len(set(r['fused'] for r in o))>1
        hist_dis= len(set(r['hist'] for r in o))>1 if len(o)>=2 else False
        alt_dis= len(a)>=2 and len(set(r['fused'] for r in a))>1
        wstats.append({'world':wi,'n_orig':len(o),'n_alt':len(a),'repro_disagree':repro_dis,'hist_disagree':hist_dis,'alt_disagree':alt_dis,
                       'orig':[(r['edge'],r['hist'],r['fused']) for r in o],'alt':[r['fused'] for r in a]})
    c1=sum(1 for w in wstats if w['repro_disagree'])
    c3_worlds=[w for w in wstats if w['n_alt']>=1]
    c3_dis=sum(1 for w in c3_worlds if w['n_alt']>=2 and w['alt_disagree'])
    agg={"kind":"x202_clone_repro","worlds":len(worlds),"runs":results,"per_world":wstats,
         "c1_repro_pairs_ge3":c1>=3,"c1_count":c1,"c3_alt_worlds":len(c3_worlds),"c3_alt_disagree_worlds":c3_dis,
         "refusal":{"R1_edge_fixed_underpowered": sum(1 for w in wstats if w['n_alt']==0), "R2_nonrepro": c1<2}}
    print(json.dumps({k:agg[k] for k in ('worlds','c1_repro_pairs_ge3','c1_count','c3_alt_worlds','c3_alt_disagree_worlds','refusal','per_world')},ensure_ascii=False,indent=1))
    if args.write:
        (POND/'l1_field_x202_clone_repro.json').write_text(json.dumps(agg,ensure_ascii=False,indent=1)+'\n',encoding='utf-8',newline='\n')
        print("wrote x202 aggregate")
    return 0

if __name__=='__main__': raise SystemExit(main())
