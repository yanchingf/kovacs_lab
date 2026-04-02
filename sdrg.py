
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
        self.clusters = {} # clusters[id]= {(pos, r)}
        
    '''
    1. To create clusters; if two stars are each within the range of the other (formally, such that δ_ij≤min{r_i,r_j},where δ_ij represents the distance between stars i and j), the stars are assigned to the same cluster. 
    2. Calculate the merged cluster’s effective range as r ̃=r_i+r_j-δ_ij (the sum of the individual ranges minus the cost, or distance, to connect them) and assign this new range to each individual star in the cluster. 
    3. If any cluster in the system does not have other stars within its effective range (i.e., if r_ij<δ_ij for all stars i in the cluster and j outside of it), then it considers that cluster as completed, yielding a constellation.
    4. Repeat steps 13 until there are no more “moves” to be made— that is, no two stars belonging to different clusters are within each other’s range. At that point, the algorithm will be terminated (see Figure 1 for an example of the resulting star clusters). 

    '''
    def run_SDRG(self, star1, star2):
        d = math.sqrt((star1.x - star2.x)**2 + (star1.y - star2.y)**2)
        theta = math.atan((star1.y - star2.y)/(star1.x - star2.x))

        while ():
            if d <= min(star1.radius, star2.radius): # merge

                new_d = star1.radius + star2.radius - d # need to reconfigure this to sum of all node radii in cluster

                for i in self.vertices: 
                    if self.vertices[i].cluster_id == star1.cluster_id: # reassign cluster ids from 2
                        self.vertices[i].cluster_id = star2.cluster_id
                        self.vertices[i].radius = new_d

                    self.clusters[star1.cluster_id] 

        



        return
