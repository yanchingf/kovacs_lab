
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches

from data_handling.star_io import parse_star_data
from data_handling.star_io import save_processed_data
from data_handling.star_io import get_coords_and_brightness

from structures.graph import Graph
from structures.graph import build_graph
from structures.graph_decimate import decimate
from structures.graph_decimate import search
from src.data_handling.random_test import generate_random_graph

from astropy import units as u
from astropy.coordinates import Angle


def star_to_graph_mapping(skycoords): # need to update per iteration

    t = get_coords_and_brightness(skycoords)
    starcoords, brightness = t[0], t[1]

    n = skycoords.shape[0]
    coords = [[0,0] for i in range(n)]

    for i in range(n):
        ra = starcoords[i].ra
        dec = starcoords[i].dec
        coords[i][0], coords[i][1] = ra, dec

    return build_graph(coords, brightness)


def get_k_neighbors(coord, skycoords, df, k=5): # get k closest stars from catalogue to the coord, check
    
    seps = coord.separation(skycoords)
    k = min(k, len(df))

    nearest_idx = np.argsort(seps)[:k]

    neighbor_df = df.iloc[nearest_idx].reset_index(drop=True)
    neighbor_seps = seps[nearest_idx]

    return neighbor_df, neighbor_seps


def plot_star_map(starcoords, graph, iteration, output_dir, patch_name=None, use_mollweide=False):

    n = len(starcoords)

    ra = Angle(starcoords.ra).wrap_at(180 * u.deg)
    dec = Angle(starcoords.dec)

    fig = plt.figure(figsize=(8, 6))
    if use_mollweide:
        ax = fig.add_subplot(111, projection="mollweide")
    else:
        ax = fig.add_subplot(111)
        ax.set_xlabel("RA (deg)")
        ax.set_ylabel("Dec (deg)")

    ra_vals = ra.radian if use_mollweide else ra.to_value(u.deg)
    dec_vals = dec.radian if use_mollweide else dec.to_value(u.deg)

    for i in range(n-1):
        if graph.nodes[i].active == True:
            for j in range(i+1, n):
                if graph.nodes[j].active and graph.adj[i][j] > 0:
                    ax.plot([ra_vals[i], ra_vals[j]], [dec_vals[i], dec_vals[j]],
                            color='gray', lw=0.8, alpha=0.5, zorder=1)
                    
    for i in range(n):

        color = cm.tab10(graph.nodes[i].cluster_id % 10) if graph.nodes[i].active else "gray"

        ax.scatter(ra_vals[i], dec_vals[i], c=[color], s=40, zorder=3,)
        ax.annotate(f"id={i}", (ra_vals[i], dec_vals[i]), xytext=(5, 5),
            textcoords="offset points", fontsize=7,)
        ax.annotate(f"cluster={graph.nodes[i].cluster_id}", (ra_vals[i], dec_vals[i]),
            xytext=(5, 15), textcoords="offset points", fontsize=5,)

    title = f"{patch_name} — Step {iteration}" if patch_name else f"Step {iteration}"
    ax.set_title(title)
    ax.grid(True)

    if use_mollweide == False:
        pad_ra = (ra_vals.max() - ra_vals.min()) * 0.1 + 0.5
        pad_dec = (dec_vals.max() - dec_vals.min()) * 0.1 + 0.5
        ax.set_xlim(ra_vals.min() - pad_ra, ra_vals.max() + pad_ra)
        ax.set_ylim(dec_vals.min() - pad_dec, dec_vals.max() + pad_dec)

    fig.savefig(os.path.join(output_dir, f"step_{iteration}.png"))
    plt.close(fig)
        

def final_visualization(g, skycoords, patch_name, output_dir, size_scale=20):

    ra = Angle(skycoords.ra).wrap_at(180 * u.deg).to_value(u.deg)
    dec = Angle(skycoords.dec).to_value(u.deg)

    fig, ax = plt.subplots(figsize=(8, 6))

    n = len(ra)

    for i in range(n):
        color = cm.tab10(g.nodes[i].cluster_id % 10)
        rr = g.nodes[i].range

        ax.scatter(ra[i], dec[i], c=[color], s=max(5, rr * size_scale), zorder=3)

    ax.set_title(f"{patch_name}: SDRG final clusters")
    ax.set_xlabel("RA (deg)")
    ax.set_ylabel("Dec (deg)")
    ax.set_aspect('equal')

    fig.savefig(os.path.join(output_dir, f"final_clusters.png"))
    plt.close(fig)
