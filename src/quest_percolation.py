
import os
import json
import glob
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.coordinates import Angle
from data_handling.star_io import get_all_star_data, get_coords_and_brightness, get_patch
import matplotlib.cm as cm
import numpy as np
import colorcet as cc
import holoviews


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

    diff_num_clusters = np.gradient(num_clusters_by_c)
    a = diff_num_clusters[np.argmax(diff_num_clusters)]
    ind_nc = c_range[np.argmax(diff_num_clusters)]

    diff_size_clusters = np.gradient(max_cluster_size_by_c)
    b = diff_size_clusters[np.argmax(diff_size_clusters)]
    ind_cs = c_range[np.argmax(diff_size_clusters)]

    '''
    
    '''
    print(f"Peak cluster num delta {a} at c={ind_nc}")
    print(f"Peak cluster size delta {b} at c={ind_cs}")

 
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


def final_sky_visualization(quest_dir, c=1.4, patch=False, patch_name="Ori"):
    c_dir = os.path.join(quest_dir, f"c_{c}")
    clusters_path = os.path.join(c_dir, "star_clusters.json")
 
    with open(clusters_path) as f:
        star_clusters = json.load(f)
 
    data = get_all_star_data()
    coords, brightness, skycoords = get_coords_and_brightness(data, c=c)
 
    ra = coords[:, 0]
    dec = coords[:, 1]
    n = len(ra)

    cluster_ids = np.full(n, -1, dtype=int)
    hr_numbers = data["HR"].astype(str).str.strip().to_numpy()
    for i, hr in enumerate(hr_numbers):
        info = star_clusters.get(hr) or star_clusters.get(str(int(hr)))
        if info is not None:
            cluster_ids[i] = int(info["cluster_id"])
 
    colors = np.array(cc.glasbey_hv)[np.array(cluster_ids)%255]
 
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(ra, dec, c=colors, s=brightness/4, lw=0, zorder=3)
 
    ax.set_title("SDRG final clusters")
    ax.set_xlabel("RA (deg)")
    ax.set_ylabel("Dec (deg)")
    ax.set_aspect('equal')
 
    fig.savefig(os.path.join(c_dir, "final_clusters.png"), dpi=500)
    plt.close(fig)

    if patch == True:

        patch_df = get_patch(data, patch_name)

        if patch == True:
    
            patch_df = get_patch(data, patch_name)
    
            if patch_df.shape[0] == 0:
                print(f"No stars found for patch '{patch_name}', skipping patch visualization")
                fig.savefig(os.path.join(c_dir, "final_clusters.png"))
                plt.close(fig)
                return
    
            patch_hr = set(patch_df["HR"].astype(str).str.strip())
            patch_mask = np.array([hr in patch_hr for hr in hr_numbers])
    
            patch_ra = ra[patch_mask]
            patch_dec = dec[patch_mask]
    
            ra_min, ra_max = patch_ra.min(), patch_ra.max()
            dec_min, dec_max = patch_dec.min(), patch_dec.max()
    
            # padding
            ra_pad = max((ra_max - ra_min) * 0.1, 0.5)
            dec_pad = max((dec_max - dec_min) * 0.1, 0.5)
    
            box_ra_min, box_ra_max = ra_min - ra_pad, ra_max + ra_pad
            box_dec_min, box_dec_max = dec_min - dec_pad, dec_max + dec_pad
    
            ax.plot(
                [box_ra_min, box_ra_max, box_ra_max, box_ra_min, box_ra_min],
                [box_dec_min, box_dec_min, box_dec_max, box_dec_max, box_dec_min],
                linestyle=':', color='red', linewidth=1.5, zorder=4,)
    
            processed_data_dir = os.path.dirname(os.path.normpath(quest_dir))
            patch_output_dir = os.path.join(processed_data_dir, patch_name)
            os.makedirs(patch_output_dir, exist_ok=True)
    
            fig.savefig(os.path.join(patch_output_dir, f"full_sky_with_patch_box_c={c}.png"))
    
            zoom_margin = 2.0  
            zoom_ra_min, zoom_ra_max = box_ra_min - zoom_margin, box_ra_max + zoom_margin
            zoom_dec_min, zoom_dec_max = box_dec_min - zoom_margin, box_dec_max + zoom_margin
    
            zoom_mask = (
                (ra >= zoom_ra_min) & (ra <= zoom_ra_max) &
                (dec >= zoom_dec_min) & (dec <= zoom_dec_max)
            )
    
            fig_zoom, ax_zoom = plt.subplots(figsize=(8, 6))
            ax_zoom.scatter(ra[zoom_mask], dec[zoom_mask], c=colors[zoom_mask],
                         s=(np.log(brightness[zoom_mask]))*8, zorder=3)
    
            ax_zoom.plot(
                [box_ra_min, box_ra_max, box_ra_max, box_ra_min, box_ra_min],
                [box_dec_min, box_dec_min, box_dec_max, box_dec_max, box_dec_min],
                linestyle=':', color='red', linewidth=1.5, zorder=4,
            )
    
            ax_zoom.set_xlim(zoom_ra_max, zoom_ra_min) 
            ax_zoom.set_ylim(zoom_dec_min, zoom_dec_max)
    
            ax_zoom.set_title(f"{patch_name}: close-up with c={c}")
            ax_zoom.set_xlabel("RA (deg)")
            ax_zoom.set_ylabel("Dec (deg)")
            ax_zoom.set_aspect('equal')
    
            fig_zoom.savefig(os.path.join(patch_output_dir, f"{patch_name}_closeup_c={c}.png"))
            plt.close(fig_zoom)
    
            print(f"Saved patch box + close-up for '{patch_name}' to {patch_output_dir}")
    
        fig.savefig(os.path.join(c_dir, "final_clusters.png"))
        plt.close(fig)

c = [0.0, 1.0, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.50, 1.55, 1.6, 2.0, 3.0, 4.0, 5.0]

quest_dir = "data/processed_data/QUEST"
plot_full_sky(quest_dir, label="QUEST")

for i in c:
    final_sky_visualization(quest_dir, patch=True, patch_name="UMa", c=i)
