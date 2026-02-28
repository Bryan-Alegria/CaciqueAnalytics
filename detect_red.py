"""
detect_red.py
Extracts inaccurate pass coordinates (red arrows) from SofaScore match screenshots.
SofaScore inaccurate-pass color range: R≈200-230, G≈60-100, B≈40-80.
Output: mendez_inaccurate_estimated.json — list of {x, y, end_x, end_y} dicts per match.
"""
from PIL import Image
import numpy as np, json

MATCH_LABELS = {
    "ohiggins": {"label": "vs O'Higgins", "match_num": 1},
    "calera":   {"label": "vs La Calera", "match_num": 2},
    "everton":  {"label": "vs Everton",   "match_num": 3},
    "limache":  {"label": "vs Limache",   "match_num": 4},
}

assets = {
    "ohiggins": r"c:\Users\PC\Projects\CaciqueAnalytics\assets\image-1772176970380.png",
    "calera":   r"c:\Users\PC\Projects\CaciqueAnalytics\assets\image-1772177022786.png",
    "everton":  r"c:\Users\PC\Projects\CaciqueAnalytics\assets\image-1772177032339.png",
    "limache":  r"c:\Users\PC\Projects\CaciqueAnalytics\assets\image-1772177040733.png",
}

# ── SofaScore color calibration ───────────────────────────────────────────────
# Inaccurate pass (red arrow): R=190-240, G=60-110, B=40-90
# Accurate pass  (green):      R=20-80,   G=130-200, B=70-140

def is_sofascore_red(r, g, b):
    return (r > 180) & (r < 250) & (g > 50) & (g < 115) & (b > 30) & (b < 95)

def is_pitch_green(r, g, b):
    return (r > 20) & (r < 100) & (g > 70) & (g < 160) & (b > 30) & (b < 100)

def simple_cluster(coords, gap=15):
    """Groups nearby pixels into clusters using a simple greedy union approach."""
    if not coords:
        return []
    pts = sorted(coords)
    clusters = [[pts[0]]]
    for p in pts[1:]:
        merged = False
        for cl in clusters:
            # Check distance against last few points in the cluster for efficiency
            for q in cl[-5:]:  # only last 5 points to keep the loop fast
                if abs(p[0]-q[0]) <= gap and abs(p[1]-q[1]) <= gap:
                    cl.append(p)
                    merged = True
                    break
            if merged:
                break
        if not merged:
            clusters.append([p])
    return [c for c in clusters if len(c) >= 4]

all_inaccurate = {}

for name, path in assets.items():
    info = MATCH_LABELS[name]
    im = Image.open(path).convert("RGB")
    arr = np.array(im)
    h, w = arr.shape[:2]
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]

    # Locate the pitch boundaries using the green channel
    pg = is_pitch_green(r, g, b)
    py, px = np.where(pg)
    if not len(py):
        print(f"{name}: pitch not detected"); continue

    x0, x1 = int(px.min()), int(px.max())
    y0, y1 = int(py.min()), int(py.max())
    pw, ph = x1 - x0, y1 - y0

    # Normalise pixel coordinates to SofaScore scale [0-100]
    def norm(px_x, px_y):
        return round((px_x - x0) / pw * 100, 1), round((px_y - y0) / ph * 100, 1)

    # Extract red pixels WITHIN the detected pitch boundaries
    red_m = is_sofascore_red(r, g, b)
    red_m[:y0, :] = False; red_m[y1:, :] = False
    red_m[:, :x0] = False; red_m[:, x1:] = False
    ry, rx = np.where(red_m)

    print(f"\n{name} ({info['label']}): pitch x={x0}-{x1} y={y0}-{y1}  "
          f"red pixels={len(ry)}")

    coords = list(zip(rx.tolist(), ry.tolist()))
    clusters = simple_cluster(coords, gap=12)
    print(f"  Clusters detected: {len(clusters)}")

    inaccurate_passes = []
    for ci, cl in enumerate(clusters):
        cl_arr = np.array(cl)
        xs_cl, ys_cl = cl_arr[:,0], cl_arr[:,1]
        # Arrow start = smallest X, arrow end = largest X
        sx, sy = norm(int(xs_cl.min()), int(ys_cl[np.argmin(xs_cl)]))
        ex, ey = norm(int(xs_cl.max()), int(ys_cl[np.argmax(xs_cl)]))
        inaccurate_passes.append({"x": sx, "y": sy, "end_x": ex, "end_y": ey,
                                   "accurate": False, "keypass": False})
        print(f"    Arrow {ci+1}: ({sx},{sy}) -> ({ex},{ey})  [{len(cl)} px]")

    all_inaccurate[info["match_num"]] = inaccurate_passes

# Save estimated inaccurate pass coordinates to JSON
out = r"c:\Users\PC\Projects\CaciqueAnalytics\outputs\victor_felipe_mendez\mendez_inaccurate_estimated.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(all_inaccurate, f, ensure_ascii=False, indent=2)

print(f"\nSaved: mendez_inaccurate_estimated.json")
total = sum(len(v) for v in all_inaccurate.values())
print(f"Total estimated inaccurate passes: {total}")


for name, path in assets.items():
    im = Image.open(path).convert("RGB")
    arr = np.array(im)
    h, w = arr.shape[:2]
    print(f"\n=== {name} === {w}x{h}")

    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]

    # SofaScore pitch green: #2d5e3e approx — wide tolerance range
    pitch_green = (r > 20) & (r < 100) & (g > 70) & (g < 160) & (b > 30) & (b < 100)
    py, px = np.where(pitch_green)
    if not len(py):
        print("  Pitch not detected"); continue
    pitch_x0, pitch_x1 = int(px.min()), int(px.max())
    pitch_y0, pitch_y1 = int(py.min()), int(py.max())
    print(f"  Pitch: x={pitch_x0}-{pitch_x1}  y={pitch_y0}-{pitch_y1}")

    region = arr[pitch_y0:pitch_y1, pitch_x0:pitch_x1].copy()
    rr, gg, bb = region[:,:,0], region[:,:,1], region[:,:,2]
    pitch_mask = (rr > 20) & (rr < 100) & (gg > 70) & (gg < 160) & (bb > 30) & (bb < 100)
    white = (rr > 150) & (gg > 150) & (bb > 150)
    arrow_mask = ~pitch_mask & ~white
    ay, ax = np.where(arrow_mask)
    print(f"  Arrow pixels (non-green, non-white): {len(ay)}")

    # Top colors for red calibration verification
    unique_colors = {}
    for i in range(len(ay)):
        c = (int(rr[ay[i], ax[i]]), int(gg[ay[i], ax[i]]), int(bb[ay[i], ax[i]]))
        key = (c[0]//20*20, c[1]//20*20, c[2]//20*20)
        unique_colors[key] = unique_colors.get(key, 0) + 1
    top = sorted(unique_colors.items(), key=lambda x: -x[1])[:20]
    print("  Top colores (R//20, G//20, B//20)  count:")
    for color, count in top:
        print(f"    RGB≈{color}  x{count}")

    # Save diagnostic image showing only the detected arrow pixels
    diag = np.zeros_like(region)
    diag[arrow_mask] = region[arrow_mask]
    out_path = fr"c:\Users\PC\Projects\CaciqueAnalytics\assets\diag_{name}.png"
    Image.fromarray(diag).save(out_path)
    print(f"  -> diag_{name}.png saved")
