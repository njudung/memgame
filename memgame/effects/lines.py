import pygame, sys
from pygame.locals import *
from random import random, choice, randint
from math import atan2, sqrt, cos, sin, pi as PI

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
]

BACKGROUND = Color(30, 30, 30)


class Line:
    COLORS = [Color(66, 209, 15), Color(252, 237, 15), Color(234, 31, 17), Color(26, 79, 242)]

    def __init__(self):
        self.x = DISPLAY_SIZE[0] - 1
        self.y = (DISPLAY_SIZE[1] + DISPLAY_SIZE[0] * 0.4) * random() - DISPLAY_SIZE[0] * 0.2
        self.rate = randint(10, 15)
        self.length = 100 * randint(5, 9)
        self.width = 60
        c = randint(80, 119)
        self.color = Color(c, c, c)
        if randint(0, 4) == 0:
            self.color = choice(Line.COLORS)

    def tick(self):
        self.x -= self.rate
        self.y += self.rate * 0.2

    def draw(self, surface):
#        pygame.draw.line(
#            surface, self.color, start_pos=(self.x, self.y), end_pos=(self.x + self.length, self.y - self.length * 0.2), width=self.width
#        )
        points = ((self.x, self.y - 30), (self.x + self.length, self.y - self.length * 0.2 - 30), (self.x + self.length, self.y - self.length * 0.2 + 30), (self.x, self.y + 30))
        pygame.draw.polygon(surface, self.color, points)

    def dead(self):
        if self.x + self.length < 0:
            return True
        return False


pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode(DISPLAY_SIZE)

lines = []

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == 102:
            lines.append(Line())

    for line in lines:
        line.tick()

    if randint(0, 19) == 0:
        lines.append(Line())

    lines = [line for line in lines if not line.dead()]


    surface = pygame.Surface((DISPLAY_SIZE[0], DISPLAY_SIZE[1] * 1.4))
    surface.fill(BACKGROUND)

    for line in lines:
        line.draw(surface)
    
    window.blit(surface, (0, - DISPLAY_SIZE[1] * 0.2))

    pygame.display.flip()
    clock.tick(FPS)
