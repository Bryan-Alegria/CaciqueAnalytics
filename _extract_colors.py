"""
_extract_colors.py
Diagnostic script for inspecting dominant colors in exported PNG assets.
Samples horizontal strips at multiple heights and reports the top quantized
color buckets — used to calibrate color detection thresholds in detect_red.py.
"""
from PIL import Image
import numpy as np
import os

# Only inspect PNG files whose names contain "Jeyson" or "Joaqu" (the two player assets)
assets = r"c:\Users\PC\Projects\CaciqueAnalytics\assets"
files = [f for f in os.listdir(assets) if f.endswith(".png") and ("Jeyson" in f or "Joaqu" in f)]
files.sort()

for fname in files:
    path = os.path.join(assets, fname)
    img = Image.open(path).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]
    print(f"\n{'='*65}")
    print(f"  {fname}  [{w}x{h}]")

    # Sample 7 evenly-spaced columns at 8 different row heights
    print(f"\n  Horizontal strip profile:")
    for row_frac, label in [(0.04, "4%"), (0.08, "8%"), (0.12, "12%"), (0.18, "18%"),
                            (0.30, "30%"), (0.50, "50%"), (0.80, "80%"), (0.95, "95%")]:
        r = int(row_frac * h)
        samp = [(arr[r, int(c*w)]) for c in (0.05, 0.20, 0.35, 0.50, 0.65, 0.80, 0.95)]
        hexes = " ".join(f"#{p[0]:02X}{p[1]:02X}{p[2]:02X}" for p in samp)
        print(f"    row {label:3s} y={r:4d}: {hexes}")

    # Random sample of 30k pixels; quantize to buckets of 20 to find dominant colors
    flat = arr.reshape(-1, 3).astype(np.int32)
    np.random.seed(42)
    idx = np.random.choice(len(flat), min(30000, len(flat)), replace=False)
    sample = flat[idx]
    q = (sample // 20) * 20
    unique, counts = np.unique(q, axis=0, return_counts=True)
    top = sorted(zip(counts, unique.tolist()), reverse=True)[:18]
    print(f"\n  Top color buckets (quantized by 20):")
    for cnt, col in top:
        pct = cnt / idx.shape[0] * 100
        print(f"    #{col[0]:02X}{col[1]:02X}{col[2]:02X}  {pct:5.1f}%")
