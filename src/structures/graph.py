
import heapq
import math

import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u

from sklearn.neighbors import BallTree
import numpy as np

from collections import defaultdict

class Node:

    def __init__(self, range=0, active=True, id=-1, cluster_id=-2, coords=None):
        
        self.range = range
        self.id = id
        self.cluster_id = cluster_id
        self.active = active

        if coords is not None:
            self.pos = coords
        else:
            print("Coords needed in declaration")

    def __repr__(self):

        return f"Range: {self.range} | ID: {self.id} | Cluster ID: {self.cluster_id} | Active: {self.active}"

        
class Graph:

    def __init__(self, n, coords=None, tree=None, use_sky_coords=True):

        if coords is None:
            coords = [None] * n

        self.nodes = {i: Node(id=i, cluster_id=i, coords=coords[i]) for i in range(n)}
        self.adj = [[0]*n for i in range(n)] # full adj matrix
        self.group_ids = defaultdict(list)
        for i in range(n):
            self.group_ids[i] = [i]
        self.length = n
        self.tree = tree if not None else None
        self.use_sky_coords = use_sky_coords
        self.adj_list = None

    def add_edge(self, u, v, weight):

        self.adj[u][v] = weight
        self.adj[v][u] = weight

    def remove_edge(self, u, v):

        self.adj[u][v] = 0
        self.adj[v][u] = 0

    def get_edge(self, u, v):

        return self.adj[u][v]
    
    def set_node_status(self, id, status):

        self.nodes[id].active = status

    def get_cluster_members(self, cluster_id):

        return [i.id for i in self.nodes.values() if i.cluster_id==cluster_id]
    
    def merge_clusters(self, head, other):

        to_change = self.get_cluster_members(other)
        head_cluster = self.nodes[head].cluster_id

        for i in to_change:
            self.nodes[i].cluster_id = head_cluster

        self.group_ids[head_cluster].extend(self.group_ids.get(other, []))
        self.group_ids.pop(other, None)

    def djikstra(self, id,  max_dist=float("inf")):

        distances = [float("inf")] * self.length
        distances[id] = 0
        pq = [(0, id)]

        while len(pq) > 0:
            curr_dist, u = heapq.heappop(pq)

            if curr_dist > distances[u]:
                continue

            if curr_dist > max_dist:
                break;

            for v, weight in enumerate(self.adj[u]):
                if weight <= 0:
                    continue

                new_dist = curr_dist + weight

                if new_dist < distances[v]:
                    distances[v] = new_dist
                    heapq.heappush(pq, (new_dist, v))

        return distances


def angular_sep(ra1_deg, dec1_deg, ra2_deg, dec2_deg):

    c1 = SkyCoord(ra=ra1_deg * u.deg, dec=dec1_deg * u.deg)
    c2 = SkyCoord(ra=ra2_deg * u.deg, dec=dec2_deg * u.deg)
    return c1.separation(c2).value

def angular_sep_matrix(ra_deg, dec_deg):

    coords = SkyCoord(ra=np.asarray(ra_deg) * u.deg, dec=np.asarray(dec_deg) * u.deg)
    n = len(coords)
    sep = np.zeros((n, n))
    for i in range(n):
        sep[i, :] = coords[i].separation(coords).value
    return sep

def build_graph(points, ranges, neighbors=None, use_sky_coords=True):
 
    a, b = points  # (ra, dec) in deg if use_sky_coords, else plain (x, y)
    coords = np.column_stack((a, b))
    ranges = np.asarray(ranges, dtype=float)
    n = coords.shape[0]
    g = Graph(n, coords=coords)
 
    for i in range(n):
        g.nodes[i].pos = coords[i]
        g.nodes[i].use_sky_coords = use_sky_coords
        if use_sky_coords:
            g.nodes[i].ra = coords[i, 0]
            g.nodes[i].dec = coords[i, 1]
        g.nodes[i].range = ranges[i]
 
    if use_sky_coords:
        rad = np.radians(coords)
        tree_coords = rad[:, ::-1]
        tree = BallTree(tree_coords, metric='haversine')
    else:
        tree_coords = coords
        tree = BallTree(tree_coords, metric='euclidean')
 
    g.tree = tree
    g.tree_coords = tree_coords
    g.use_sky_coords = use_sky_coords
 
    def _dist(i, j):
        if use_sky_coords:
            return angular_sep(a[i], b[i], a[j], b[j])
        return np.linalg.norm(coords[i] - coords[j])
 
    if neighbors is not None:
        k = min(neighbors, n - 1)
        added = set()
 
        jj, idx = tree.query(tree_coords, k=k + 1)
 
        for i in range(n):
            for j in idx[i]:
                if j == i:
                    continue
                edge = (min(i, j), max(i, j))
                if edge not in added:
                    added.add(edge)
                    g.add_edge(edge[0], edge[1], _dist(i, j))
 
    else:

        for i in range(n):
            r = np.radians(ranges[i]) if use_sky_coords else ranges[i]
            cand = tree.query_radius(tree_coords[i:i + 1], r=r)[0]
            for j in cand:
                if j <= i:
                    continue
                g.add_edge(i, j, _dist(i, j))
 
    return g
 