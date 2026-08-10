
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches
from datetime import datetime

from structures.graph import Graph
from structures.graph import build_graph
from structures.graph_decimate import decimate
from structures.graph_decimate import filter_bond 
from structures.graph_decimate import search
from structures.graph_decimate import in_range
from structures.graph_decimate import repair
from structures.smart_decimate import smart_search, smart_search_v2, smart_decimate

from src.data_handling.random_test import generate_random_graph
from src.stars import plot_star_map

from collections import Counter


def plot_graph(g, points, n, iteration, neg_x_lim=0, x_lim=5000, neg_y_lim=0, y_lim=5000,
               output_dir=os.path.join(os.path.dirname(__file__), '..', 'tests','test-plots')):
    
    os.makedirs(output_dir, exist_ok=True)

    x, y, colors, sizes = [], [], [], []
    num_cluster = 0

    fig, ax = plt.subplots()

    for i in range(n):

        x.append(points[0][i])
        y.append(points[1][i])

        colors.append(g.nodes[i].cluster_id)
        sizes.append(max(0.001, g.nodes[i].range))

    for i in range(n):
        if g.nodes[i].active:
            num_cluster = max(num_cluster, g.nodes[i].cluster_id + 1)
            for j in range(i+1, n):
                if g.nodes[j].active and g.adj[i][j] > 0 and in_range(g, i, j):
                    plt.plot([points[0][i], points[0][j]],
                            [points[1][i], points[1][j]],
                            color='gray', lw=0.8, alpha=0.5, zorder=1)
                

    for i in range(n): # add radius and nodes
        xx, yy = points[0][i], points[1][i]
        rr = g.nodes[i].range
        color = cm.tab10(g.nodes[i].cluster_id % 10) if g.nodes[i].active else "gray"

        ax.add_patch(mpatches.Circle((xx, yy), radius=rr, fill=True,
                                    facecolor=color, alpha=0.08, zorder=0))
        ax.annotate(f"id={i}", (xx, yy), textcoords="offset points",
                xytext=(5, 5), fontsize=7, color='black')
        ax.annotate(f"cluster_id={g.nodes[i].cluster_id}", (xx, yy), textcoords="offset points",
                xytext=(5, 15), fontsize=5, color='black')
        ax.scatter(xx, yy, c=[color], s=40, zorder=3)


    ax.set_title(f"SDRG Step {iteration} | {n} nodes")
    ax.set_xlim(neg_x_lim, x_lim)
    ax.set_ylim(neg_y_lim, y_lim)
    ax.set_aspect('equal')
    fig.savefig(os.path.join(output_dir, f"step_{iteration}.png"))
    plt.close(fig)

 
