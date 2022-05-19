import pygame
from pygame.locals import *
from random import random, choice, randint

from ..config import *
from ..colors import *


SPEED = 1000 * TICKS


class Line():
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.length = 3000
            
    def tick(self):
        self.x -= SPEED / TICKS
        self.y += 0.2 * SPEED / TICKS
        
    def draw(self, surface):
        pygame.draw.line(surface, self.color, (self.x, self.y), (self.x + self.length, self.y - self.length * 0.2), width=5)

    def dead(self):
        return self.x + self.length < 0


class Lines():
    COLORS = [Color(66, 209, 15), Color(252, 237, 15), Color(234, 31, 17), Color(26, 79, 242)]

    def __init__(self):
        self.lines = []

        self.surface = pygame.Surface((DISPLAY_SIZE[0], DISPLAY_SIZE[1] * 1.4))


    def tick(self):
        for line in self.lines:
            line.tick()

        if randint(0, 9) == 0:
            color = choice(Lines.COLORS)
        else:
            c = randint(80, 120)
            color = Color(c, c, c)
        
        
        self.lines.append(Line(
            DISPLAY_SIZE[0] - 1 + randint(0, 500), 
            (DISPLAY_SIZE[1] + DISPLAY_SIZE[0] * 0.4) * random() - DISPLAY_SIZE[0] * 0.2, 
            color
        ))

        self.lines = [line for line in self.lines if not line.dead()]


    def draw(self, surface):
        self.surface.fill(BG)

        for line in self.lines:
            line.draw(surface)
        
        self.surface.blit(surface, (0, - DISPLAY_SIZE[1] * 0.2))
        

    def _dead(self):
        if self.x + self.length < 0:
            return True
        return False
