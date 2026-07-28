
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import time
import json
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime

from stars import final_visualization

from data_handling.star_io import get_all_star_data, get_patch, get_coords_and_brightness
from sdrg import run_sdrg, plot_star_map

data = get_all_star_data()

c_lower_lim = 1
c_upper_lim = 5
c_range = list(range(c_lower_lim, c_upper_lim + 1))

patch_names = ["Cnc"]

variants = {
    "unfiltered": False,
    "filtered": True,
}

output_dir = os.path.join(os.path.dirname(__file__), 'tests', 'benchmarks')
os.makedirs(output_dir, exist_ok=True)

results = []

log_path = os.path.join(output_dir, "benchmark_log.txt")

def log(msg, also_print=True):
    if also_print:
        print(msg)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n")


log(f"=== Benchmark run started ===")
log(f"c_range={c_range}, patches={patch_names}, variants={list(variants.keys())}")

for patch_name in patch_names:

    patch_df = get_patch(data, patch_name)

    if patch_df.shape[0] < 2:
        log(f"{patch_name}: not enough stars, skipping")
        continue

    log(f"{patch_name}: {len(patch_df)} stars found")

    patch_dir = os.path.join(output_dir, patch_name, datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(patch_dir, exist_ok=True)

    for c in c_range:

        t = get_coords_and_brightness(patch_df, c=c)
        coords, brightness, skycoords = t[0], t[1], t[2]
        x = coords[:, 0]
        y = coords[:, 1]

        for variant_name, filter_flag in variants.items():

            run_dir = os.path.join(patch_dir, f"c_{c}", variant_name)
            os.makedirs(run_dir, exist_ok=True)

            log(f"Running {patch_name} : c={c} : variant={variant_name} "
                f"(filter_bonds={filter_flag}) : n={len(x)}")

            t0 = time.perf_counter()

            g = run_sdrg(
                n=len(x),
                neg_x_lim=0, x_lim=float(x.max()) + 1,
                neg_y_lim=0, y_lim=float(y.max()) + 1,
                random=False,
                inp=(x, y, brightness),
                percolation_stats=True,
                skycoords=skycoords,
                patch_name=patch_name,
                output_dir=run_dir,
                filter_bonds=filter_flag,
                plot_every=10,
            )

            elapsed = time.perf_counter() - t0

            c_dir = os.path.join(patch_dir, f"c_{c}", f"filter-{filter_flag}")
            os.makedirs(c_dir, exist_ok=True)

            plot_star_map(skycoords, g, iteration="final", output_dir=c_dir)
            final_visualization(g, skycoords, patch_name, c_dir)

            sizes = [len(members) for members in g.group_ids.values()]

            result = {
                "patch": patch_name,
                "c": c,
                "n_stars": len(x),
                "variant": variant_name,
                "filter_bonds": filter_flag,
                "elapsed_sec": elapsed,
                "num_clusters": len(sizes),
                "max_cluster_size": max(sizes) if sizes else 0,
                "cluster_size_dist": dict(Counter(sizes)),
            }
            results.append(result)

            log(f"  -> {elapsed:.3f}s, {result['num_clusters']} clusters, "
                f"max size {result['max_cluster_size']}")

    for c in c_range:
        rows = [r for r in results if r["patch"] == patch_name and r["c"] == c]
        by_variant = {r["variant"]: r for r in rows}

        if set(by_variant.keys()) != set(variants.keys()):
            continue

        u = by_variant["unfiltered"]
        f = by_variant["filtered"]
        if u["num_clusters"] != f["num_clusters"] or u["max_cluster_size"] != f["max_cluster_size"]:
            log(f"WARNING: {patch_name} c={c} — filtered and unfiltered runs "
                f"disagree on final cluster structure "
                f"({u['num_clusters']} vs {f['num_clusters']} clusters, "
                f"max size {u['max_cluster_size']} vs {f['max_cluster_size']})")
        else:
            log(f"OK: {patch_name} c={c} — filtered/unfiltered final structure matches "
                f"({u['num_clusters']} clusters, max size {u['max_cluster_size']})")

    times_by_variant = {
        vname: [r["elapsed_sec"] for r in results
                 if r["patch"] == patch_name and r["variant"] == vname]
        for vname in variants
    }

    speedup_log = []
    for c, unf_t, filt_t in zip(c_range, times_by_variant["unfiltered"], times_by_variant["filtered"]):
        speedup = unf_t / filt_t if filt_t > 0 else float("inf")
        speedup_log.append(f"c={c}: unfiltered={unf_t:.3f}s, filtered={filt_t:.3f}s, speedup={speedup:.2f}x")
    log(f"{patch_name} timing summary:\n  " + "\n  ".join(speedup_log))

    fig, ax = plt.subplots()
    for vname, times in times_by_variant.items():
        ax.plot(c_range, times, marker='o', label=vname)
    ax.set_xlabel("c")
    ax.set_ylabel("Wall-clock time (s)")
    ax.set_title(f"{patch_name}: runtime vs c (filtered vs unfiltered)")
    ax.legend()
    fig.savefig(os.path.join(patch_dir, "runtime_vs_c.png"))
    plt.close(fig)

    log(f"Done: {patch_name} ({len(c_range)} c-values x {len(variants)} variants)")

with open(os.path.join(output_dir, "results.json"), "w") as f:
    json.dump(results, f, indent=2)

log(f"All benchmark results written to {os.path.join(output_dir, 'results.json')}")
log(f"=== Benchmark run finished ===\n")