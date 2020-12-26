from random import randint

import pygame
from phoenyx import Engine

from boid import Boid
from quadtree import Circle, Point, Quadtree, Rect


def _map(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    """
    linear interpolation
    """
    return (y0 * (x1 - x) + y1 * (x - x0)) / (x1 - x0)


class Population:
    """
    Population
    ==========
    Group of Boids

    Population has :
     * a ``Group`` of Boids
     * a ``quadtree`` recursive structure
    """
    def __init__(self, renderer: Engine, win: tuple, n: int = 10) -> None:
        self._renderer = renderer
        self._win = win
        self.pop = pygame.sprite.Group()

        self.qt = Quadtree(
            Rect(renderer, self._win[0] // 2, self._win[1] // 2, self._win[0] // 2, self._win[1] // 2))

        for _ in range(n):
            self.pop.add(Boid(renderer, randint(0, win[0]), randint(0, win[1]), win))

    def show(self) -> None:
        """
        calls draw methods from Engine to draw Sprite Group
        """
        self._renderer.sprites(self.pop)

    def build(self) -> None:
        """
        Rebuilds the Quadtree
        """
        self.qt = Quadtree(
            Rect(self._renderer, self._win[0] // 2, self._win[1] // 2, self._win[0] // 2, self._win[1] // 2))

        for boid in self.pop:
            point = Point(boid.rect.x, boid.rect.y, boid)
            self.qt.insert(point)

    def update(self, a: float = 1, b: float = 1, c: float = 1) -> tuple:
        """
        Updates all population

        Parameters
        ----------
            a : (float, optional)
                coefficient for alignment
                Defaults to 1
            b : (float, optional)
                coefficient for cohesion
                Defaults to 1
            c : (float, optional)
                coefficient for separation
                Defaults to 1
        Returns
        -------
            tuple : total neighbors, velocity, brute and modified force
        """
        total, vel = 0, 0
        brute, modified = 0, 0

        for boid in self.pop.sprites()[:]:
            points =\
                self.qt.query(Circle(self._renderer, boid.rect.x, boid.rect.y, boid.RADIUS)) +\
                self.qt.query(Circle(self._renderer, boid.rect.x + self._win[0], boid.rect.y, boid.RADIUS)) +\
                self.qt.query(Circle(self._renderer, boid.rect.x - self._win[0], boid.rect.y, boid.RADIUS)) +\
                self.qt.query(Circle(self._renderer, boid.rect.x, boid.rect.y + self._win[1], boid.RADIUS)) +\
                self.qt.query(Circle(self._renderer, boid.rect.x, boid.rect.y - self._win[1], boid.RADIUS))
            others = [p.data for p in points]

            tot, br, mo = boid.flock(others, a, b, c)
            total += tot
            brute += br
            modified += mo

        for boid in self.pop:
            vel += boid.move()

        self.build()
        return total, vel, brute, modified
