
import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime

from astropy.coordinates import get_constellation

from data_handling.star_io import get_all_star_data, get_coords_and_brightness
from sdrg import run_sdrg
from stars import plot_star_map, final_visualization

try:
    from sklearn.metrics import adjusted_rand_score
    HAVE_SKLEARN_METRICS = True
except ImportError:
    HAVE_SKLEARN_METRICS = False
    print("WARNING: sklearn not available -- skipping adjusted Rand index, "
          "will only report cluster purity vs ground truth.")


def ground_truth_labels(skycoords, short_name=True):
   
    names = get_constellation(skycoords, short_name=short_name)
    return np.array(names)


def cluster_purity(pred_labels, true_labels):

    total = len(true_labels)
    correct = 0
    for cluster_id in np.unique(pred_labels):
        mask = pred_labels == cluster_id
        true_in_cluster = true_labels[mask]
        if len(true_in_cluster) == 0:
            continue
        majority_count = Counter(true_in_cluster).most_common(1)[0][1]
        correct += majority_count
    return correct / total if total > 0 else 0.0


def main():
    parser = argparse.ArgumentParser(description="Run naive SDRG on full star catalog for one c value.")
    parser.add_argument("--c", type=int, required=True, help="Brightness scaling constant")
    parser.add_argument("--max-stars", type=int, default=None,
                         help="Optional cap on number of stars, for quick sanity-check runs")
    parser.add_argument("--output-dir", type=str, default=None,
                         help="Output directory (default: tests/runs/full_catalog/<timestamp>/c_<c>)")
    args = parser.parse_args()

    c = args.c

    data = get_all_star_data()
    if args.max_stars is not None:
        data = data.iloc[:args.max_stars].reset_index(drop=True)
    print(f"Catalog size for this run: {len(data)} stars")

    base_output_dir = os.path.join(os.path.dirname(__file__), 'tests', 'runs')
    os.makedirs(base_output_dir, exist_ok=True)

    if args.output_dir is not None:
        c_dir = args.output_dir
    else:
        run_dir = os.path.join(base_output_dir, "full_catalog", datetime.now().strftime("%Y%m%d_%H%M%S"))
        c_dir = os.path.join(run_dir, f"c_{c}")
    os.makedirs(c_dir, exist_ok=True)

    print(f"Running full catalog : c={c} (naive)")

    coords, brightness, skycoords = get_coords_and_brightness(data, c=c)
    x, y = coords[:, 0], coords[:, 1]

    true_labels = ground_truth_labels(skycoords)

    g = run_sdrg(
        n=len(x),
        neg_x_lim=0, x_lim=float(x.max()) + 1,
        neg_y_lim=0, y_lim=float(y.max()) + 1,
        random=False,
        inp=(x, y, brightness),
        percolation_stats=True,
        skycoords=skycoords,
        patch_name="full_catalog",
        output_dir=c_dir,
        plot_every=100000000,
        smart=False,
    )

    plot_star_map(skycoords, g, iteration="final", output_dir=c_dir)
    final_visualization(g, skycoords, "full_catalog", c_dir)

    n = len(x)
    pred_labels = np.array([g.nodes[i].cluster_id for i in range(n)])

    sizes = [len(members) for members in g.group_ids.values()]
    num_clusters = len(sizes)
    max_cluster_size = max(sizes) if sizes else 0

    purity = cluster_purity(pred_labels, true_labels)

    result_line = f"c={c}: {num_clusters} clusters, max size {max_cluster_size}, purity={purity:.3f}"

    if HAVE_SKLEARN_METRICS:
        ari = adjusted_rand_score(true_labels, pred_labels)
        result_line += f", ARI={ari:.3f}"
    else:
        ari = None

    print(result_line)

    summary_path = os.path.join(c_dir, "summary.txt")
    with open(summary_path, "w") as f:
        f.write(result_line + "\n")
        f.write(f"n_stars={len(x)}\n")
        f.write(f"num_clusters={num_clusters}\n")
        f.write(f"max_cluster_size={max_cluster_size}\n")
        f.write(f"purity={purity}\n")
        if ari is not None:
            f.write(f"adjusted_rand_index={ari}\n")

    print(f"Done: c={c}, results in {c_dir}")


if __name__ == "__main__":
    main()