#!/usr/bin/env python
#
# Graph visualization using force-directed drawing
#

import random
import logging

import numpy as np

# prevent pygame from printing annoying message
import contextlib
with contextlib.redirect_stdout(None):
    import pygame as pg
    from pygame import gfxdraw

# number of nodes
N = 20

class ForceGraph:
    """
    Visualization of a graph by simulation of interacting forces between nodes
    """

    REPEL_CONST = 150
    ATTRACT_CONST = 15
    GRAVITY_CONST = 2

    def __init__(self, N, edges, directed):
        self.N = N
        self.edges = edges

        self.directed = directed

        self.positions = [[random.uniform(-2, 2), random.uniform(-2, 2)] for _ in range(self.N)]
        self.velocities = [[0.0, 0.0] for _ in range(self.N)]

        self.gravity_enabled = False

    def compute_graph(self):
        """
        Computes the final graph by running the simulation until we reach an equilibrium, ie.
        when the sum of forces in the system is close to zero
        """
        n = 0

        while True:
            self.update(0.005)

            v = self.total_velocity

            if v < 0.1:
                break
            n+=1

    def update(self, dt):
        # velocity decay
        for i in range(self.N):
            self.velocities[i][0] *= 0.99 * dt
            self.velocities[i][1] *= 0.99 * dt

        self.add_forces()

        # update node positions by its velocity
        for i in range(self.N):
            self.positions[i][0] += self.velocities[i][0] * dt
            self.positions[i][1] += self.velocities[i][1] * dt


    def add_forces(self):
        self.add_repel_forces()
        self.add_attraction_forces()

        if self.gravity_enabled:
            self.add_gravitational_forces()

    def add_gravitational_forces(self):
        for i in range(self.N):
            x1, y1 = self.positions[i]
            x2, y2 = [0, 0]

            r, angle = self.polar(x1, y1, x2, y2)

            F = self.GRAVITY_CONST * r

            fx = F * np.cos(angle)
            fy = F * np.sin(angle)

            self.velocities[i][0] += fx
            self.velocities[i][1] += fy

    def add_repel_forces(self):
        for i in range(self.N):
            for j in range(i+1, self.N):
                x1, y1 = self.positions[i]
                x2, y2 = self.positions[j]

                r, angle = self.polar(x1, y1, x2, y2)

                F = - self.REPEL_CONST / r**2

                fx = F * np.cos(angle)
                fy = F * np.sin(angle)

                self.velocities[i][0] += fx
                self.velocities[i][1] += fy

                self.velocities[j][0] += -fx
                self.velocities[j][1] += -fy

    def add_attraction_forces(self):
        for (p1, p2) in self.edges:
                x1, y1 = self.positions[p1]
                x2, y2 = self.positions[p2]

                r, angle = self.polar(x1, y1, x2, y2)

                F = self.ATTRACT_CONST * r

                fx = F * np.cos(angle)
                fy = F * np.sin(angle)

                self.velocities[p1][0] += fx
                self.velocities[p1][1] += fy

                self.velocities[p2][0] += -fx
                self.velocities[p2][1] += -fy

    @staticmethod
    def polar(x1, y1, x2, y2):
        """
        Get the polar coordinates to (x2, y2), relative to (x1, y1)

        Returns coordinates as a tuple of (distance, radians)
        """
        a = x2 - x1 # dx
        b = y2 - y1 # dy

        distance = np.sqrt(a**2 + b**2)
        angle = np.arctan2(b,a)

        return (distance, angle)


    @property
    def total_velocity(self):
        v = 0

        for x,y in self.velocities:
            v += np.sqrt(x**2 + y**2)

        return v


