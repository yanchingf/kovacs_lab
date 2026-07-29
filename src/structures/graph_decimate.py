
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

    for i in active:

        can_reach = False

        for j in active:

            if i == j:
                continue

            d = graph.adj[i][j]

            if d <= graph.nodes[i].range and d > 0:
                can_reach = True

                if d <= graph.nodes[j].range:
                    return (i, j)

        # i cannot reach any other active site
        if can_reach == False:
            return (i, None)

    return (None, None)


def filter_bond(graph, k ,neighbors=None):  # k is about to be decimated

    if neighbors is None:
        neighbors = [v.id for v in graph.nodes.values() if v.active == True and graph.adj[v.id][k] > 0] # 

    l = len(neighbors)

    if l <= 0:
        return -1

    c = 0

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
                new_d = d_ik + d_jk
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
            c = filter_bond(graph, node_id, neighbors=neighbors)
            print(f"Filtered {c} bonds decimating {node_id}")

        for i in range(r): 
            for j in range(i+1, r):

                if graph.adj[ni][nj] == -1:
                    continue
                    
                ni, nj = neighbors[i], neighbors[j]
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
                    updated.append(ni)
                    updated.append(nj)

                graph.adj[ni][nj] = new_dist
                graph.adj[nj][ni] = new_dist
                
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

        graph.set_node_status(v_id, False)
        for k in range(graph.length):
            if graph.adj[v_id][k] > 0:
                graph.remove_edge(v_id, k)

    return total_filtered


def repair(graph):

    n = len(graph.nodes)

    for i in range(n):
        for j in range(i + 1, n):

            if graph.nodes[i].active and graph.nodes[j].active and in_range(graph, i, j):

                if graph.adj[i][j] == 0:
                    d = np.linalg.norm(graph.nodes[i].pos - graph.nodes[j].pos)
                    graph.add_edge(i, j, d)

    return graph