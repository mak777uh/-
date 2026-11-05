import json, math, statistics, glob
import numpy as np

P = 'morphogenesis/experiments/L1_field/'
G = 96


def cxy(c):
    return (float(c[2]), float(c[3]))


def wd(a, b):
    return (a - b + G / 2) % G - G / 2


def dd(p, q):
    return math.hypot(wd(p[0], q[0]), wd(p[1], q[1]))


d = json.load(open(P + 'x189_series_index.json', encoding='utf-8'))
pk3, drifts, pk10 = [], [], []
for r in d['runs']:
    tag = f"{r['arm']}_{r['level']}_s{r['seed']}"
    a = json.load(open(P + f'x189_{tag}.compact.json', encoding='utf-8'))
    s = a['series']
    by = {int(row[0]): [cxy(c) for c in row[1]] for row in s}
    seed0 = [cxy(c) for c in s[0][1]]
    for sp in sorted(glob.glob('_hourly/x189_fields/' + tag + '/*.npy')):
        st = int(sp.split('_t')[-1][:-4])
        cur = by.get(st)
        if not cur or len(cur) != 2:
            continue
        f = np.load(sp)

        def peak(c, rad):
            best = 0.0
            for dy in range(-rad, rad + 1):
                for dx in range(-rad, rad + 1):
                    if dx * dx + dy * dy <= rad * rad:
                        best = max(best, float(f[int(round(c[1] + dy)) % G, int(round(c[0] + dx)) % G]))
            return best
        pk3.append(max(peak(cur[0], 3), peak(cur[1], 3)))
        pk10.append(max(peak(cur[0], 10), peak(cur[1], 10)))
        o1 = dd(cur[0], seed0[0]) + dd(cur[1], seed0[1])
        o2 = dd(cur[0], seed0[1]) + dd(cur[1], seed0[0])
        drifts.append(min(o1, o2) / 2)

s3 = sorted(pk3)
print(f'radius-3 peak over {len(pk3)} slices: min {s3[0]:.3f} p25 {s3[len(s3)//4]:.3f} median {statistics.median(pk3):.3f} '
      f'p75 {s3[3*len(s3)//4]:.3f} max {s3[-1]:.3f}; >=0.3 in {sum(1 for v in pk3 if v>=0.3)}/{len(pk3)}')
s10 = sorted(pk10)
print(f'radius-10 peak: min {s10[0]:.3f} median {statistics.median(pk10):.3f} max {s10[-1]:.3f}')
sd = sorted(drifts)
print(f'matched centroid drift per slice: median {statistics.median(drifts):.2f} p75 {sd[3*len(sd)//4]:.2f} max {sd[-1]:.2f} cells')
