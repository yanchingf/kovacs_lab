
import os
import json
import glob
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.coordinates import Angle

def load_stats(patch_dir):

    records = []
    for stats_path in sorted(glob.glob(os.path.join(patch_dir, "c_*", "stats.json"))):
        with open(stats_path) as f:
            stats = json.load(f)
        records.append((stats["c"], stats["num_clusters"], stats["max_cluster_size"]))
    records.sort(key=lambda r: r[0])
    return records


def plot_full_sky(quest_dir, label=None):
    label = label or os.path.basename(os.path.normpath(quest_dir))
 
    records = load_stats(quest_dir)
    if not records:
        print(f"No stats.json files found under {quest_dir}")
        return
 
    c_range, num_clusters_by_c, max_cluster_size_by_c = zip(*records)
 
    fig, ax = plt.subplots()
    ax.plot(c_range, num_clusters_by_c, marker='o')
    ax.set_xlabel("c"); ax.set_ylabel("Final number of clusters")
    ax.set_title(f"{label}: num clusters vs c")
    fig.savefig(os.path.join(quest_dir, "num_clusters_vs_c.png"))
    plt.close(fig)
 
    fig, ax = plt.subplots()
    ax.plot(c_range, max_cluster_size_by_c, marker='o', color='darkorange')
    ax.set_xlabel("c"); ax.set_ylabel("Final max cluster size")
    ax.set_title(f"{label}: max cluster size vs c")
    fig.savefig(os.path.join(quest_dir, "max_cluster_size_vs_c.png"))
    plt.close(fig)
 
    print(f"Saved plots to {quest_dir}")


def final_visualization(g, skycoords, patch_name, output_dir, c=1.4):

    

    fig, ax = plt.subplots(figsize=(8, 6))

    n = len(ra)

    for i in range(n):
        color = cm.tab10(g.nodes[i].cluster_id % 10)
        rr = g.nodes[i].range

        ax.scatter(ra[i], dec[i], c=[color], zorder=3)

    ax.set_title(f"{patch_name}: SDRG final clusters")
    ax.set_xlabel("RA (deg)")
    ax.set_ylabel("Dec (deg)")
    ax.set_aspect('equal')

    fig.savefig(os.path.join(output_dir, f"final_clusters.png"))
    plt.close(fig)


quest_dir = "data/processed_data/QUEST"
plot_full_sky(quest_dir, label="QUEST")