
import heapq
from collections import deque
import numpy as np

from src.structures import graph_decimate_kernel

def get_adj_list(graph):
    
    if not hasattr(graph, "adj_list") or graph.adj_list is None:
        adj_list = {i: {} for i in graph.nodes}
        n = graph.length
        for i in range(n):
            for j in range(n):
                if i != j and graph.adj[i][j] > 0:
                    adj_list[i][j] = graph.adj[i][j]
        graph.adj_list = adj_list
    return graph.adj_list

 
def adjlist_remove_edge(graph, i, j):
   
    adj_list = graph.adj_list
    adj_list.get(i, {}).pop(j, None)
    adj_list.get(j, {}).pop(i, None)
 
 
def adjlist_set_edge(graph, i, j, w):
    adj_list = graph.adj_list
    if w > 0:
        adj_list.setdefault(i, {})[j] = w
        adj_list.setdefault(j, {})[i] = w
    else:
        adjlist_remove_edge(graph, i, j)


def adjlist_remove_node(graph, i):
    adj_list = graph.adj_list
    neighbors = adj_list.pop(i, {})
    for j in neighbors:
        adj_list.get(j, {}).pop(i, None)


def build_adjacency_list(graph):
    adj_list = {i: {} for i in graph.nodes}
    n = graph.length
    for i in range(n):
        for j in range(n):
            if i != j and graph.adj[i][j] > 0:
                adj_list[i][j] = graph.adj[i][j]
    return adj_list


def smart_search(graph):

    active = [i for i, node in graph.nodes.items() if node.active]
    if not active:
        return (None, None)

    active_set = set(active)
    adj_list = get_adj_list(graph)

    dist = {}
    heap = []

    attempted = set()

    for s in active:
        dist[s] = (0.0, s)
        heapq.heappush(heap, (0.0, s, s))

    visited_by = {}
    exhausted = set()

    while heap:

        d, node, source = heapq.heappop(heap)

        if source in exhausted:
            continue

        if node in visited_by:
            owner = visited_by[node]
            if owner != source and node in active_set:
                owner_dist = dist[node][0]
                delta = owner_dist + d
                owner_range = graph.nodes[owner].range
                source_range = graph.nodes[source].range
                if delta <= source_range and delta <= owner_range:
                    return ('fuse', owner, source, delta)
            continue

        source_range = graph.nodes[source].range

        if d > source_range:
            exhausted.add(source)
            continue

        visited_by[node] = source
        dist[node] = (d, source)

        for neighbor, w in adj_list.get(node, {}).items():
            nd = d + w
            key = (source, neighbor)
            if nd <= source_range and key not in attempted:
                attempted.add(key)
                heapq.heappush(heap, (nd, neighbor, source))

    for s in active:
        if s in exhausted or not adj_list.get(s):
            return ('inactive', s)

    return ('inactive', active[0])


def smart_search_v2(graph, seeds=None):

    if not hasattr(graph, "_pending"):
        graph._pending = deque(i for i, node in graph.nodes.items() if node.active)
        graph._active_set = set(graph._pending)

    if seeds is not None:
        for s in seeds:
            if s not in graph._pending:
                graph._pending.append(s)

    adj_list = get_adj_list(graph)
    active_set = set(i for i, node in graph.nodes.items() if node.active)

    while graph._pending:
        i = graph._pending.popleft()
        if i not in graph._active_set:
            continue

        r_i = graph.nodes[i].range
        heap = [(0.0, i)]
        visited = set()
        found = None
        can_reach_anyone = False

        while heap:
            d, node = heapq.heappop(heap)
            if node in visited:
                continue
            visited.add(node)

            if node != i and node in active_set and d <= r_i:
                can_reach_anyone = True 
                r_node = graph.nodes[node].range
                if d <= r_node:
                    found = (node, d)
                    break

            if d > r_i:
                break

            for neighbor, w in adj_list.get(node, {}).items():
                nd = d + w
                if nd <= r_i and neighbor not in visited:
                    heapq.heappush(heap, (nd, neighbor))

        if found is not None:
            j, delta = found
            return ('fuse', i, j, delta)
        elif can_reach_anyone:
            graph._pending.append(i)
            continue
        else:
            return ('inactive', i)

    return (None, None)

 
def smart_decimate(graph, event):

    get_adj_list(graph)
 
    kind = event[0]
 
    if kind == 'fuse':
        _, i, j, delta_ij = event
        u, v = graph.nodes[i], graph.nodes[j]
        if v.range > u.range:
            u, v = v, u
 
        new_range = max(0, u.range + v.range - delta_ij)
 
        neighbor_ks = set(graph.adj_list.get(u.id, {}).keys())
        neighbor_ks.update(graph.adj_list.get(v.id, {}).keys())
        neighbor_ks.discard(u.id)
        neighbor_ks.discard(v.id)
 
        for k in neighbor_ks:
            d_uk = graph.adj[u.id][k]
            d_vk = graph.adj[v.id][k]
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
 
            if best > 0:
                adjlist_set_edge(graph, u.id, k, best)
            else:
                adjlist_remove_edge(graph, u.id, k)
 
        graph.merge_clusters(u.id, v.cluster_id)
        u.range = new_range
 
        for vv in graph.nodes.values():
            if vv.cluster_id == u.cluster_id and vv.active:
                vv.range = new_range
 
        graph.set_node_status(v.id, False)
        for (k, _w) in list(graph.adj_list.get(v.id, {}).items()):
            graph.remove_edge(v.id, k)
 
        adjlist_remove_node(graph, v.id)
 
        return [u.id, v.id]
 
    elif kind == 'inactive':
 
        _, i = event
        graph.set_node_status(i, False)
        for (k, _w) in list(graph.adj_list.get(i, {}).items()):
            graph.remove_edge(i, k)
 
        adjlist_remove_node(graph, i)
 
        return [i]
 
    return []

def adjlist_to_csr_arrays(adj_list, n):
    rows, cols, weights = [], [], []
    for i, neighbors in adj_list.items():
        for j, w in neighbors.items():
            rows.append(i)
            cols.append(j)
            weights.append(w)
    return (
        np.array(rows, dtype=np.int32),
        np.array(cols, dtype=np.int32),
        np.array(weights, dtype=np.float64),
    )
