import pygame, sys
from pygame.locals import *
from random import random, choice, randint
from math import atan2, sqrt, cos, sin, pi as PI

from ..config import *


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