def run_sdrg(n=1, neg_x_lim=0, x_lim=5000, neg_y_lim=0, y_lim=5000, random=True, inp=None,
             percolation_stats=False, skycoords=None, patch_name=None,
             output_dir=os.path.join(os.path.dirname(__file__), '..', 'tests', 'runs'),
             filter_bonds=False, plot_every=1, k_neighbors=None, use_sky_coords=True,
             smart=False):
 
    if random:
        obj = generate_random_graph(n, neg_x_lim, x_lim, neg_y_lim, y_lim)
        g = obj[0]
        points = obj[1]
 
    else:
        if inp == None:
            print("INPUT REQUIRED")
            return
 
        g = build_graph((inp[0], inp[1]), inp[2], neighbors=k_neighbors, use_sky_coords=use_sky_coords)
        points = (inp[0], inp[1])
        n = len(inp[0])
 
    search_fn = smart_search_v2 if smart else search
 
    iteration = 1
 
    curr = search_fn(g)
 
    step_plot_dir = os.path.join(output_dir, "steps")
    stat_output_dir = os.path.join(output_dir, "percolation")
    txt_f = os.path.join(output_dir, "log.txt")
 
    os.makedirs(step_plot_dir, exist_ok=True)
    os.makedirs(stat_output_dir, exist_ok=True)
 
    if skycoords is None:
        plot_graph(g, points, n, iteration=0, neg_x_lim=neg_x_lim, x_lim=x_lim,
                   neg_y_lim=neg_y_lim, y_lim=y_lim, output_dir=step_plot_dir)
    else:
        plot_star_map(skycoords, g, iteration=0, output_dir=step_plot_dir, patch_name=patch_name)
 
    with open(txt_f, "a", encoding="utf-8") as f:
        f.write(f"Step 0 | Ω=initial\n")
        for i in range(n):
            f.write(f"    id={g.nodes[i].id} h={g.nodes[i].range} "
                    f"cluster={g.nodes[i].cluster_id} active={g.nodes[i].active}\n")
 
    n_clusters, max_sizes, size_distro, filtered_counts = [], [], [], []
 
    while curr[0] is not None:
 
        with open(txt_f, "a", encoding="utf-8") as f:
            f.write(f"Step {iteration} | Ω={curr}\n")  # write log
            for i in range(n):
                f.write(f"    id={g.nodes[i].id} h={g.nodes[i].range} cluster={g.nodes[i].cluster_id} active={g.nodes[i].active}\n")
 
        if smart:
            updated = smart_decimate(g, curr)
        elif filter_bonds == True:
            total, updated = decimate(g, curr, filter=True)
            with open(txt_f, "a", encoding="utf-8") as f:
                f.write(f"    filtered {total} bonds this step\n")
            filtered_counts.append(total)
        else:
            total, updated = decimate(g, curr, filter=False)
 
        to_plot = ((iteration % plot_every) == 0)
 
        if to_plot:
            if skycoords is None:
                plot_graph(g, points, n, iteration, neg_x_lim=neg_x_lim, x_lim=x_lim,
                           neg_y_lim=neg_y_lim, y_lim=y_lim, output_dir=step_plot_dir)
            else:
                plot_star_map(skycoords, g, iteration=iteration, output_dir=step_plot_dir, patch_name=patch_name)
 
        iteration += 1
 
        g, repaired_candidates = repair(g, to_repair=updated)
        curr = search_fn(g) if not smart else search_fn(g)
 
        if percolation_stats == True:
            group_sizes = [len(members) for members in g.group_ids.values()]
            n_clusters.append(len(group_sizes))
            max_sizes.append(max(group_sizes) if group_sizes else 0)
            size_distro.append(Counter(group_sizes))
 
    if skycoords is None:
        plot_graph(g, points, n, iteration, neg_x_lim=neg_x_lim, x_lim=x_lim,
                   neg_y_lim=neg_y_lim, y_lim=y_lim, output_dir=step_plot_dir)
    else:
        plot_star_map(skycoords, g, iteration=iteration, output_dir=step_plot_dir, patch_name=patch_name)
 
    if percolation_stats == True:
 
        fig, ax = plt.subplots()
        ax.plot(range(len(n_clusters)), n_clusters, marker='o', linestyle='-', color='b')
        ax.set_title("Number of Clusters by Iteration")
        ax.set_xlabel("Iteration Number")
        ax.set_ylabel("Number of Clusters")
        fig.savefig(os.path.join(stat_output_dir, "num_cluster_plt.png"))
        plt.close(fig)
 
        fig, ax = plt.subplots()
        ax.plot(range(len(max_sizes)), max_sizes, marker="o", linestyle='-', color='r')
        ax.set_title("Max Size of Cluster by Iteration")
        ax.set_xlabel("Iteration Number")
        ax.set_ylabel("Max Size of Cluster")
        fig.savefig(os.path.join(stat_output_dir, "max_cluster_size_plt.png"))
        plt.close(fig)
 
        fig, ax = plt.subplots()
        ax.plot(n_clusters, max_sizes, marker="o", linestyle='-', color='r')
        ax.set_title("Max Cluster Size vs Number of Clusters")
        ax.set_xlabel("Number of Clusters")
        ax.set_ylabel("Max Size of Cluster")
        fig.savefig(os.path.join(stat_output_dir, "max_cluster_v_num_cluster_plt.png"))
        plt.close(fig)
 
        fig, ax = plt.subplots()
        sample_idxs = range(0, len(size_distro), max(1, len(size_distro) // 5))
        for idx in sample_idxs:
            counts = size_distro[idx]
            if counts != None:
                xs = sorted(counts.keys())
                ys = [counts[x] for x in xs]
                ax.plot(xs, ys, marker='o', ms=3, label=f"iter={idx + 1}")
        ax.set_title("Cluster Size Distribution")
        ax.set_xlabel("Cluster size")
        ax.set_ylabel("Count of clusters with that size")
        ax.legend(fontsize=7)
        fig.savefig(os.path.join(stat_output_dir, "cluster_distro_size_plt.png"))
        plt.close(fig)
 
        fig, ax = plt.subplots()
        ax.plot(range(len(filtered_counts)), filtered_counts, marker='o', linestyle='-', color='g')
        ax.set_title("Bonds Filtered per Iteration")
        ax.set_xlabel("Iteration Number")
        ax.set_ylabel("Number of Bonds Filtered")
        fig.savefig(os.path.join(stat_output_dir, "filtered_bonds_plt.png"))
        plt.close(fig)
 
    with open(txt_f, "a", encoding="utf-8") as f:
        f.write(f"Done at iteration {iteration}, plots saved to '{output_dir}/'\n")
 
    return g
 

TEST_CASES = [
     
    ([200, 400], [150, 150], [10, 10]),

    ([200, 400], [150, 150], [250, 250]),

    ([100, 300], [200, 200], [200, 200]),

    ([100, 200, 300, 100, 200, 300, 100, 200, 300],
     [100, 200, 300, 200, 100, 200, 300, 300, 100],
     [150, 300, 10, 150, 150, 10, 10, 10, 10]),

    ([100, 200, 300, 100, 200, 300, 100, 200, 300],
     [100, 200, 300, 200, 100, 200, 300, 300, 100],
     [150, 400, 150, 10, 10, 10, 150, 10, 150]),

    ([100, 200, 300, 100, 200, 300, 100, 200, 300],
     [100, 200, 300, 200, 100, 200, 300, 300, 100],
     [90, 300, 90, 150, 150, 150, 90, 150, 90]),

    ([100, 200, 300, 100, 200, 300, 100, 200, 300],
     [100, 200, 300, 200, 100, 200, 300, 300, 100],
     [110, 300, 110, 150, 150, 150, 110, 150, 110]),

    ([100, 150, 240, 290], [200, 200, 200, 200], [100, 60, 100, 60]),

    ([100, 150, 240, 290], [200, 200, 200, 200], [60, 60, 100, 60]),

    ([100, 200, 300, 300], [100, 100, 100, 300], [120, 120, 120, 250]),

    ([200, 400, 200, 400], [200, 200, 400, 400], [250, 250, 250, 250]),

    ([100, 200, 500], [100, 100, 100], [110, 110, 110]),

    ([100, 200, 150], [100, 100, 186.6], [110, 110, 110]),

    ([99, 100, 200], [300, 300, 300], [99, 99, 199]),

    ([200, 300, 400], [200, 200, 200], [300, 300, 300]),

    ([100, 400, 700], [200, 200, 200], [350, 350, 350]),

    ([300, 100, 300, 500, 300], [300, 300, 100, 300, 500], [210, 210, 210, 210, 210]),
    ([100, 280, 460, 640, 820, 1000], [200, 200, 200, 200, 200, 200], [200, 200, 200, 200, 200, 200]),
    ([200, 400, 450, 700, 850], [200, 200, 200, 200, 200], [220, 220, 220, 220, 220]),
]
 

def run_tests(compare_smart=True):
 
    for x, y, r in TEST_CASES:
 
        n = len(x)
 
        variants = [("naive", False)] + ([("smart", True)] if compare_smart else [])
 
        for variant_name, smart_flag in variants:
 
            out_dir = os.path.join(os.path.dirname(__file__), '..', 'tests', 'sdrg-test-plots-v2',
                                    datetime.now().strftime("%Y%m%d_%H%M%S"))

            if compare_smart:
                flag_file = "smart" if smart_flag==True else "naive"
                out_dir = os.path.join(out_dir, f"{flag_file}")
 
            print(f"Running test case ({variant_name})")
 
            run_sdrg(n, 0, 500, 0, 500, False, (x, y, r), output_dir=out_dir, use_sky_coords=False, smart=smart_flag)
 
# run_tests(compare_smart=True)