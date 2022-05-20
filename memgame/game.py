# from guizero import App, Drawing
import pygame, sys, os
from pygame.locals import *
from gpiozero import Button, LED
from signal import pause
from time import sleep
from random import randint, choice
from . import logger
from .events import *
from .colors import *
from .state import State
from .effects.lines import Lines
from .effects.fireworks import FireworkDouble
from .config import *


def middle_pos(src, dest):
    x = (dest.get_width() - src.get_width()) / 2
    y = (dest.get_height() - src.get_height()) / 2
    return (x, y)


def center_pos(src, dest):
    return (dest.get_width() - src.get_width()) / 2


class Game:
    def __init__(self, kiosk=False):
        pygame.init()

        self.state = WaitState(self)
        #self.state = HighScoreState(self)
        self.next_state = None

        self.buttons = [Button(10), Button(9), Button(11)]
        self.leds = [LED(17), LED(27), LED(22)]
        self.combination = []
        self.position = 0
        self.highscore = Game.load_highscore()

        self.clock = pygame.time.Clock()

        self.font_normal = pygame.font.SysFont(None, 50)
        self.font_large = pygame.font.SysFont(None, 150)
        self.font_xlarge = pygame.font.SysFont(None, 350)

        self.screen = pygame.display.set_mode(DISPLAY_SIZE)
        if kiosk: pygame.display.toggle_fullscreen()

        ## Initialize buttons
        for i, button in enumerate(self.buttons):
            button.when_pressed = lambda btn=button, num=i: pygame.event.post(
                pygame.event.Event(BUTTON_PRESSED, {"button": btn, "num": num})
            )
            button.when_released = lambda btn=button, num=i: pygame.event.post(
                pygame.event.Event(BUTTON_RELEASED, {"button": btn, "num": num})
            )

    def run(self):
        while True:
            for event in pygame.event.get():
                # logger.debug("Processing event {}".format(event))
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.unicode == "f":
                    pygame.display.toggle_fullscreen()
                elif event.type == CHANGE_STATE:
                    self.next_state = event.next_state
                else:
                    self.state.on_event(event)

            self._tick()

            self._draw()

            if self.next_state:
                old_state = self.state
                self.state = self.next_state(self)
                self.next_state = None
                pygame.event.post(pygame.event.Event(STATE_CHANGED, {"from": str(old_state)}))

            self.clock.tick(TICKS)

    def set_state(self, next_state):
        pygame.event.post(pygame.event.Event(CHANGE_STATE, {"next_state": next_state}))

    def _tick(self):
        self.state.tick()

    def _draw(self):
        self.screen.fill(BG)

        # if self.state:
        self.state.draw()

        pygame.display.flip()

    def turn_off_leds(self):
        for led in self.leds:
            led.off()

    def turn_on_leds(self):
        for led in self.leds:
            led.on()

    def flash_leds(self, n=5, f=10):
        dt = 1 / (f * 2)

        for _ in range(n):
            self.turn_on_leds()
            sleep(dt)
            self.turn_off_leds()
            sleep(dt)

    @staticmethod
    def load_highscore():
        filename = os.path.join(BASE_DIR, "highscore.txt")
        rv = []

        try:
            with open(filename) as fp:
                for line in fp.readlines():
                    rv.append(line.strip().split("|"))
        except FileNotFoundError:
            logger.info(f"No {filename} found.")

        return rv

    @staticmethod
    def save_highscore(scores):
        with open(of.path.join(BASE_DIR, "highscores.txt"), "w") as fp:
            for name, score in scores.sort(lambda item: item[1]):
                fp.write(f"{name}|{score}")


