"""Prove the seed is toroidal: the same disc must have the same mass wherever it is placed.

Before the fix, a disc of radius 2 had 13 nodes at the centre and 6 at a corner, so the initial mass depended
on where the seed sat. This test builds the seed the way field_track does and checks the mass is invariant.
"""
import numpy as np

fails = 0


def check(name, ok, detail=""):
    global fails
    print(f"{'OK  ' if ok else 'FAIL'} {name}{(' — ' + detail) if detail and not ok else ''}")
    if not ok:
        fails += 1


def seed_mask(g: int, c: tuple[int, int], r0: float, toroidal: bool) -> np.ndarray:
    yy = np.arange(g).reshape(-1, 1).repeat(g, axis=1)
    xx = np.arange(g).reshape(1, -1).repeat(g, axis=0)
    if toroidal:
        dx = ((xx - c[0] + g // 2) % g) - g // 2
        dy = ((yy - c[1] + g // 2) % g) - g // 2
    else:
        dx = xx - c[0]
        dy = yy - c[1]
    return (dx * dx + dy * dy) <= r0 * r0


g, r0 = 96, 3.0
centre = (g // 2, g // 2)
corner = (0, 0)
edge = (0, g // 2)

eu_c = int(seed_mask(g, centre, r0, False).sum())
eu_k = int(seed_mask(g, corner, r0, False).sum())
tor_c = int(seed_mask(g, centre, r0, True).sum())
tor_k = int(seed_mask(g, corner, r0, True).sum())
tor_e = int(seed_mask(g, edge, r0, True).sum())

print(f"euclidean: centre {eu_c}, corner {eu_k}")
print(f"toroidal : centre {tor_c}, corner {tor_k}, edge {tor_e}")

check("the Euclidean seed DOES depend on position (the defect)", eu_c != eu_k, f"{eu_c} vs {eu_k}")
check("the toroidal seed does NOT depend on position", tor_c == tor_k == tor_e,
      f"{tor_c} / {tor_k} / {tor_e}")
check("the toroidal seed keeps the full disc at a corner", tor_k == tor_c, f"{tor_k} vs {tor_c}")

print(f"\n[seed-selftest] провалов: {fails} из 3")
raise SystemExit(0 if fails == 0 else 1)
