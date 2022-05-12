#from guizero import App, Drawing
import pygame, sys
from pygame.locals import *
from .events import *
from .colors import *
from gpiozero import Button, LED
from signal import pause
from . import logger
from time import sleep
from random import randint


TICKS = 30
DISPLAY_SIZE = (1920, 1080)


class Game():
    def __init__(self):
        pygame.init()

        self.state = WaitState(self)
        self.next_state = None
 
        self.buttons = [Button(10), Button(9), Button(11)]
        self.leds = [LED(17), LED(27), LED(22)]
        self.combination = []
        self.position = 0
        self.highscore = Game.load_highscore()

        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont(None, 50)

        self.screen = pygame.display.set_mode(DISPLAY_SIZE)

        ## Initialize buttons
        for i, button in enumerate(self.buttons):
            button.when_pressed = lambda btn=button, num=i: pygame.event.post(pygame.event.Event(BUTTON_PRESSED, {'button': btn, 'num': num}))
            button.when_released = lambda btn=button, num=i: pygame.event.post(pygame.event.Event(BUTTON_RELEASED, {'button': btn, 'num': num}))


    def run(self):
        while True:
            for event in pygame.event.get():
                logger.debug("Processing event {}".format(event))
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.unicode == "f":
                    pygame.display.toggle_fullscreen()
                elif event.type == CHANGE_STATE:
                    self.next_state = event.next_state
                else:
                    self.state.on_event(event)
         
            self._draw()
            
            if self.next_state:
                old_state = self.state
                self.state = self.next_state(self)
                self.next_state = None
                pygame.event.post(pygame.event.Event(STATE_CHANGED, {"from": str(old_state)}))
                
            self.clock.tick(TICKS)


    def set_state(self, next_state):
        pygame.event.post(pygame.event.Event(CHANGE_STATE, {"next_state": next_state}))


    def _draw(self):
        self.screen.fill(BG)
        
        #if self.state: 
        self.state.draw()
        
        pygame.display.flip()


    def turn_off_leds(self):
        for led in self.leds:
            led.off()
        

    def turn_on_leds(self):
        for led in self.leds:
            led.on()


    def flash_leds(self, n=5, f=10):
        dt = 1/(f*2)
        
        for _ in range(n):
            self.turn_on_leds()
            sleep(dt)
            self.turn_off_leds()
            sleep(dt)
    
    
    @staticmethod
    def load_highscore():
        rv = []

        try:
            with open("highscore.txt") as fp:
                for line in fp.readlines():
                    rv.append(line.strip().split("|"))
        except FileNotFoundError:
            pass

        return rv


    @staticmethod
    def save_highscore(scores):
        with open("highscores.txt", "w") as fp:
            for name, score in scores.sort(lambda item: item[1]):
                fp.write(f"{name}|{score}")
            
            
class State():
    def __init__(self, game):
        logger.debug(f'Changing to state: {str(self)}')
        self.game = game


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        return self.__class__.__name__


    def draw(self):
        raise NotImplementedError


    def on_event(self, event):
        raise NotImplementedError


class WaitState(State):
    def on_event(self, event):
        if event.type == BUTTON_PRESSED:
            logger.info('Starting game.')
            self.combination = []  # Reset combination
            
            self.game.set_state(ShowCombinationState)

    def draw(self):
        font = self.game.font
        text = font.render("MinnesSpel", True, FG)
        self.game.screen.blit(text, (100, 100))


class StartGameState(State):
    def on_event(self, event):
        self.game.combination = []

        self.game.set_state(ShowCombinationState)


    def on_event(self, event):
        pass


    def draw(self):
        pass


class ShowCombinationState(State):
    def on_event(self, event):
        if event.type == STATE_CHANGED:
            nv = randint(0, len(self.game.leds) - 1)
            if len(self.game.combination) and nv == self.game.combination[-1]:
                nv = randint(0, len(self.game.leds) - 1)

            self.game.combination.append(nv)
            logger.debug('Combination updated to: {}'.format(', '.join([str(v) for v in self.game.combination])))

            self.position = 0

            self.ticks = 0
            pygame.time.set_timer(pygame.event.Event(TICK, {}), 100)


        if event.type == TICK:
            if self.ticks == 0:
                self.game.leds[self.game.combination[self.game.position]].on()
                self.game.position += 1

            if self.ticks == 8:
                self.game.turn_off_leds()
                
            self.ticks = (self.ticks + 1) % 10

            if self.game.position >= len(self.game.combination):
                pygame.time.set_timer(pygame.event.Event(TICK, {}), 0)
                self.game.set_state(RepeatCombinationState)
                return
 

    def draw(self):
        font = self.game.font

        n = len(self.game.combination)
        c = self.game.position

        text = font.render("{}{}".format("X" * c, "-" * (n - c)), True, FG)
        self.game.screen.blit(text, (100, 100))


class RepeatCombinationState(State):
    def on_event(self, event):
        if event.type == STATE_CHANGED:
            self.game.position = 0
            self.game.turn_off_leds()

        if event.type == BUTTON_PRESSED:
            """ Flash once to confirm correct button press. """
            self.game.leds[event.num].on()

        if event.type == BUTTON_RELEASED:
            """ Check for correct button press. """
            self.game.leds[event.num].off()

            # Correct button?
            if event.num == self.game.combination[self.game.position]:
                self.game.position += 1

                if self.game.position >= len(self.game.combination):
                    self.game.set_state(ShowCombinationState)

            else:
                self.game.set_state(GameOverState)
    
    
    def draw(self):
        font = self.game.font
        text = font.render("Repetera", True, FG)
        self.game.screen.blit(text, (100, 100))


class GameOverState(State):
    def on_event(self, event):
        if event.type == STATE_CHANGED:
            logger.info('Wrong button. Game over.')

            self.game.combination = []

            self.game.flash_leds()
        
        if event.type == BUTTON_PRESSED:
            self.game.set_state(WaitState)


    def draw(self):
        self.game.screen.fill(GAME_OVER_BG)
        font = self.game.font
        text = font.render("GAME OVER", True, GAME_OVER_FG)
        self.game.screen.blit(text, (100, 100))
