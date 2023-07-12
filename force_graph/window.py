# window.py

import math

from force_graph.graph import ForceGraph

# prevent pygame from printing annoying message
import contextlib
with contextlib.redirect_stdout(None):
    import pygame as pg
    from pygame import gfxdraw


class GraphWindow:
    """
    GraphWindow represents the window that handles the actual displaying of the graph,
    keyboard inputs, as well as the simulation loop
    """

    DEFAULT_WINDOW_SIZE = DEFAULT_WINDOW_W, DEFAULT_WINDOW_H = 800, 600

    def __init__(self, N, edges, window_size=None, directed=False, precompute_graph=False):
        self.graph = ForceGraph(N, edges, directed)

        self.draw_scale = 25
        self.node_colors = [[255-i*8, i*8, 200] for i in range(N)]
        self.node_radius = 16

        if precompute_graph:
            self.graph.compute_graph()

        if window_size:
            self.window_size = window_size
        else:
            self.window_size = self.DEFAULT_WINDOW_SIZE

        pg.init()
        self.screen = None

        self.running = False
        self.paused = False

    def loop(self):
        self.screen = pg.display.set_mode(self.window_size)

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

        w = 8  # bottom width
        l = 8  # length from point to shaft

        # root of the arrowhead, ie. where it meets the shaft
        prx = x1 + (dist - self.node_radius - l) * math.cos(angle)
        pry = y1 + (dist - self.node_radius - l) * math.sin(angle)

        # point of the arrow
        p1x = int(x1 + (dist - self.node_radius) * math.cos(angle))
        p1y = int(y1 + (dist - self.node_radius) * math.sin(angle))

        # sides of the arrow
        p2x = int(prx + w/2 * math.cos(angle + math.pi/2))
        p2y = int(pry + w/2 * math.sin(angle + math.pi/2))
        p3x = int(prx + w/2 * math.cos(angle - math.pi/2))
        p3y = int(pry + w/2 * math.sin(angle - math.pi/2))

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

        x = int(x * self.draw_scale + self.window_size[0] //2)
        y = int(-y * self.draw_scale + self.window_size[1] //2)

        return (x,y)
