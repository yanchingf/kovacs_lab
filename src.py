import math

# build sdrg
class Node:
    def __init__(self, x=0, y=0):
        self.radius = 10
        self.edges = ()
        self.x = x
        self.y = y
        self.cluster_id = 0

class Tree:
    def __init__(self):
        self.vertices = ()
        self.clusters = ()

    # assume info is stored in form (pos_1, pos_2, r_1, r_2)
    def run_SDRG(self):
        distance = math.sqrt()
        return
