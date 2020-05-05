from collections import defaultdict
from timeit import timeit
import os
import numpy as np
from Queue import deque
from pprint import pprint

class Graph(object):

    def __init__(self, graph_dict=None):
        """ initializes a graph object 
            If no dictionary or None is given, 
            an empty dictionary will be used
        """
        if graph_dict == None:
            graph_dict = {}
        self.__graph_dict = graph_dict

    def vertices(self):
        """ returns the vertices of a graph """
        return list(self.__graph_dict.keys())

    def edges(self):
        """ returns the edges of a graph """
        return self.__generate_edges()

    def add_vertex(self, vertex):
        """ If the vertex "vertex" is not in 
            self.__graph_dict, a key "vertex" with an empty
            list as a value is added to the dictionary. 
            Otherwise nothing has to be done. 
        """
        if vertex not in self.__graph_dict:
            self.__graph_dict[vertex] = []

    def add_edge(self, edge):
        """ assumes that edge is of type set, tuple or list; 
            between two vertices can be multiple edges! 
        """
        edge = set(edge)
        (vertex1, vertex2) = tuple(edge)
        if vertex1 in self.__graph_dict:
            self.__graph_dict[vertex1].append(vertex2)
        else:
            self.__graph_dict[vertex1] = [vertex2]

    def __generate_edges(self):
        """ A static method generating the edges of the 
            graph "graph". Edges are represented as sets 
            with one (a loop back to the vertex) or two 
            vertices 
        """
        edges = []
        for vertex in self.__graph_dict:
            for neighbour in self.__graph_dict[vertex]:
                if {neighbour, vertex} not in edges:
                    edges.append({vertex, neighbour})
        return edges

    def __str__(self):
        res = "vertices: "
        for k in self.__graph_dict:
            res += str(k) + " "
        res += "\nedges: "
        for edge in self.__generate_edges():
            res += str(edge) + " "
        return res

    def dijkstra(self, start, goal):
        self.cost = {}
        self.parent = {}
        for v in range(self.vertex):
            self.cost[v] = float("inf")
            self.parent[v] = None

        self.cost[start] = 0

        vertices = set(self.cost)

        while vertices:
            curr = min(vertices, key=lambda v: self.cost[v])
            vertices.remove(curr)
            if self.cost[curr] == float("inf"):
                break
            for neighbor in self.graph[curr]:
                diff = self.cost[curr] + self.weight.get((curr, neighbor))
                if diff < self.cost[neighbor]:
                    self.cost[neighbor] = diff
                    self.parent[neighbor] = curr

        path, curr = deque(), goal
        count = 0
        while self.parent[curr] is not None:
            if count == 100:
                path.clear()
                return path
                break
            path.appendleft(curr)
            curr = self.parent[curr]
            count += 1
        if path:
            path.appendleft(curr)
        return path

def dijkstra(g):
    distance_matrix = np.zeros((8, 8))
    for i in range(g.vertex):
        for j in range(g.vertex):
            temp = g.dijkstra(i, j)
            distance_matrix[i, j] = (len(temp))

    print(distance_matrix)
    return distance_matrix

"""
if __name__ == "__main__":

    g = { "a" : ["d"],
          "b" : ["c"],
          "c" : ["b", "c", "d", "e"],
          "d" : ["a", "c"],
          "e" : ["c"],
          "f" : []
        }


    graph = Graph(g)

    print("Vertices of graph:")
    print(graph.vertices())

    print("Edges of graph:")
    print(graph.edges())

    print("Add vertex:")
    graph.add_vertex("z")

    print("Vertices of graph:")
    print(graph.vertices())
 
    print("Add an edge:")
    graph.add_edge({"a","z"})
    
    print("Vertices of graph:")
    print(graph.vertices())

    print("Edges of graph:")
    print(graph.edges())

    print('Adding an edge {"x","y"} with new vertices:')
    graph.add_edge({"x","y"})
    print("Vertices of graph:")
    print(graph.vertices())
    print("Edges of graph:")
    print(graph.edges())
"""