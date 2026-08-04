
import heapq

def build_adjacency_list(graph):

    adj_list = {i: [] for i in graph.nodes}
    n = graph.length
    for i in range(n):
        if not graph.nodes[i].active:
            continue
        for j in range(n):
            if i != j and graph.adj[i][j] > 0:
                adj_list[i].append((j, graph.adj[i][j]))
    return adj_list
 
 
def smart_search(graph):
 
    active = [i for i, node in graph.nodes.items() if node.active]
    if not active:
        return (None, None)
 
    adj_list = build_adjacency_list(graph)
 
    # dist[node] = distance so far
    dist = {}
    # heap entries: distance + node_id + source
    heap = []
 
    for s in active:
        budget = graph.nodes[s].range / 2.0
        dist[s] = (0.0, s)
        heapq.heappush(heap, (0.0, s, s))
 
    visited_by = {}

    while heap:
 
        d, node, source = heapq.heappop(heap)
 
        if node in visited_by:
            owner = visited_by[node]
            if owner != source:

                d_owner = dist[node][0] if node in dist and dist[node][1] == owner else None
                delta_ij = d + (dist[node][0] if dist.get(node, (None,))[1] == owner else 0)
                return ('fuse', owner, source, delta_ij)
            
            continue
 
        source_range = graph.nodes[source].range
        budget = source_range / 2.0
 
        if d > budget:
            continue
 
        visited_by[node] = source
        dist[node] = (d, source)
 
        for neighbor, w in adj_list.get(node, []):
            nd = d + w
            if nd <= budget and (neighbor not in visited_by):
                heapq.heappush(heap, (nd, neighbor, source))
 
    # heap drained with no fusion found -- every active site exhausted
    # its own r_i/2 budget without reaching another active site.
    # Per the paper, all such sites become inactive; return the first one
    for s in active:

        if not adj_list.get(s):
            return ('inactive', s)

    return ('inactive', active[0])
 
 
def smart_decimate(graph, event):

    kind = event[0]
 
    if kind == 'fuse':
        _, i, j, delta_ij = event
        u, v = graph.nodes[i], graph.nodes[j]
        if v.range > u.range:
            u, v = v, u
 
        new_range = max(0, u.range + v.range - delta_ij)
 
        for k in range(graph.length):
            if k not in (u.id, v.id):
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
 
        graph.merge_clusters(u.id, v.cluster_id)
        u.range = new_range
 
        for vv in graph.nodes.values():
            if vv.cluster_id == u.cluster_id and vv.active:
                vv.range = new_range
 
        graph.set_node_status(v.id, False)
        for k in range(graph.length):
            if graph.adj[v.id][k] > 0:
                graph.remove_edge(v.id, k)
 
        return [u.id, v.id]
 
    elif kind == 'inactive':

        _, i = event
        graph.set_node_status(i, False)
        for k in range(graph.length):
            if graph.adj[i][k] > 0:
                graph.remove_edge(i, k)
        return [i]
 
    return []