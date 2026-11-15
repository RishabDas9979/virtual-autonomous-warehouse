"""Waypoint graph: shortest paths between named warehouse locations."""
import heapq
import math

import yaml


class Graph:
    def __init__(self, nodes, edges, orderable=None):
        self.nodes = {k: (float(v[0]), float(v[1])) for k, v in nodes.items()}
        self.orderable = list(orderable or [])
        self.adj = {k: [] for k in self.nodes}
        for a, b in edges:
            d = self.dist(a, b)
            self.adj[a].append((b, d))
            self.adj[b].append((a, d))

    @classmethod
    def from_yaml(cls, path):
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(data['nodes'], data['edges'], data.get('orderable'))

    def dist(self, a, b):
        (x1, y1), (x2, y2) = self.nodes[a], self.nodes[b]
        return math.hypot(x2 - x1, y2 - y1)

    def nearest(self, x, y):
        return min(self.nodes, key=lambda k: math.hypot(
            self.nodes[k][0] - x, self.nodes[k][1] - y))

    def chargers(self):
        return [k for k in self.nodes if k.startswith('charger_')]

    def path(self, start, goal):
        """Dijkstra. Returns (list of node names, length) or (None, inf)."""
        best = {start: 0.0}
        prev = {}
        heap = [(0.0, start)]
        while heap:
            d, k = heapq.heappop(heap)
            if k == goal:
                p = [k]
                while k in prev:
                    k = prev[k]
                    p.append(k)
                return p[::-1], d
            if d > best.get(k, math.inf):
                continue
            for n, w in self.adj[k]:
                nd = d + w
                if nd < best.get(n, math.inf):
                    best[n] = nd
                    prev[n] = k
                    heapq.heappush(heap, (nd, n))
        return None, math.inf

    def length(self, start, goal):
        return self.path(start, goal)[1]

    def nearest_charger(self, node):
        return min(self.chargers(), key=lambda c: self.length(node, c))
