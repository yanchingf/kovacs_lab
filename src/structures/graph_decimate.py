
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


def search(graph): # helper func for finding largest interaction

    active = [i for i, n in graph.nodes.items() if n.active]
    
    curr = (-1, None, None)
    best_distance_edge = (-1, None, None)
    
    if len(active) == 0:
        return curr

    for node_id in active:
        if 1/max(1e-20, graph.nodes[node_id].range) > curr[0]:
            curr = (graph.nodes[node_id].range, node_id, "Node")

        for v in active:
            if v > node_id:
                weight = graph.adj[node_id][v]
                if weight > 0:
                    if in_range(graph, node_id, v):
                        if weight > best_distance_edge[0]: # distance based edges should have priority
                            best_distance_edge = (weight, (node_id, v), "Edge")
                        elif weight == best_distance_edge[0]: # prioritize brighter edge cover if same 1/d
                            curr_brightness = graph.nodes[node_id].range + graph.nodes[v].range
                            best_u, best_v = best_distance_edge[1]
                            best_brightness = graph.nodes[best_u].range + graph.nodes[best_v].range
                            if curr_brightness > best_brightness:
                                best_distance_edge = (weight, (node_id, v), "Edge")
                    else:
                        if weight > curr[0]: # new edges compete with nodes based on literal value
                            curr = (weight, (node_id, v), "Edge")

        has_distance_edge = [graph.adj[node_id][v] > 0 and in_range(graph, node_id, v)
                            for v in active if v != node_id]
        
        if len(has_distance_edge) <= 0 and graph.nodes[node_id].range > curr[0]:
            curr = (graph.nodes[node_id].range, node_id, "Node")

    if best_distance_edge[1] != None:
        return best_distance_edge

    return curr


def filter_bond(graph, k ,neighbors=None):  # k is about to be decimated

    if neighbors is None:
        neighbors = [v.id for v in graph.nodes if v.active == True and graph.adj[v][k] > 0] # 

    l = len(neighbors)

    if l <= 0:
        return -1

    c = 0

    for i in range(l-1):
        for j in range(i+1, l):
            ni = neighbors[i]
            nj = neighbors[j]
            if (graph.adj[k][ni] > graph.adj[ni][nj] and graph.adj[k][nj] > graph.adj[ni][nj]):
                new_bond = graph.adj[ni][k] + graph.adj[nj][k] - graph.nodes[k].range
                if (new_bond > graph.adj[ni][nj]):
                    graph.adj[ni][nj] = 0
                    c += 1

    return c


def decimate(graph, obj):  # decimate node / edge

    if obj[2] == "Node":

        node_id = obj[1]
        node_range = obj[0]

        neighbors = [v for v in range(graph.length) if (graph.adj[node_id][v] > 0 
                     and graph.nodes[v].active) and in_range(graph, node_id, v)]

        c = filter_bond(graph, node_id, neighbors=neighbors)
        print(f"Num bonds filtered while decimating {node_id}: {c}")

        r = len(neighbors)

        for i in range(r): 
            for j in range(i+1, r):
                    
                ni, nj = neighbors[i], neighbors[j]
                J_ij = graph.adj[node_id][ni]
                J_ik = graph.adj[node_id][nj]

                # largest term field => new couplings generated,
                # each calculated with strength J_jk ~= J_ij*J_ik / h_i

                new_strength = max(graph.adj[ni][nj], J_ij * J_ik / node_range)
                graph.adj[ni][nj] = new_strength
                graph.adj[nj][ni] = new_strength
                
        graph.set_node_status(node_id, False)

        for v in neighbors:
            graph.remove_edge(node_id, v)

    else:

        # if coupling, connected sites i and j go into same cluster
        u, v = graph.nodes[obj[1][0]], graph.nodes[obj[1][1]]
        if v.range > u.range:
            u, v = v, u
        v_id = v.id

        if in_range(graph, u.id, v_id):
            new_traverse = max(0, u.range + v.range - graph.adj[u.id][v_id])
        else:
            new_traverse = u.range # negative safeguard

        for k in range(graph.length):
            if not (k == u.id or k == v_id):
                best = max(graph.adj[u.id][k], graph.adj[v_id][k])
                graph.adj[u.id][k] = best
                graph.adj[k][u.id] = best

        graph.merge_clusters(u.id, v.cluster_id)
        u.range = new_traverse

        for vv in graph.nodes.values(): # update for rest in cluster
            if vv.cluster_id == u.cluster_id and vv.active:
                vv.range = new_traverse

        graph.set_node_status(v_id, False)
        for k in range(graph.length):
            if graph.adj[v_id][k] > 0:
                graph.remove_edge(v_id, k)

    return


def repair(graph): # only check affected

    n = len(graph.nodes)

    for i in range(n): # repair edge iff in range
        for j in range(i + 1, n):

            if (graph.nodes[j].active and graph.nodes[i].active) and in_range(graph, i, j):

                if graph.adj[i][j] == 0: # check for deleted edges?

                    d = np.linalg.norm(graph.nodes[i].pos - graph.nodes[j].pos)
                    graph.add_edge(i, j, 1/max(d, 1e-9))
           
    return graph   