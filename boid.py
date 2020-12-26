from math import degrees

import pygame

from phoenyx import Engine, Vector


class Boid(pygame.sprite.Sprite):
    """
    Boid
    ====
    inherits from pygame.sprite.Sprite\\
    uses ``Engine``
    """
    RADIUS = 50
    ANGLE = 35
    MAXFORCE = .1
    SPEED = 4

    def __init__(self, renderer: Engine, x: int, y: int, win: tuple) -> None:
        """
        new Boid instante

        Parameters
        ----------
            renderer : Engine
                main Engine
            x : int
                x coordinate of the Boid
            y : int
                y coordinate of the Boid
            win : tuple
                main screen dimensions
        """
        super().__init__()
        self._renderer = renderer

        self.image = pygame.image.load("images/triangle.png")
        self.image = pygame.transform.scale(self.image, (14, 15))
        self.image = pygame.transform.rotate(self.image, -90)
        self._origin_image = self.image

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self._win = win

        self.pos = Vector(x, y)
        self.vel = Vector.random2d(mag=self.SPEED)
        self.acc = Vector()

        self._width = self.image.get_width()
        self._height = self.image.get_height()

    def move(self) -> float:
        """
        moves the Boid and returns its velocity magnitude
        """
        self.pos += self.vel
        self.vel += self.acc
        self.vel.limit(upper=self.SPEED)
        self.acc *= 0

        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        if self.rect.x <= 0:
            self.rect.x = self._win[0] - self._width - 1
        elif self.rect.x > self._win[0] - self._width:
            self.rect.x = 1

        if self.rect.y <= 0:
            self.rect.y = self._win[1] - self._height - 1
        if self.rect.y > self._win[1] - self._height:
            self.rect.y = 1

        self.pos.setCoord(self.rect.x, self.rect.y)
        angle = -degrees(self.vel.angle)
        self.image = pygame.transform.rotate(self._origin_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        return self.vel.magnitude

    def flock(self, others: pygame.sprite.Group, a: float = 1, b: float = 1, c: float = 1) -> tuple:
        """
        make changes to the Boid acceleration\\
        return

        Parameters
        ----------
            others : pygame.sprite.Group
                other Boids
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
            tuple : number of neighbors, brute forces and modified forces
        """
        alignment, cohesion, separation, total = self.get_forces(others)
        brute = alignment.magnitude + cohesion.magnitude + separation.magnitude

        alignment *= a
        cohesion *= b
        separation *= c

        self.acc += alignment + cohesion + separation
        modified = alignment.magnitude + cohesion.magnitude + separation.magnitude

        return total, brute, modified

    def get_forces(self, others: pygame.sprite.Group) -> tuple:
        """
        computes alignment, cohesion and separation steering forces

        Parameters
        ----------
            others : pygame.sprite.Group
                other Boids
        Returns
        -------
            tuple : steerings forces and number of neighbors
        """
        steering_alignment = Vector()
        steering_cohesion = Vector()
        steering_separation = Vector()
        total = 0

        for other in others:
            d = self.pos.distance(other.pos)

            if other is not self and self.is_visible(other):
                steering_alignment += other.vel
                steering_cohesion += other.pos

                diff = (self.pos - other.pos) / (1 + d * d)
                steering_separation += diff

                total += 1

        if total >= 1:
            steering_alignment /= total
            steering_alignment.magnitude = self.SPEED
            steering_alignment -= self.vel
            steering_alignment.limit(upper=self.MAXFORCE)

            steering_cohesion /= total
            steering_cohesion -= self.pos
            steering_cohesion.magnitude = self.SPEED
            steering_cohesion -= self.vel
            steering_cohesion.limit(upper=self.MAXFORCE)

            steering_separation /= total
            steering_separation.magnitude = self.SPEED
            steering_separation -= self.vel
            steering_separation.limit(upper=self.MAXFORCE)

        return steering_alignment, steering_cohesion, steering_separation, total

    def is_visible(self, other) -> bool:
        """
        implements the vision of the boid (does no longer check the distance since v1.2)\\
        ``True`` if other is visible by ``self``
        """
        v1 = -self.vel
        v2 = other.pos - self.pos
        return degrees(abs(v1.angle_between(v2))) > self.ANGLE
