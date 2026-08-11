
import sys
import os
import json
import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt


def load_stats(run_dir):

    pattern = os.path.join(run_dir, "c_*", "stats.json")
    paths = glob.glob(pattern)
    if not paths:
        raise FileNotFoundError(f"No stats.json files found under {pattern}")

    stats = []
    for p in paths:
        with open(p) as f:
            stats.append(json.load(f))

    stats.sort(key=lambda s: s["c"])
    return stats


def plot_num_clusters_vs_c(stats, out_dir):

    c_vals = [s["c"] for s in stats]
    num_clusters = [s["num_clusters"] for s in stats]

    fig, ax = plt.subplots()
    ax.plot(c_vals, num_clusters, marker='o')
    ax.set_xlabel("c")
    ax.set_ylabel("Final number of clusters")
    ax.set_title("Number of clusters vs c (naive)")
    ax.grid(True, alpha=0.3)
    fig.savefig(os.path.join(out_dir, "num_clusters_vs_c.png"))
    plt.close(fig)


def plot_max_cluster_size_vs_c(stats, out_dir):

    c_vals = [s["c"] for s in stats]
    max_sizes = [s["max_cluster_size"] for s in stats]

    fig, ax = plt.subplots()
    ax.plot(c_vals, max_sizes, marker='o', color='darkorange')
    ax.set_xlabel("c")
    ax.set_ylabel("Final max cluster size")
    ax.set_title("Max cluster size vs c (naive)")
    ax.grid(True, alpha=0.3)
    fig.savefig(os.path.join(out_dir, "max_cluster_size_vs_c.png"))
    plt.close(fig)


def plot_size_distribution_across_c(stats, out_dir):

    fig, ax = plt.subplots()

    for s in stats:
        sizes = s["cluster_sizes"]
        if not sizes:
            continue
        from collections import Counter
        counts = Counter(sizes)
        xs = sorted(counts.keys())
        ys = [counts[x] for x in xs]
        ax.plot(xs, ys, marker='o', ms=3, label=f"c={s['c']}")

    ax.set_xlabel("Cluster size")
    ax.set_ylabel("Count of clusters with that size")
    ax.set_title("Cluster size distribution across c (naive)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.savefig(os.path.join(out_dir, "cluster_size_distribution_across_c.png"))
    plt.close(fig)


def plot_ground_truth_agreement_vs_c(stats, out_dir):

    c_vals = [s["c"] for s in stats]
    purity = [s.get("purity") for s in stats]
    ari = [s.get("adjusted_rand_index") for s in stats]

    if all(p is None for p in purity):
        return 

    fig, ax = plt.subplots()
    ax.plot(c_vals, purity, marker='o', color='green', label='purity')
    if not all(a is None for a in ari):
        ax.plot(c_vals, ari, marker='s', color='purple', label='adjusted Rand index')
    ax.set_xlabel("c")
    ax.set_ylabel("Score vs ground-truth constellations")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("SDRG clusters vs true constellations (naive)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.savefig(os.path.join(out_dir, "ground_truth_agreement_vs_c.png"))
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate per-c stats.json files into cross-c percolation plots."
    )
    parser.add_argument("run_dir", type=str,
                         help="Directory containing c_1/, c_2/, ... subfolders with stats.json")
    parser.add_argument("--out-dir", type=str, default=None,
                         help="Where to save plots (default: same as run_dir)")
    args = parser.parse_args()

    out_dir = args.out_dir or args.run_dir
    os.makedirs(out_dir, exist_ok=True)

    stats = load_stats(args.run_dir)
    print(f"Loaded stats for c values: {[s['c'] for s in stats]}")

    plot_num_clusters_vs_c(stats, out_dir)
    plot_max_cluster_size_vs_c(stats, out_dir)
    plot_size_distribution_across_c(stats, out_dir)
    plot_ground_truth_agreement_vs_c(stats, out_dir)

    print(f"Saved cross-c percolation plots to {out_dir}")


if __name__ == "__main__":
    main()