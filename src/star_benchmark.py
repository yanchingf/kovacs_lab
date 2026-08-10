
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import time
import numpy as np
import matplotlib.pyplot as plt

from structures.graph import build_graph
from structures.graph_decimate import search_k, decimate, repair
from data_handling.star_io import get_all_star_data, get_coords_and_brightness
from stars import get_k_neighbors

df = get_all_star_data()

_, _, all_skycoords = get_coords_and_brightness(df, c=1)

k_values = [10, 100, 1000]
repeats = 3
seed = 0

results = {"k": [], "time": [], "steps": []}

rng = np.random.default_rng(seed)

for k in k_values:

    if k > len(df):
        print(f"Skipping k={k}: only {len(df)} stars available in full catalog")
        continue

    times, steps_list = [], []

    for r in range(repeats):

        center_idx = int(rng.integers(0, len(df)))
        center_coord = all_skycoords[center_idx]

        neighbor_df, neighbor_seps = get_k_neighbors(
            center_coord, all_skycoords, df, k=k
        )

        coords, brightness, skycoords = get_coords_and_brightness(neighbor_df, c=1)
        x, y = coords[:, 0], coords[:, 1]

        g = build_graph((x, y), brightness, neighbors=None, use_sky_coords=True)

        start = time.perf_counter()

        n_steps = 0
        curr = search_k(g)
        while curr[0] is not None:
            _, updated = decimate(g, curr, filter=False)
            g, _ = repair(g, to_repair=updated)
            curr = search_k(g)
            n_steps += 1

        elapsed = time.perf_counter() - start

        times.append(elapsed)
        steps_list.append(n_steps)

        print(f"  k={k}, trial {r}: {elapsed*1000:.2f} ms over {n_steps} steps")

    results["k"].append(k)
    results["time"].append(min(times))
    results["steps"].append(int(np.mean(steps_list)))

    print(f"k={k}: min={min(times)*1000:.2f} ms, mean steps={int(np.mean(steps_list))}")

output_dir = os.path.join(os.path.dirname(__file__), 'tests', 'test-plots')
os.makedirs(output_dir, exist_ok=True)

fig, ax = plt.subplots()
ax.plot(results["k"], np.array(results["time"]) * 1000, marker="o")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("k (nearest neighbors around random star)")
ax.set_ylabel("Naive full-run time (ms)")
ax.set_title("Naive SDRG runtime on real star-data neighborhoods")
ax.grid(True, alpha=0.3)
fig.savefig(os.path.join(output_dir, "naive_star_neighborhood_scaling.png"))
plt.close(fig)

print(f"\nSaved plot to {os.path.join(output_dir, 'naive_star_neighborhood_scaling.png')}")