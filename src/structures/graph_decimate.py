
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import heapq
import math
import random
from src.structures.graph import Graph
from src.structures.graph import angular_sep
from src.structures import graph_decimate_kernel

import numpy as np

from sklearn.neighbors import BallTree
import numpy as np


def in_range(graph, u, v):

    d = graph.adj[u][v]
    return d <= graph.nodes[u].range and d <= graph.nodes[v].range

def search_k(graph):
    n = graph.length
    adj = np.asarray(graph.adj, dtype=np.float64)[:n, :n]
    adj = np.ascontiguousarray(adj)
    ranges = np.array([graph.nodes[i].range for i in range(n)], dtype=np.float64)
    active = np.array([graph.nodes[i].active for i in range(n)], dtype=bool)
    i, j = graph_decimate_kernel.search_kernel(adj, ranges, active, n)
    return (i, j)

def search(graph):

    active = [i for i, node in graph.nodes.items() if node.active]
    active_set = set(active)

    # pass 1: decimate any available coupling before doing fields
    for i in active:

        for j in active:

            if i == j:
                continue

            d = graph.adj[i][j]

            if d <= graph.nodes[i].range and d > 0 and d <= graph.nodes[j].range:
                return (i, j)

    best = None
    best_degree = None

    for i in active:

        can_reach = False
        degree = 0

        for j in active:

            if i == j:
                continue

            d = graph.adj[i][j]

            if d > 0:
                degree += 1

            if d <= graph.nodes[i].range and d > 0:
                can_reach = True

        if can_reach == False:
            if best is None or degree < best_degree:
                best = i
                best_degree = degree

    if best is not None:
        return (best, None)

    return (None, None)


def filter_bond(graph, k ,neighbors=None):  # k is about to be decimated

    if neighbors is None:
        neighbors = [v.id for v in graph.nodes.values() if v.active == True and graph.adj[v.id][k] > 0] # 

    l = len(neighbors)

    if l <= 0:
        return -1

    c = 0

    t_k = graph.nodes[k].range

    for i in range(l-1):
        for j in range(i+1, l):

            ni = neighbors[i]
            nj = neighbors[j]

            if graph.adj[ni][nj] <= 0:
                continue

            d_ij = graph.adj[ni][nj]
            d_ik = graph.adj[k][ni]
            d_jk = graph.adj[k][nj]

            if d_ik < d_ij and d_jk < d_ij:
                new_d = d_ik + d_jk - t_k
                if new_d < d_ij:
                    graph.adj[ni][nj] = -1
                    graph.adj[nj][ni] = -1
                    c += 1

    return c


def decimate(graph, obj, filter=False):  # decimate node / edge

    total_filtered = 0

    updated = []

    if obj[1] is None:

        node_id = obj[0]
        node_range = graph.nodes[node_id].range

        neighbors = [v for v in range(graph.length) if (graph.adj[node_id][v] > 0 
                     and graph.nodes[v].active) and in_range(graph, node_id, v)]

        r = len(neighbors)

        if filter == True:
            filter_bond(graph, node_id, neighbors=neighbors)

        for i in range(r): 
            for j in range(i+1, r):
                    
                ni, nj = neighbors[i], neighbors[j]
                J_ij = graph.adj[node_id][ni]
                J_ik = graph.adj[node_id][nj]

                # largest term field => new couplings generated,
                # each calculated with strength J_jk ~= J_ij*J_ik / h_i

                new_strength = max(graph.adj[ni][nj], J_ij * J_ik / node_range)

                if graph.adj[ni][nj] != new_strength:
                    updated.append(ni)
                    updated.append(nj)

                graph.adj[ni][nj] = new_strength
                graph.adj[nj][ni] = new_strength
                
        graph.set_node_status(node_id, False)

        for v in neighbors:
            graph.remove_edge(node_id, v)

    else:

        # if coupling, connected sites i and j go into same cluster
        u, v = graph.nodes[obj[0]], graph.nodes[obj[1]]
        if v.range > u.range:
            u, v = v, u
        v_id = v.id

        updated.append(u.id)
        updated.append(v.id)

        if in_range(graph, u.id, v_id):
            new_traverse = max(0, u.range + v.range - graph.adj[u.id][v_id])
        else:
            new_traverse = u.range # negative safeguard

        for k in range(graph.length):

            if not (k == u.id or k == v_id):
 
                d_uk = graph.adj[u.id][k]
                d_vk = graph.adj[v_id][k]
 
                if d_uk > 0 and d_vk > 0:
                    best = min(d_uk, d_vk)
                elif d_uk > 0:
                    best = d_uk
                elif d_vk > 0:
                    best = d_vk
                else:
                    best = 0
 
                graph.adj[u.id][k] = best
                graph.adj[k][u.id] = best

        graph.merge_clusters(u.id, v.cluster_id)
        u.range = new_traverse

        for vv in graph.nodes.values(): # update for rest in cluster
            if vv.cluster_id == u.cluster_id and vv.active:
                vv.range = new_traverse
                updated.append(vv.id)

        if filter == True:
            c = filter_bond(graph, u.id)
            print(f"Filtered {c} bonds merging into node {u.id}")
            total_filtered += c

        graph.set_node_status(v_id, False)
        for k in range(graph.length):
            if graph.adj[v_id][k] > 0:
                graph.remove_edge(v_id, k)

    return total_filtered, list(dict.fromkeys(updated))


def find_sep(graph, n_i, n_j):
    if getattr(graph, "use_sky_coords", True):
        return angular_sep(n_i.ra, n_i.dec, n_j.ra, n_j.dec)
    return np.linalg.norm(n_i.pos - n_j.pos)


def repair(graph, to_repair=None):
 
    candidates = []
 
    n = len(graph.nodes)
    tree = getattr(graph, "tree", None)
    use_sky = getattr(graph, "use_sky_coords", False)
 
    if to_repair is not None:
 
        ids = sorted(to_repair)
 
        for t_i in ids:
 
            node_i = graph.nodes[t_i]
            if not node_i.active:
                continue
 
            if tree is not None:
                # radius just this node's neighborhood
                # instead of scanning every other node
                r = np.radians(node_i.range) if use_sky else node_i.range
                cand = tree.query_radius(graph.tree_coords[t_i:t_i + 1], r=r)[0]
            else:
                cand = range(n)
 
            for j in cand:
 
                if t_i == j:
                    continue
 
                if graph.nodes[j].active and in_range(graph, t_i, j):
 
                    if graph.adj[t_i][j] == 0:
                        d = find_sep(graph, node_i, graph.nodes[j])
                        graph.add_edge(t_i, j, d)

                        if hasattr(graph, "adj_list") and graph.adj_list is not None:
                            graph.adj_list.setdefault(t_i, {})[j] = d
                            graph.adj_list.setdefault(j, {})[t_i] = d

                        candidates.append(t_i)
                        candidates.append(j)
 
    else:
        for i in range(n):
            for j in range(i + 1, n):
 
                if graph.nodes[i].active and graph.nodes[j].active and in_range(graph, i, j):
 
                    if graph.adj[i][j] == 0:
                        d = find_sep(graph, graph.nodes[i], graph.nodes[j])
                        graph.add_edge(i, j, d)
                        candidates.append(i)
                        candidates.append(j)
 
    return graph, list(dict.fromkeys(candidates))