class WaitState(State):
    def __init__(self, game):
        State.__init__(self, game)
        
        self.effect = Lines()

    def on_event(self, event):
        if event.type == BUTTON_PRESSED:
            logger.info("Starting game.")
            self.combination = []  # Reset combination

            self.game.set_state(ShowCombinationState)

    def tick(self):
        self.effect.tick()


    def draw(self):
        self.effect.draw(self.game.screen)

        font = self.game.font_large
        text = font.render("MinnesSpel", True, FG)
        self.game.screen.blit(text, (center_pos(text, self.game.screen), 100))

        font = self.game.font_normal
        center = self.game.screen.get_width() / 2

        for i, (score, name) in enumerate(self.game.highscore):
            score = font.render(score, True, FG)
            name = font.render(name, True, FG)

            self.game.screen.blit(score, (center - score.get_width() - 10, 60 * i + 300))
            self.game.screen.blit(name, (center + 10, 60 * i + 300))


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
            logger.debug(
                "Combination updated to: {}".format(
                    ", ".join([str(v) for v in self.game.combination])
                )
            )

            self.game.position = 0

            self.ticks = 0
            pygame.time.set_timer(pygame.event.Event(TICK, {}), 100)

        if event.type == TICK:
            if self.ticks == 0:
                self.game.leds[self.game.combination[self.game.position]].on()

            if self.ticks == 8:
                self.game.turn_off_leds()

            if self.ticks == 9:
                self.game.position += 1

                if self.game.position >= len(self.game.combination):
                    pygame.time.set_timer(pygame.event.Event(TICK, {}), 0)
                    self.game.set_state(RepeatCombinationState)

            self.ticks = (self.ticks + 1) % 10

    def draw(self):
        font = self.game.font_large
        pos = (
            self.game.position <= len(self.game.combination)
            if self.game.position
            else len(self.game.combination)
        )

        text = font.render(str(pos), True, FG)
        self.game.screen.blit(text, (100, 100))


class RepeatCombinationState(State):
    def on_event(self, event):
        if event.type == STATE_CHANGED:
            self.game.position = 0
            self.game.turn_off_leds()

        if event.type == BUTTON_PRESSED:
            """Flash once to confirm correct button press."""
            self.game.leds[event.num].on()

        if event.type == BUTTON_RELEASED:
            """Check for correct button press."""
            self.game.leds[event.num].off()

            # Correct button?
            if event.num == self.game.combination[self.game.position]:
                self.game.position += 1

                if self.game.position >= len(self.game.combination):
                    self.game.set_state(ShowCombinationState)

            else:
                if True:
                    self.game.set_state(HighScoreState)
                else:
                    self.game.set_state(GameOverState)

    def draw(self):
        font = self.game.font_large
        text = font.render("Repetera", True, FG)
        self.game.screen.blit(text, middle_pos(text, self.game.screen))


class GameOverState(State):
    def on_event(self, event):
        if event.type == STATE_CHANGED:
            logger.info("Wrong button. Game over.")

            self.game.combination = []

            self.game.flash_leds()

        if event.type == BUTTON_PRESSED:
            self.game.set_state(WaitState)

    def draw(self):
        self.game.screen.fill(GAME_OVER_BG)
        font = self.game.font_xlarge
        text = font.render("GAME OVER", True, GAME_OVER_FG)
        self.game.screen.blit(text, middle_pos(text, self.game.screen))


class HighScoreState(State):
    fireworks = [FireworkDouble() for _ in range(3)]

    symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def on_event(self, event):
        if event.type == STATE_CHANGED:
            self.current_pos = 0
            self.name = ""
        if event.type == BUTTON_PRESSED:
            if event.num == 0:
                self.current_pos -= 1
                if self.current_pos < 0:
                    self.current_pos = len(HighScoreState.symbols) - 1
            if event.num == 1:
                if len(self.name) < 3:
                    self.name += HighScoreState.symbols[self.current_pos]
            if event.num == 2:
                self.current_pos += 1
                if self.current_pos >= len(HighScoreState.symbols):
                    self.current_pos = 0


    def tick(self):
        if randint(0, 29) == 0:
            self.fireworks.append(FireworkDouble())
        
        for firework in self.fireworks:
            firework.tick()

        self.fireworks = [f for f in self.fireworks if not f.dead()]


    def draw(self):
        for firework in self.fireworks:
            firework.draw(self.game.screen)

        font = self.game.font_xlarge

        for i in range(3):
            x = self.game.screen.get_width() // 2 - 300
            y = self.game.screen.get_height() // 2
            pygame.draw.rect(self.game.screen, HIGH_SCORE_COMP, (x - 125 + 300 * i, y - 150, 250, 300))

            letter = font.render(self.name[i] if len(self.name) > i else "A", True, HIGH_SCORE_FG)
            self.game.screen.blit(letter, (x + 300 * i - letter.get_width() // 2, y - letter.get_height() + 130 ))

        letter = font.render(HighScoreState.symbols[self.current_pos], True, HIGH_SCORE_HL)
        self.game.screen.blit(letter, (x + 300 * len(self.name) - letter.get_width() // 2, y - letter.get_height() + 130))
