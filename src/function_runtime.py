import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import time
import timeit
import random
import copy

import numpy as np
import matplotlib

import matplotlib.pyplot as plt

from structures.graph import build_graph
from structures.graph_decimate import search, decimate, repair

matplotlib.use("Agg")


def make_random_graph(n, seed=0, box=100.0, min_range=5.0, max_range=25.0):

    rng = np.random.default_rng(seed)
    x = rng.uniform(0, box, n)
    y = rng.uniform(0, box, n)
    ranges = rng.uniform(min_range, max_range, n)
    # synthetic 2D test data, not real RA/Dec -- must stay Euclidean or
    # y values above 90 blow up SkyCoord's declination validation
    return build_graph((x, y), ranges, use_sky_coords=False)


def time_fn(fn, setup_fn, repeats=5, number=1):

    times = []
    for i in range(repeats):
        graph = setup_fn()
        start = time.perf_counter()
        for j in range(number):
            fn(graph)
        end = time.perf_counter()
        times.append((end - start) / number)
    return min(times)  


def benchmark(sizes, repeats=5, seed=0):
    results = {"n": [], "search": [], "decimate": [], "repair": [], "repair_scoped": []}

    for n in sizes:
        print(f"Benchmarking n={n} ...")

        base_graph = make_random_graph(n, seed=seed)
        t_search = time_fn(search, lambda: base_graph, repeats=repeats)

        def decimate_setup():
            g = make_random_graph(n, seed=seed)
            return g

        def decimate_call(g):
            obj = search(g)
            decimate(g, obj)

        t_decimate = time_fn(decimate_call, decimate_setup, repeats=repeats)
        t_repair = time_fn(repair, lambda: make_random_graph(n, seed=seed), repeats=repeats)

        # scoped repair: same graph, but pass to_repair=all node ids so
        # it goes through the KDTree-scoped query path (if graph.tree is
        # set) instead of the full O(n^2) scan
        all_ids = list(range(n))
        t_repair_scoped = time_fn(
            lambda g: repair(g, to_repair=all_ids),
            lambda: make_random_graph(n, seed=seed),
            repeats=repeats,
        )

        results["n"].append(n)
        results["search"].append(t_search)
        results["decimate"].append(t_decimate)
        results["repair"].append(t_repair)
        results["repair_scoped"].append(t_repair_scoped)

        print(f"  search:        {t_search*1000:.3f} ms")
        print(f"  decimate:      {t_decimate*1000:.3f} ms")
        print(f"  repair:        {t_repair*1000:.3f} ms")
        print(f"  repair_scoped: {t_repair_scoped*1000:.3f} ms")

    return results

def plot_results(results, out_path):
    fig, ax = plt.subplots(figsize=(8, 5.5))

    for name, marker in [("search", "o"), ("decimate", "s"), ("repair", "^"), ("repair_scoped", "D")]:
        ax.plot(results["n"], np.array(results[name]) * 1000, marker=marker, label=name)
    ax.loglog()
    ax.set_xlabel("Number of nodes (n)")
    ax.set_ylabel("Time (ms)")
    ax.set_title("Runtime scaling of search / decimate / repair (full vs scoped)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"\nSaved plot to {out_path}")


def run_benchmark(sizes=None, repeats=5, seed=42, image_name="runtime_scaling.png"):

    if sizes is None:
        sizes = [10, 25, 50, 100, 200, 300, 400, 1000, 2500, 3500]

    output_dir = os.path.join(os.path.dirname(__file__), 'tests')
    os.makedirs(output_dir, exist_ok=True)

    out_path = os.path.join(output_dir, image_name)

    results = benchmark(sizes, repeats=repeats, seed=seed)
    plot_results(results, out_path)

    print("\nSummary (ms):")
    print(f"{'n':>6} {'search':>10} {'decimate':>10} {'repair':>10} {'repair_scoped':>14}")
    for i, n in enumerate(results["n"]):
        print(f"{n:>6} {results['search'][i]*1000:>10.3f} "
            f"{results['decimate'][i]*1000:>10.3f} {results['repair'][i]*1000:>10.3f} "
            f"{results['repair_scoped'][i]*1000:>14.3f}")

    return results

run_benchmark()