class GraphWindow:
    """
    Handles the actual displaying of the graph
    """

    WINDOW_SIZE = WINDOW_W, WINDOW_H = 800, 600

    def __init__(self, N, edges, directed, precompute_graph=False):
        self.graph = ForceGraph(N, edges, directed)

        self.draw_scale = 25
        self.node_colors = [[255-i*8, i*8, 200] for i in range(N)]
        self.node_radius = 16

        if precompute_graph:
            self.graph.compute_graph()

        pg.init()
        self.screen = pg.display.set_mode(self.WINDOW_SIZE)


        self.running = False
        self.paused = False

    def loop(self):
        now = pg.time.get_ticks()
        last = now

        self.running = True
        while self.running:
            now = pg.time.get_ticks()
            delta  = (now - last) / 1000.0 # seconds since last loop
            last = now

            if not self.paused:
                self.graph.update(delta)

            self.handle_events()
            self.render()

        pg.quit()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type ==  pg.KEYDOWN and (event.key == pg.K_ESCAPE or event.key == pg.K_q):
                self.running = False
            elif event.type ==  pg.KEYDOWN and event.key == pg.K_k:
                self.draw_scale *= 1.05
            elif event.type ==  pg.KEYDOWN and event.key == pg.K_j:
                self.draw_scale *= 0.95
            elif event.type ==  pg.KEYDOWN and event.key == pg.K_g:
                self.graph.gravity_enabled = not self.graph.gravity_enabled
            elif event.type ==  pg.KEYDOWN and event.key == pg.K_r:
                self.graph = ForceGraph(self.graph.N, self.graph.edges, self.graph.directed)
            elif event.type ==  pg.KEYDOWN and event.key == pg.K_p:
                self.paused = not self.paused

    def render(self):
        self.screen.fill([255, 255, 255])

        self.draw_graph_edges()
        self.draw_graph_nodes()

        pg.display.update()

    def draw_graph_edges(self):
        """
        Draw all the edges of the graph
        """
        for (p1, p2) in self.graph.edges:
            x1, y1 = self.graph.positions[p1]
            x2, y2 = self.graph.positions[p2]

            x1, y1 = self.to_screen_position((x1, y1))
            x2, y2 = self.to_screen_position((x2, y2))

            self.draw_edge(x1, y1, x2, y2)

            if self.graph.directed:
                self.draw_edge_direction(x1, y1, x2, y2)

    def draw_edge_direction(self, x1, y1, x2, y2):
        """
        Draw a triangle representing the head of an arrow,
        indicating the direction of the edge
        """
        dist, angle = self.graph.polar(x1,y1, x2, y2)

        w = 8 # bottom width
        l = 8  # length from point to shaft

        # root of the arrowhead, ie. where it meets the shaft
        prx = x1 + (dist - self.node_radius - l) * np.cos(angle)
        pry = y1 + (dist - self.node_radius - l) * np.sin(angle)

        # point of the arrow
        p1x = int(x1 + (dist - self.node_radius) * np.cos(angle))
        p1y = int(y1 + (dist - self.node_radius) * np.sin(angle))

        # sides of the arrow
        p2x = int(prx + w/2 * np.cos(angle + np.pi/2))
        p2y = int(pry + w/2 * np.sin(angle + np.pi/2))
        p3x = int(prx + w/2 * np.cos(angle - np.pi/2))
        p3y = int(pry + w/2 * np.sin(angle - np.pi/2))

        self.draw_triangle(p1x, p1y, p2x, p2y, p3x, p3y)


    def draw_graph_nodes(self):
        """
        Draw all the nodes of the graph
        """
        for i in range(self.graph.N):
            p = self.graph.positions[i]
            c = self.node_colors[i]

            x, y = self.to_screen_position(p)

            self.draw_node(x, y, c)

    def draw_edge(self, x1, y1, x2, y2):
        """
        Draw a single edge from (x1, y1) to (x2, y2)
        """
        gfxdraw.line(self.screen, x1, y1, x2, y2, [0,0,0])

    def draw_node(self, x, y, color=[100,100,100]):
        """
        Draw a single node at (x,y)
        """
        self.draw_circle(x,y, self.node_radius)
        self.draw_circle(x,y, self.node_radius-2, color=color)

    def draw_circle(self, x, y, r, color=[0,0,0]):
        """
        Draw a bordered circle with radius r, centered at (x,y)
        """

        gfxdraw.aacircle(self.screen, x, y, r, color)
        gfxdraw.filled_circle(self.screen, x, y, r, color)

    def draw_triangle(self, x1, y1, x2, y2, x3, y3):
        """
        Draw a filled triangle with corners at (x1, y1), (x2, y2), (x3, y3)
        """
        gfxdraw.filled_trigon(self.screen, x1, y1,x2, y2,x3, y3, [0,0,0])

    def to_screen_position(self, pos):
        """
        Converts a position in the coordinate space to its position on the screen
        """
        x,y = pos

        x = int(x * self.draw_scale + self.WINDOW_W //2)
        y = int(-y * self.draw_scale + self.WINDOW_H //2)

        return (x,y)


if __name__ == "__main__":
    # cycle graph
    edges = [(n, n+1) for n in range(N-1)]
    edges.append((N-1, 0))

    # random edges
    for _ in range(N//3):
        a = random.randint(0, N-1)
        b = random.randint(0, N-1)

        while b == a:
            b = random.randint(0, N-1)

        edges.append((a,b))

    GraphWindow(N, edges, True, False).loop()
