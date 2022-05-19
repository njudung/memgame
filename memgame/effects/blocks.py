import pygame
from pygame.locals import *
from random import random, choice, randint
from math import ceil

from ..config import *
from ..colors import BG

BLOCK_SIZE = 120

class Block():
	COLORS = [Color(66, 209, 15), Color(252, 237, 15), Color(234, 31, 17), Color(26, 79, 242)]
	
	def __init__(self):
		self.num_blocks_x = ceil(DISPLAY_SIZE[0] / BLOCK_SIZE)
		self.num_blocks_y = ceil(DISPLAY_SIZE[1] / BLOCK_SIZE)
		self.num_blocks = self.num_blocks_x * self.num_blocks_y
		self.blocks = [[1.0, 0.1, (0, 0, 0)]] * self.num_blocks

	def tick(self):
		for i in range(self.num_blocks):
			self.blocks[i][0] += self.blocks[i][1]
			
			if self.blocks[i][0] > 1.0:
				if randint(0, 9) == 0:
					self.blocks[i] = [0.0, random() / 100, choice(Block.COLORS)]
				else:
					c = randint(80, 120)
					self.blocks[i] = [0.0, random() / 100, Color(c, c, c)]

	def draw(self, surface):
		for i in range(self.num_blocks):
			x = i % self.num_blocks_x
			y = i // self.num_blocks_x
			color = self.blocks[i][2].lerp(BG, self.blocks[i][0])
			pygame.draw.rect(surface, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
		
