import sys
import os
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


data = get_all_star_data()
print(f"Full catalog: {len(data)} stars")

c_lower_lim = 1
c_upper_lim = 5
c_range = list(range(c_lower_lim, c_upper_lim + 1))

output_dir = os.path.join(os.path.dirname(__file__), 'tests', 'runs')
os.makedirs(output_dir, exist_ok=True)

run_dir = os.path.join(output_dir, "full_catalog", datetime.now().strftime("%Y%m%d_%H%M%S"))
os.makedirs(run_dir, exist_ok=True)

num_clusters_by_c = []
max_cluster_size_by_c = []
purity_by_c = []
ari_by_c = []

for c in c_range:

    print(f"Running full catalog : c={c} (naive)")

    c_dir = os.path.join(run_dir, f"c_{c}")
    os.makedirs(c_dir, exist_ok=True)

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
    num_clusters_by_c.append(len(sizes))
    max_cluster_size_by_c.append(max(sizes) if sizes else 0)

    purity = cluster_purity(pred_labels, true_labels)
    purity_by_c.append(purity)

    if HAVE_SKLEARN_METRICS:
        ari = adjusted_rand_score(true_labels, pred_labels)
        ari_by_c.append(ari)
        print(f"  c={c}: {len(sizes)} clusters, max size {max(sizes) if sizes else 0}, "
              f"purity={purity:.3f}, ARI={ari:.3f}")
    else:
        print(f"  c={c}: {len(sizes)} clusters, max size {max(sizes) if sizes else 0}, "
              f"purity={purity:.3f}")


fig, ax = plt.subplots()
ax.plot(c_range, num_clusters_by_c, marker='o')
ax.set_xlabel("c"); ax.set_ylabel("Final number of clusters")
ax.set_title("Full catalog: num clusters vs c (naive)")
fig.savefig(os.path.join(run_dir, "num_clusters_vs_c.png"))
plt.close(fig)

fig, ax = plt.subplots()
ax.plot(c_range, max_cluster_size_by_c, marker='o', color='darkorange')
ax.set_xlabel("c"); ax.set_ylabel("Final max cluster size")
ax.set_title("Full catalog: max cluster size vs c (naive)")
fig.savefig(os.path.join(run_dir, "max_cluster_size_vs_c.png"))
plt.close(fig)

fig, ax = plt.subplots()
ax.plot(c_range, purity_by_c, marker='o', color='green', label='purity')
if HAVE_SKLEARN_METRICS:
    ax.plot(c_range, ari_by_c, marker='s', color='purple', label='adjusted Rand index')
ax.set_xlabel("c"); ax.set_ylabel("Score vs ground-truth constellations")
ax.set_ylim(-0.05, 1.05)
ax.set_title("Full catalog: SDRG clusters vs true constellations (naive)")
ax.legend()
fig.savefig(os.path.join(run_dir, "ground_truth_agreement_vs_c.png"))
plt.close(fig)

print(f"\nDone: full catalog ({len(c_range)} runs), results in {run_dir}")