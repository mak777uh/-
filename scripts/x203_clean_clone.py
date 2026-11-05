"""
X203 — larger-n clean clones at fixed (geometry, phase, edge) on verified non-zero-baseline strata.
Pre-reg: reports/2026-11-05-x203-clean-clone-plan.md
CPU, field_track/X198 COMMON, F=0.030, 400 steps.
"""
from __future__ import annotations
import argparse, json, math, statistics, subprocess, sys, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PY=sys.executable; TRACK=ROOT/"scripts/field_track.py"; L1=ROOT/"morphogenesis/experiments/L1_field"; POND=ROOT/"morphogenesis/experiments/E09_pond"
FLOW="0.030"; STEPS=400; GRID=96; SCAN=250000
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
def fused_of(out):
    d=json.loads(Path(out).read_text(encoding='utf-8')); s=d.get('series') or []
    if not s: return None
    c=[len(r[1]) if isinstance(r,list) and len(r)>1 and isinstance(r[1],list) else 0 for r in s]
    return int(min(c)==1)
def run_track(tag,radius,sep_gap,seed,device):
    out=L1/f"{tag}.json"
    if out.exists() and out.stat().st_size>0:
        return {"tag":tag,"seed":seed,"status":"skipped","fused":fused_of(out)}
    cmd=[PY,str(TRACK),*COMMON,"--device",device,"--F",FLOW,"--seed",str(seed),"--out",str(out),"--init-spots",f"{radius:g}:{2*radius+sep_gap:g}"]
    t0=time.time(); p=subprocess.run(cmd,cwd=str(ROOT),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=3600)
    fus=fused_of(out) if p.returncode==0 and out.exists() else None
    rec={"tag":tag,"seed":seed,"status":"ok" if p.returncode==0 else "failed","fused":fus,"sec":round(time.time()-t0,1)}
    if rec['status']=='failed': rec['tail']=(p.stderr or p.stdout or '')[-250]
    return rec
def find_seeds(radius,sep,target_ph,edge_val,need,exclude):
    out=[]
    for seed in range(SCAN):
        if seed in exclude: continue
        ph,e=phase_edge(radius,sep,seed)
        if ph==target_ph and e==edge_val:
            out.append(seed); exclude.add(seed)
            if len(out)>=need: break
    return out
def wilson(k,n,z=1.96):
    if n==0: return [None,None]
    p=k/n; den=1+z*z/n; cen=(p+z*z/(2*n))/den; half=z*math.sqrt((p*(1-p)+z*z/(4*n))/n)/den
    return [round(max(0,cen-half),4), round(min(1,cen+half),4)]

