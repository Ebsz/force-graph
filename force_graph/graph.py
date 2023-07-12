# graph.py

import math
import random


class ForceGraph:
    """
    Creates a visualization of a graph by simulating interacting forces between nodes
    """

    DEFAULT_REPEL_CONST = 150
    DEFAULT_ATTRACT_CONST = 15
    DEFAULT_GRAVITY_CONST = 2

    def __init__(self, N, edges, directed=False, constants=None):
        self.N = N
        self.edges = edges

        self.directed = directed

        self.positions = [[random.uniform(-2, 2), random.uniform(-2, 2)] for _ in range(self.N)]
        self.velocities = [[0.0, 0.0] for _ in range(self.N)]

        if constants:
            self.repel_const, self.attract_const, self.gravity_const = constants
        else:
            self.repel_const = self.DEFAULT_REPEL_CONST
            self.attract_const = self.DEFAULT_ATTRACT_CONST
            self.gravity_const = self.DEFAULT_GRAVITY_CONST

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

            F = self.gravity_const * r

            fx = F * math.cos(angle)
            fy = F * math.sin(angle)

            self.velocities[i][0] += fx
            self.velocities[i][1] += fy

    def add_repel_forces(self):
        for i in range(self.N):
            for j in range(i+1, self.N):
                x1, y1 = self.positions[i]
                x2, y2 = self.positions[j]

                r, angle = self.polar(x1, y1, x2, y2)

                F = - self.repel_const / r**2

                fx = F * math.cos(angle)
                fy = F * math.sin(angle)

                self.velocities[i][0] += fx
                self.velocities[i][1] += fy

                self.velocities[j][0] += -fx
                self.velocities[j][1] += -fy

    def add_attraction_forces(self):
        for (p1, p2) in self.edges:
                x1, y1 = self.positions[p1]
                x2, y2 = self.positions[p2]

                r, angle = self.polar(x1, y1, x2, y2)

                F = self.attract_const * r

                fx = F * math.cos(angle)
                fy = F * math.sin(angle)

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

        distance = math.sqrt(a**2 + b**2)
        angle = math.atan2(b,a)

        return (distance, angle)

    @property
    def total_velocity(self):
        v = 0

        for x,y in self.velocities:
            v += math.sqrt(x**2 + y**2)

        return v
