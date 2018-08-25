from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
import numpy as np


def check_symmetric(a, tol=1e-8):
    return np.allclose(a, a.T, atol=tol)


def symmetrize(a):
    return a + a.T - np.diag(a.diagonal())


class CostmapToSparseGraph:
    """Class that convert image to sparse graph representation """

    def __init__(self, costmap):
        self.costmap = costmap

    def graph_id(self, i, j):
        return i + j * self.costmap.shape[0]

    def is_in_costmap(self, i, j):
        """ Returns true if the node coord is in the costmap """
        return (
            i >= 0 and i < self.costmap.shape[0] and
            j >= 0 and j < self.costmap.shape[1])

    @staticmethod
    def neiborghs(i, j):
        """ returns the costmap coordinates of all neighbor nodes """
        coord = [None] * 8
        coord[0] = (i, j + 1)
        coord[1] = (i, j - 1)
        coord[2] = (i + 1, j)
        coord[3] = (i + 1, j - 1)
        coord[4] = (i + 1, j + 1)
        coord[5] = (i - 1, j)
        coord[6] = (i - 1, j - 1)
        coord[7] = (i - 1, j + 1)
        return coord

    @staticmethod
    def edge_cost(c_i, c_j, n_i, n_j):
        return 1

    def convert(self):
        """ Converts a costmap to a compressed sparse graph

            cost : The M x N matrix of costs. cost[i,j] 
                   gives the cost of a certain node
            node_map_coord  = (i, j)
            node_graph_id   = i + j * M
        """
        nb_nodes = self.costmap.shape[0] * self.costmap.shape[1]
        graph_dense = np.zeros((nb_nodes, nb_nodes))
        for (c_i, c_j), c_ij in np.ndenumerate(self.costmap):
            c_node = self.graph_id(c_i, c_j)
            for (n_i, n_j) in self.neiborghs(c_i, c_j):
                if self.is_in_costmap(n_i, n_j):
                    # get the neighbor graph id
                    # compute edge cost and store it in graph
                    n_node = self.graph_id(n_i, n_j)
                    graph_dense[c_node, n_node] = self.edge_cost(
                        c_i, c_j, n_i, n_j)
        return graph_dense