#!/usr/bin/env python
#
# Simple example of visualizing a cycle graph
#

import random
from force_graph import GraphWindow

N = 20 # number of nodes

# create edges of a cycle graph
edges = [(n, n+1) for n in range(N-1)]
edges.append((N-1, 0))

w = GraphWindow(N, edges)
w.loop()
