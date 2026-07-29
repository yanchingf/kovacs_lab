
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import heapq
import math
import random
from src.structures.graph import Graph
from src.structures.graph_decimate import filter_bond

import numpy as np


def smart_search(graph):

    active = [i for i, node in graph.nodes.items() if node.active]

    zones = {} # {node: dist} within r_i/2
    for i in active:
        r_i = graph.nodes[i].range
        zones[i] = graph.djikstra(i, max_dist=r_i / 2)

    for i in active:
        for j in active:
            if i == j:
                continue
            r_i = graph.nodes[i].range
            r_j = graph.nodes[j].range

            if zones[i][j] < float("inf"): 
                d_ij = zones[i][j]
            else: 
                arr = graph.djikstra(i, max_dist=r_i)
                d_ij = arr[j]

            if d_ij <= r_i and d_ij <= r_j:
                return (i, j)

    for i in active:
        r_i = graph.nodes[i].range
        full = graph.djikstra(i, max_dist=r_i)
        if all(full[j] > r_i for j in active if j != i):
            return (i, None)

    return (None, None)


def smart_decimate(graph, obj, filter=False):  # decimate node / edge

    total_filtered = 0

    updated = []

    if obj[1] is None:

        node_id = obj[0]
        node_range = graph.nodes[node_id].range

        dist_from_node = graph.djkstra(node_id, max_dist=node_range)

        neighbors = [v for v in range(graph.length) if (graph.nodes[v].active
                     and v != node_id and dist_from_node[v] <= node_range
                     and dist_from_node[v] <= graph.nodes[v].range)]

        r = len(neighbors)

        if filter == True:
            filter_bond(graph, node_id, neighbors=neighbors)

        for i in range(r): 
            for j in range(i+1, r):

                ni, nj = neighbors[i], neighbors[j]

                if graph.adj[ni][nj] == -1:
                    continue

                d_ik = dist_from_node[ni]
                d_jk = dist_from_node[nj]
                candidate = d_ik + d_jk

                if graph.adj[ni][nj] > 0:
                    new_dist = min(graph.adj[ni][nj], candidate)
                else:
                    new_dist = candidate

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

        dist_from_u = graph.dijkstra(u.id, max_dist=max(u.range, v.range))
        d_uv = dist_from_u[v_id]

        if d_uv <= u.range and d_uv <= v.range:
            new_traverse = max(0, u.range + v.range - d_uv)
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