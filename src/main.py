
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from data_handling.star_io import get_all_star_data, get_patch, get_coords_and_brightness
from datetime import datetime
from sdrg import run_sdrg

from stars import plot_star_map
from stars import final_visualization

data = get_all_star_data()

c_lower_lim = 2
c_upper_lim = 3
c_range = list(range(c_lower_lim, c_upper_lim + 1))

patch_names = ["Cnc"]

output_dir = os.path.join(os.path.dirname(__file__), 'tests', 'runs')
os.makedirs(output_dir, exist_ok=True)

for patch_name in patch_names:

    patch_df = get_patch(data, patch_name)

    if patch_df.shape[0] < 2:
        print(f"{patch_name}: not enough stars")
        continue
    else:
        print(f"{patch_name}: {len(patch_df)} stars found")

    patch_dir = os.path.join(output_dir, patch_name, datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(patch_dir, exist_ok=True)

    num_clusters_by_c = []
    max_cluster_size_by_c = []
    size_dist_by_c = {}

    for c in c_range:

        print(f"Running {patch_name} : c={c}")

        c_dir = os.path.join(patch_dir, f"c_{c}")
        os.makedirs(c_dir, exist_ok=True)

        t = get_coords_and_brightness(patch_df, c=c)
        coords, brightness, skycoords = t[0], t[1], t[2]
        x = coords[:,0]
        y = coords[:,1]

        g = run_sdrg(
            n=len(x),
            neg_x_lim=0, x_lim=float(x.max()) + 1,
            neg_y_lim=0, y_lim=float(y.max()) + 1,
            random=False,
            inp=(x, y, brightness),
            percolation_stats=True,
            skycoords=skycoords,
            patch_name=patch_name,
            output_dir=c_dir)

        plot_star_map(skycoords, g, iteration="final", output_dir=c_dir)
        final_visualization(g, skycoords, patch_name, c_dir)

        cluster_sizes = Counter()
        for members in g.group_ids.values():
            cluster_sizes[len(members)] += 1 

        sizes = [len(members) for members in g.group_ids.values()]
        num_clusters_by_c.append(len(sizes))
        max_cluster_size_by_c.append(max(sizes) if sizes else 0)
        size_dist_by_c[c] = sizes

    fig, ax = plt.subplots()
    ax.plot(c_range, num_clusters_by_c, marker='o')
    ax.set_xlabel("c"); ax.set_ylabel("Final number of clusters")
    ax.set_title(f"{patch_name}: num clusters vs c")
    fig.savefig(os.path.join(patch_dir, "num_clusters_vs_c.png"))
    plt.close(fig)

    fig, ax = plt.subplots()
    ax.plot(c_range, max_cluster_size_by_c, marker='o', color='darkorange')
    ax.set_xlabel("c"); ax.set_ylabel("Final max cluster size")
    ax.set_title(f"{patch_name}: max cluster size vs c")
    fig.savefig(os.path.join(patch_dir, "max_cluster_size_vs_c.png"))
    plt.close(fig)

    print(f"Done: {patch_name} ({len(c_range)} runs)")