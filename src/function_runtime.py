
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
from structures.graph_decimate import search, decimate, repair, search_k
from structures.smart_decimate import smart_search, smart_search_v2, smart_decimate

matplotlib.use("Agg")


def make_random_graph(n, seed=0, box=100.0, min_range=5.0, max_range=25.0, k_neighbors=None):

    rng = np.random.default_rng(seed)
    x = rng.uniform(0, box, n)
    y = rng.uniform(0, box, n)
    ranges = rng.uniform(min_range, max_range, n)
    return build_graph((x, y), ranges, neighbors=k_neighbors, use_sky_coords=False)


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


def benchmark(sizes, repeats=5, seed=0, k_neighbors=None):

    results = {
        "n": [], "search": [], "decimate": [], "repair": [], "repair_scoped": [],
        "smart_search": [], "smart_decimate": [],
    }

    for n in sizes:
        print(f"Benchmarking n={n} (k_neighbors={k_neighbors}) ...")

        base_graph = make_random_graph(n, seed=seed, k_neighbors=k_neighbors)
        t_search = time_fn(search_k, lambda: base_graph, repeats=repeats)

        t_smart_search = time_fn(smart_search, lambda: base_graph, repeats=repeats)

        def decimate_setup():
            g = make_random_graph(n, seed=seed, k_neighbors=k_neighbors)
            return g

        def smart_decimate_setup():
            g = make_random_graph(n, seed=seed, k_neighbors=k_neighbors)
            smart_search(g) # call for tree to be built
            return g

        def decimate_call(g):
            obj = search_k(g)
            decimate(g, obj)

        def smart_decimate_call(g):
            event = smart_search(g)
            smart_decimate(g, event)

        t_decimate = time_fn(decimate_call, decimate_setup, repeats=repeats)
        t_smart_decimate = time_fn(smart_decimate_call, smart_decimate_setup, repeats=repeats)

        t_repair = time_fn(repair, lambda: make_random_graph(n, seed=seed, k_neighbors=k_neighbors), repeats=repeats)

        all_ids = list(range(n))
        t_repair_scoped = time_fn(
            lambda g: repair(g, to_repair=all_ids),
            lambda: make_random_graph(n, seed=seed, k_neighbors=k_neighbors),
            repeats=repeats,
        )

        results["n"].append(n)
        results["search"].append(t_search)
        results["decimate"].append(t_decimate)
        results["repair"].append(t_repair)
        results["repair_scoped"].append(t_repair_scoped)
        results["smart_search"].append(t_smart_search)
        results["smart_decimate"].append(t_smart_decimate)

        print(f"  search:        {t_search*1000:.3f} ms")
        print(f"  smart_search:  {t_smart_search*1000:.3f} ms")
        print(f"  decimate:      {t_decimate*1000:.3f} ms")
        print(f"  smart_decimate:{t_smart_decimate*1000:.3f} ms")
        print(f"  repair:        {t_repair*1000:.3f} ms")
        print(f"  repair_scoped: {t_repair_scoped*1000:.3f} ms")

    return results

def plot_results(results, out_path, k_neighbors=None):
    fig, ax = plt.subplots(figsize=(8, 5.5))

    series = [
        ("search", "o"), ("decimate", "s"), ("repair", "^"), ("repair_scoped", "D"),
        ("smart_search", "P"), ("smart_decimate", "X"),
    ]

    for name, marker in series:
        ax.plot(results["n"], np.array(results[name]) * 1000, marker=marker, label=name)
    ax.loglog()
    ax.set_xlabel("Number of nodes (n)")
    ax.set_ylabel("Time (ms)")
    title_suffix = f" (k_neighbors={k_neighbors})" if k_neighbors is not None else " (dense, no k_neighbors)"
    ax.set_title("Runtime scaling: naive / scoped / smart (Dijkstra) search & decimate" + title_suffix)
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"\nSaved plot to {out_path}")


def run_benchmark(sizes=None, repeats=5, seed=42, image_name="runtime_scaling.png", k_neighbors=None, output_dir=None):

    if sizes is None:
        sizes = [10, 25, 50, 100, 200, 300, 400, 1000, 2500]

    out_path = os.path.join(output_dir, image_name)

    results = benchmark(sizes, repeats=repeats, seed=seed, k_neighbors=k_neighbors)
    plot_results(results, out_path, k_neighbors=k_neighbors)

    print("\nSummary (ms):")
    print(f"{'n':>6} {'search':>10} {'decimate':>10} {'repair':>10} {'repair_scoped':>14} "
          f"{'smart_search':>13} {'smart_decimate':>15}")
    for i, n in enumerate(results["n"]):
        print(f"{n:>6} {results['search'][i]*1000:>10.3f} "
            f"{results['decimate'][i]*1000:>10.3f} {results['repair'][i]*1000:>10.3f} "
            f"{results['repair_scoped'][i]*1000:>14.3f} "
            f"{results['smart_search'][i]*1000:>13.3f} {results['smart_decimate'][i]*1000:>15.3f}")

    return results


