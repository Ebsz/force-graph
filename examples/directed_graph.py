#!/usr/bin/env python
#
# Example of visualizing a directed graph
#

import random
from force_graph import GraphWindow

N = 10 # number of nodes

edges = [(n, n+1) for n in range(N-1)]

# add random edges
for _ in range(N//3):
    a = random.randint(0, N-1)
    b = random.randint(0, N-1)

    while b == a:
        b = random.randint(0, N-1)

    edges.append((a,b))


w = GraphWindow(N, edges, directed=True)
w.loop()
