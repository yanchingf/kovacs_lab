
import heapq


def get_adj_list(graph):

    if not hasattr(graph, "adj_list") or graph.adj_list is None:
        adj_list = {i: [] for i in graph.nodes}
        n = graph.length
        for i in range(n):
            for j in range(n):
                if i != j and graph.adj[i][j] > 0:
                    adj_list[i].append((j, graph.adj[i][j]))
        graph.adj_list = adj_list
    return graph.adj_list

 
def adjlist_remove_edge(graph, i, j):
   
    adj_list = graph.adj_list
    adj_list[i] = [(k, w) for (k, w) in adj_list.get(i, []) if k != j]
    adj_list[j] = [(k, w) for (k, w) in adj_list.get(j, []) if k != i]
 
 
def adjlist_set_edge(graph, i, j, w):

    adjlist_remove_edge(graph, i, j)
    if w > 0:
        graph.adj_list[i].append((j, w))
        graph.adj_list[j].append((i, w))
 
 
def adjlist_remove_node(graph, i):

    adj_list = graph.adj_list
    neighbors = adj_list.pop(i, [])
    for (j, _) in neighbors:
        adj_list[j] = [(k, w) for (k, w) in adj_list.get(j, []) if k != i]


def build_adjacency_list(graph):

    adj_list = {i: [] for i in graph.nodes}
    n = graph.length
    for i in range(n):
        for j in range(n):
            if i != j and graph.adj[i][j] > 0:
                adj_list[i].append((j, graph.adj[i][j]))
    return adj_list


def smart_search(graph):
 
    active = [i for i, node in graph.nodes.items() if node.active]
    if not active:
        return (None, None)
 
    active_set = set(active)
    adj_list = get_adj_list(graph)
 
    dist = {}
    heap = []  # (distance, node, source)
 
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
                j_range = graph.nodes[node].range
                source_range = graph.nodes[source].range
                if d <= source_range and d <= j_range:
                    return ('fuse', owner, source, d)
            continue
 
        source_range = graph.nodes[source].range
 
        if d > source_range:
            exhausted.add(source)
            continue
 
        visited_by[node] = source
        dist[node] = (d, source)
 
        for neighbor, w in adj_list.get(node, []):
            nd = d + w
            if nd <= source_range and neighbor not in visited_by:
                heapq.heappush(heap, (nd, neighbor, source))
 
    for s in active:
        if s in exhausted or not adj_list.get(s):
            return ('inactive', s)
 
    return ('inactive', active[0])
 
 
def smart_decimate(graph, event):

    get_adj_list(graph)
 
    kind = event[0]
 
    if kind == 'fuse':
        _, i, j, delta_ij = event
        u, v = graph.nodes[i], graph.nodes[j]
        if v.range > u.range:
            u, v = v, u
 
        new_range = max(0, u.range + v.range - delta_ij)
 
        neighbor_ks = set(k for k, _w in graph.adj_list.get(u.id, []))
        neighbor_ks.update(k for k, _w in graph.adj_list.get(v.id, []))
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
        for (k, _w) in list(graph.adj_list.get(v.id, [])):
            graph.remove_edge(v.id, k)
 
        adjlist_remove_node(graph, v.id)
 
        return [u.id, v.id]
 
    elif kind == 'inactive':
 
        _, i = event
        graph.set_node_status(i, False)
        for (k, _w) in list(graph.adj_list.get(i, [])):
            graph.remove_edge(i, k)
 
        adjlist_remove_node(graph, i)
 
        return [i]
 
    return []