def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('--device',default='cpu'); ap.add_argument('--write',action='store_true'); ap.add_argument('--n',type=int,default=8); args=ap.parse_args(argv)
    # candidate strata: from X202 (alts showed [1,0] at fixed phase+edge) and from X200 disagreeing with known (phase,edge)
    x202=json.loads((POND/'l1_field_x202_clone_repro.json').read_text(encoding='utf-8'))
    cand=[]
    # X202 world 2 had alts [1,0] at edge 15, phase ((3,2),(9,2)), r4 g10
    for w in x202['per_world']:
        if w.get('alt_disagree') and w['n_alt']>=2:
            # recover cell/phase/edge from orig
            edge=w['orig'][0][0] if w['orig'] else None
            ph=tuple(tuple(p) for p in (x202.get('phase_hint') or [])) # not stored; reconstruct below
    # build candidates from X202 runs
    by_w={}
    for r in x202['runs']:
        by_w.setdefault(r['world'],[]).append(r)
    for wi,rs in by_w.items():
        alts=[r for r in rs if r['kind']=='alt' and r.get('fused') is not None]
        orig=[r for r in rs if r['kind']=='orig']
        if len(alts)>=2 and len(set(r['fused'] for r in alts))>1 and orig:
            ph=tuple(tuple(p) for p in orig[0]['phase']); edge=orig[0]['edge'] # first member edge used for alts
            cand.append({'label':f'x202_w{wi}','radius':4.0,'gap':10.0,'phase':ph,'edge':edge,'source':'x202_alt_disagree'})
    # also add a few from X200 reproducible disagreeing (phase,edge of the fused member) as probes
    x200=json.loads((POND/'l1_field_x200_clone_pairs.json').read_text(encoding='utf-8'))
    for w in x200['p1_disagreeing_worlds']:
        if w['cell']!=[3.9,10,0.03]: continue
        by={}
        for e,o in zip(w['edge'],w['outcomes']): by.setdefault(e,[]).append(o)
        # pick edge value that had both? no, fixed edge - pick an edge with known fused=1 copies
        for e,os in by.items():
            if 1 in os:
                cand.append({'label':f"x200_{w['phase'][0][0]}{w['phase'][0][1]}",'radius':4.0,'gap':10.0,'phase':tuple(tuple(p) for p in w['phase']),'edge':e,'source':'x200_fused_edge'})
                break
        if len(cand)>=8: break
    # dedupe by (phase,edge)
    seen=set(); uniq=[]
    for c in cand:
        k=(c['phase'],c['edge'],c['gap']); 
        if k in seen: continue
        seen.add(k); uniq.append(c)
    cand=uniq[:6]
    print(f"[x203] candidates {len(cand)}")
    strata=[]; all_runs=[]
    for ci,c in enumerate(cand):
        used=set(); seeds=find_seeds(c['radius'],c['radius']*2+c['gap'],c['phase'],c['edge'],args.n+2,used)
        if len(seeds)<4:
            strata.append({**{k:v for k,v in c.items() if k!='phase'},'phase':c['phase'],'feasible':len(seeds),'status':'R1'})
            print(f"[x203] {c['label']} phase={c['phase']} edge={c['edge']} feasible={len(seeds)} R1"); continue
        # pilot 4
        pilot=seeds[:4]; rest=seeds[4:4+max(0,args.n-4)]
        runs=[]
        for si,s in enumerate(pilot):
            rec=run_track(f"x203_{ci}_p{si}_s{s}",c['radius'],c['gap'],s,args.device); rec.update({'stratum':ci,'phase':c['phase'],'edge':c['edge'],'stage':'pilot'}); runs.append(rec)
        vals=[r['fused'] for r in runs if r.get('fused') is not None]
        baseline_ok = len(vals)>=4 and 0<sum(vals)<len(vals) and (sum(vals)/len(vals) > 0.1 and sum(vals)/len(vals) < 0.9)
        share_p = (sum(vals)/len(vals)) if vals else None
        print(f"[x203] {c['label']} pilot n={len(vals)} fused={sum(vals) if vals else None} share={share_p} baseline_ok={baseline_ok}")
        stage='main' if baseline_ok else 'pilot_only'
        if baseline_ok:
            for si,s in enumerate(rest):
                rec=run_track(f"x203_{ci}_m{si}_s{s}",c['radius'],c['gap'],s,args.device); rec.update({'stratum':ci,'phase':c['phase'],'edge':c['edge'],'stage':'main'}); runs.append(rec)
        all_runs.extend(runs)
        vals2=[r['fused'] for r in runs if r.get('fused') is not None]
        k=sum(vals2); n=len(vals2)
        strata.append({**{k2:v for k2,v in c.items() if k2!='phase'},'phase':c['phase'],'feasible':len(seeds),'pilot_share':share_p,'baseline_ok':baseline_ok,
                       'n':n,'fused':k,'share':(round(k/n,4) if n else None),'wilson':wilson(k,n),
                       'disagree': (0<k<n) if n else None, 'stage':stage})
    baseline_strata=[s for s in strata if s.get('baseline_ok')]
    c1=len(baseline_strata)>=3
    c2=any(s['disagree'] for s in baseline_strata if s.get('n',0)>=6)
    # pooled over baseline
    K=sum(s['fused'] for s in baseline_strata); N=sum(s['n'] for s in baseline_strata)
    agg={"kind":"x203_clean_clone","candidates":len(cand),"strata":strata,"runs":all_runs,
         "C1_baseline_ge3":c1,"C2_residual_variance":c2,
         "pooled_baseline":{"n":N,"fused":K,"share":(round(K/N,4) if N else None),"wilson":wilson(K,N),"all_zero_disagree": (K==0 or K==N) if N else None},
         "refusal":{"R2_no_sensitive_strata": not c1}}
    print(json.dumps({k:agg[k] for k in ('candidates','C1_baseline_ge3','C2_residual_variance','pooled_baseline','refusal','strata')},ensure_ascii=False,indent=1))
    if args.write:
        (POND/'l1_field_x203_clean_clone.json').write_text(json.dumps(agg,ensure_ascii=False,indent=1)+'\n',encoding='utf-8',newline='\n')
        print('wrote x203')
    return 0

if __name__=='__main__': raise SystemExit(main())
