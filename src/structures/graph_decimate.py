
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import heapq
import math
import random
from src.structures.graph import Graph

import numpy as np


def in_range(graph, u, v):

    d = graph.adj[u][v]
    return d <= graph.nodes[u].range and d <= graph.nodes[v].range


def search(graph):

    active = [i for i, node in graph.nodes.items() if node.active]

    couplings = []

    # pass 1: decimate any available coupling before doing fields
    for i in active:

        for j in active:

            if i == j:
                continue

            d = graph.adj[i][j]

            if d <= graph.nodes[i].range and d > 0 and d <= graph.nodes[j].range:
                couplings.append([i,j])

    # pass 2: no couplings left, pick smallest-degree local-max field

    fields = [] # i, degree

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

        # i cannot reach any other active site
        if can_reach == False:
            fields.append([i, degree])

    if len(active) <= 1 or not fields:
        return couplings, (None, None)

    if len(fields) >= len(active) - 1: # step 3
        keep_id = min(fields, key=lambda t: graph.nodes[t[0]].range)[0]
        to_remove = [i for i, j in fields if i != keep_id]

        return couplings, (keep_id, to_remove)

    best_id = min(fields, key=lambda t: t[1])[0]
    return couplings, (best_id, None)


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

    couplings, fields = obj

    total_filtered = 0
    updated = set()

    for i, j in couplings:

        # skip if inactive
        if not graph.nodes[i].active or not graph.nodes[j].active:
            continue

        # if coupling, connected sites i and j go into same cluster
        u, v = graph.nodes[i], graph.nodes[j]
        if v.range > u.range:
            u, v = v, u
        v_id = v.id

        updated.add(u.id)
        updated.add(v.id)

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
                updated.add(vv.id)

        graph.set_node_status(v_id, False)
        for k in range(graph.length):
            if graph.adj[v_id][k] > 0:
                graph.remove_edge(v_id, k)

    keep_id, to_remove = fields
    field_ids = [keep_id] + (to_remove if to_remove else [])

    for node_id in field_ids:

        if not graph.nodes[node_id].active:
            continue

        node_range = graph.nodes[node_id].range

        neighbors = [v for v in range(graph.length) if (graph.adj[node_id][v] > 0
                     and graph.nodes[v].active) and in_range(graph, node_id, v)]

        updated.update(neighbors)

        r = len(neighbors)

        if filter == True:
            c = filter_bond(graph, node_id, neighbors=neighbors)
            print(f"Filtered {c} bonds decimating {node_id}")
            total_filtered += c

        for i in range(r):
            for j in range(i+1, r):

                ni, nj = neighbors[i], neighbors[j]

                if graph.adj[ni][nj] == -1:
                    continue

                d_ik = graph.adj[node_id][ni]
                d_jk = graph.adj[node_id][nj]

                candidate = d_ik + d_jk

                if graph.adj[ni][nj] > 0:
                    new_dist = min(graph.adj[ni][nj], candidate)
                else:
                    new_dist = candidate

                # largest term field => new couplings generated,
                # each calculated with strength J_jk ~= J_ij*J_ik / h_i

                if graph.adj[ni][nj] != new_dist:
                    updated.add(ni)
                    updated.add(nj)

                graph.adj[ni][nj] = new_dist
                graph.adj[nj][ni] = new_dist

        graph.set_node_status(node_id, False)

        for v in neighbors:
            graph.remove_edge(node_id, v)

    return total_filtered, updated


def repair(graph, to_repair=None):

    n = len(graph.nodes)

    if to_repair is not None:

        n = len(to_repair)
        ids = sorted(to_repair)
        all_ids = len(graph.nodes)

        for i in range(n):
            for j in range(all_ids):

                if i == j :
                    continue

                t_i = ids[i]

                if graph.nodes[t_i].active and graph.nodes[j].active and in_range(graph, t_i, j):

                    if graph.adj[t_i][j] == 0:
                        d = np.linalg.norm(graph.nodes[t_i].pos - graph.nodes[j].pos)
                        graph.add_edge(t_i, j, d)

    else: 
        for i in range(n):
            for j in range(i + 1, n):

                if graph.nodes[i].active and graph.nodes[j].active and in_range(graph, i, j):

                    if graph.adj[i][j] == 0:
                        d = np.linalg.norm(graph.nodes[i].pos - graph.nodes[j].pos)
                        graph.add_edge(i, j, d)

    return graph