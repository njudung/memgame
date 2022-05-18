import pygame, sys
from pygame.locals import *
from random import random, choice, randint
from math import atan2, sqrt, cos, sin, pi as PI

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 30
TIME_PER_TICK = 1 / FPS
DISPLAY_SIZE = (1920, 1080)

K_air = 0.001  # Air resistance constant
G_r = 100 / FPS  # Gravity constant
G_phi = PI / 2

COLORS = [
    Color(255, 0, 0),
    Color(255, 255, 0),
    Color(0, 255, 0),
    Color(0, 255, 255),
    Color(0, 0, 255),
    Color(255, 0, 255),
    Color(255, 255, 255),
]

BACKGROUND = Color(30, 30, 30)


class Particle:
    def __init__(self, position=None, velocity=None, direction=None, color=None, fade=0.01):
        self.position = position if position else [DISPLAY_SIZE[0] * random(), DISPLAY_SIZE[1] * random()]
        self.velocity = velocity if velocity else 20 * random()
        self.direction = direction if direction else 2 * PI * random()
        self._color = color if color else choice(COLORS)
        self.fade = fade
        self.intensity = 0.0

    @property
    def color(self):
        if self.fade:
            return self._color.lerp(BACKGROUND, self.intensity)
        return self._color

    @color.setter
    def color(self, c):
        self._color = c

    def tick(self):
        # Update velocity
        self.velocity, self.direction = Particle.vector_add(self.velocity, self.direction, G_r, G_phi)

        # Update position
        self.position = (
            self.position[0] + self.velocity * cos(self.direction) * TIME_PER_TICK,
            self.position[1] + self.velocity * sin(self.direction) * TIME_PER_TICK,
        )

        # Update color?
        if self.fade:
            self.intensity += self.fade
            if self.intensity > 1:
                self.intensity = 1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, 3)

    def dead(self):
        if self.intensity >= 1.0:
            return True

        if self.position[0] < 100 or self.position[0] > DISPLAY_SIZE[0] + 100 or self.position[1] > DISPLAY_SIZE[1]:
            return True

        return False

    @staticmethod
    def vector_add(r1, phi1, r2, phi2):
        """Add two vectors in polar coordinates.
        https://math.stackexchange.com/a/1365938
        """
        r = sqrt(r1 * r1 + r2 * r2 + 2 * r1 * r2 * cos(phi2 - phi1))
        phi = phi1 + atan2(r2 * sin(phi2 - phi1), r1 + r2 * cos(phi2 - phi1))
        return r, phi


class Firework:
    STATE_LAUNCH = 1
    STATE_DETONATION = 2

    def __init__(self):
        self.state = Firework.STATE_LAUNCH
        self.particles = [
            Particle(
                position=(1920 / 2, 1079),
                velocity=400 * random() + 200,
                direction=-PI / 2 + (random() - 0.5),
                color=Color(70, 70, 70),
                fade=0,
            )
        ]
        self.tick_count = 0
        self.detonation_tick = randint(50, 100)
        self.base_color = choice(COLORS)

    def tick(self):
        self.tick_count += 1

        if self.state == Firework.STATE_LAUNCH:
            self.particles[0].tick()

            if self.tick_count == self.detonation_tick:
                self.state = Firework.STATE_DETONATION

                base_direction = self.particles[0].direction
                base_velocity = self.particles[0].velocity
                position = self.particles[0].position
                color = self.base_color

                self.particles = self.explode(base_direction, base_velocity, position, color)

        elif self.state == Firework.STATE_DETONATION:
            for p in self.particles:
                p.tick()

        self.particles = [p for p in self.particles if not p.dead()]

    def explode(self, direction, velocity, position, color):
        particles = []
        for _ in range(100):
            r, phi = Particle.vector_add(velocity, direction, 20 * random() + 50, 2 * PI * random())
            particles.append(Particle(direction=phi, velocity=r, position=position, color=color))

        return particles

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def dead(self):
        if not self.particles:
            return True

        return False


class FireworkDouble(Firework):
    def explode(self, direction, velocity, position, color):
        particles = []
        for _ in range(50):
            r, phi = Particle.vector_add(velocity, direction, 20 * random() + 80, 2 * PI * random())
            particles.append(Particle(direction=phi, velocity=r, position=position, color=color))

        color = choice(COLORS)
        for _ in range(50):
            r, phi = Particle.vector_add(velocity, direction, 20 * random() + 40, 2 * PI * random())
            particles.append(Particle(direction=phi, velocity=r, position=position, color=color))

        return particles


class FireworkStar(Firework):
    def explode(self, direction, velocity, position, color):
        particles = []
        angle = 2 * PI * random()
        for _ in range(100):
            phi = 2 * PI * random()
#            r = 100 * ((sin(5 * phi) + 1) / 2) + 100
            r = 100 * FireworkStar.sawtooth(5 * phi + angle) + 100 + 20 * random()

            r, phi = Particle.vector_add(velocity, direction, r, phi)

            particles.append(Particle(direction=phi, velocity=r, position=position, color=color))

        return particles

    @staticmethod
    def sawtooth(x):
        x = x % (2 * PI)

        if x < PI:
            return x / PI
        else:
            return 1.0 - ((x - PI) / PI)


pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode(DISPLAY_SIZE)

fireworks = []

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == 102:
            fireworks.append(choice([Firework, FireworkDouble, FireworkStar])())

    for firework in fireworks:
        firework.tick()

    fireworks = [f for f in fireworks if not f.dead()]

    window.fill(BACKGROUND)

    for firework in fireworks:
        firework.draw(window)

    # print(sum([len(f.particles) for f in fireworks]))

    pygame.display.flip()
    clock.tick(FPS)