def run_to_completion(g, use_smart):

    search_fn = smart_search_v2 if use_smart else search_k
    decimate_fn = smart_decimate if use_smart else decimate

    start = time.perf_counter()

    steps = 0
    curr = search_fn(g)

    while curr[0] is not None:
        decimate_fn(g, curr)
        curr = search_fn(g)
        steps += 1

    elapsed = time.perf_counter() - start
    return elapsed, steps


def full_run_benchmark(sizes, repeats=3, seed=0, k_neighbors=None, run_smart=True):
    results = {"n": [], "naive_time": [], "naive_steps": [], "smart_time": [], "smart_steps": []}

    for n in sizes:
        print(f"Full-run benchmarking n={n} (k_neighbors={k_neighbors}) ...")

        naive_times, naive_steps_list = [], []
        smart_times, smart_steps_list = [], []

        for r in range(repeats):
            g_naive = make_random_graph(n, seed=seed + r, k_neighbors=k_neighbors)
            t, steps = run_to_completion(g_naive, use_smart=False)
            naive_times.append(t)
            naive_steps_list.append(steps)

            if run_smart:
                g_smart = make_random_graph(n, seed=seed + r, k_neighbors=k_neighbors)
                t, steps = run_to_completion(g_smart, use_smart=True)
                smart_times.append(t)
                smart_steps_list.append(steps)

        results["n"].append(n)
        results["naive_time"].append(min(naive_times))
        results["naive_steps"].append(int(np.mean(naive_steps_list)))

        if run_smart:
            results["smart_time"].append(min(smart_times))
            results["smart_steps"].append(int(np.mean(smart_steps_list)))
        else:
            results["smart_time"].append(None)
            results["smart_steps"].append(None)

        print(f"  naive: {min(naive_times)*1000:.2f} ms over {int(np.mean(naive_steps_list))} steps")
        if run_smart:
            print(f"  smart: {min(smart_times)*1000:.2f} ms over {int(np.mean(smart_steps_list))} steps")

    return results


def plot_full_run_results(results, out_path, k_neighbors=None, run_smart=True):

    fig, ax = plt.subplots(figsize=(8, 5.5))

    ax.plot(results["n"], np.array(results["naive_time"]) * 1000, marker="o", label="naive (full run)")
    if run_smart:
        ax.plot(results["n"], np.array(results["smart_time"]) * 1000, marker="s", label="smart (full run)")
    ax.loglog()
    ax.set_xlabel("Number of nodes (n)")
    ax.set_ylabel("Total time to full decimation (ms)")
    title_suffix = f" (k_neighbors={k_neighbors})" if k_neighbors is not None else " (dense)"
    ax.set_title("Full-run time to completion: naive" + (" vs smart" if run_smart else "") + title_suffix)
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"\nSaved plot to {out_path}")
 

output_dir = os.path.join(os.path.dirname(__file__), '..', 'tests', 'test-plots')


'''
run_benchmark(image_name="runtime_scaling_k_v2=None.png", output_dir=output_dir)
run_benchmark(image_name="runtime_scaling_k_v2=5.png", k_neighbors=5, output_dir=output_dir)
run_benchmark(image_name="runtime_scaling_k_v2=10.png", k_neighbors=10, output_dir=output_dir)
'''

'''
full_dense = full_run_benchmark([10, 25, 50, 100, 200, 300, 400, 1000], k_neighbors=None)
plot_full_run_results(full_dense, os.path.join(output_dir, "full_run_dense_v2.png"), k_neighbors=None)

full_sparse = full_run_benchmark([10, 25, 50, 100, 200, 300, 400, 1000], k_neighbors=5)
plot_full_run_results(full_sparse, os.path.join(output_dir, "full_run_k=5_v2.png"), k_neighbors=10)
 
full_sparse = full_run_benchmark([10, 25, 50, 100, 200, 300, 400, 1000], k_neighbors=10)
plot_full_run_results(full_sparse, os.path.join(output_dir, "full_run_k=10_v2.png"), k_neighbors=10)
'''

# full_dense = full_run_benchmark([10, 100, 100, 1000, 10000], k_neighbors=None, run_smart=False)
# plot_full_run_results(full_dense, os.path.join(output_dir, "full_run_dense_v2.png"), k_neighbors=None, run_smart=False)
'''
full_sparse1 = full_run_benchmark([10, 25, 50, 100, 200, 300, 400, 1000], k_neighbors=5)
plot_full_run_results(full_sparse1, os.path.join(output_dir, "full_run_k=5_v2.png"), k_neighbors=10)
 
full_sparse2 = full_run_benchmark([10, 25, 50, 100, 200, 300, 400, 1000], k_neighbors=10)
plot_full_run_results(full_sparse2, os.path.join(output_dir, "full_run_k=10_v2.png"), k_neighbors=10)

full_sparse3 = full_run_benchmark([10, 25, 50, 100, 200, 300, 400, 1000], k_neighbors=25)
plot_full_run_results(full_sparse3, os.path.join(output_dir, "full_run_k=25_v2.png"), k_neighbors=25)

full_sparse2 = full_run_benchmark([10, 25, 50, 100, 200, 300, 400, 1000], k_neighbors=50)
plot_full_run_results(full_sparse2, os.path.join(output_dir, "full_run_k=50_v2.png"), k_neighbors=50)
'''
