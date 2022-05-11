from guizero import App, Drawing
from gpiozero import Button, LED
from signal import pause
from . import logger
from .state_machine import Context, State
from time import sleep
from random import randint


class Game():
    def __init__(self):
        self.state = {
            'buttons': [Button(10), Button(9), Button(11)],
            'leds': [LED(17), LED(27), LED(22)],
            'combination': [],
            'position': 0,
            'highscore': Game.load_highscore()
            }


        self.app = App(title="Memgame", bg=(30, 30, 30))
        self.app.set_full_screen()
        self.drawing = Drawing(self.app, width="fill", height="fill")

        self.ctx = Context(self, WaitState())


    def run(self):
        for i, button in enumerate(self.state['buttons']):
            button.when_pressed = lambda btn=button, num=i: self.ctx.on_event({'name': 'button_pressed', 'button': btn, 'num': num})
            button.when_released = lambda btn=button, num=i: self.ctx.on_event({'name': 'button_released', 'button': btn, 'num': num})

        self.app.display()
    

    def turn_off_leds(self):
        for led in self.state['leds']:
            led.off()
        

    def turn_on_leds(self):
        for led in self.state['leds']:
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
            


class WaitState(State):
    def on_event(self, event):
        if event['name'] == 'init':
            dwg = self.drawing
            dwg.clear()
            dwg.text(10, 10, "MEMGAME", color=(250, 250, 250), size=50)
            dwg.text(10, 100, "Tryck på en knapp", color=(250, 250, 250), size=30)


        if event['name'] == 'button_pressed':
            logger.info('Starting game.')
            self.game_state['combination'] = []  # Reset combination
            return ShowCombinationState()

        return self


class StartGameState(State):
    def on_event(self, event):
        if event['name'] == 'init':
            dwg = self.drawing
            dwg.clear()
            dwg.text(10, 10, "", color=(250, 250, 250), size=50)
            dwg.text(10, 100, "Starting game", color=(250, 250, 250), size=30)

            self.game_state['combination'] = []
            self.game_state['position'] = 0
    
            sleep(1)
    
            return ShowCombinationState()
    
        return self
    

class ShowCombinationState(State):
    def on_event(self, event):
        if event['name'] == 'init':
            dwg = self.drawing
            dwg.clear()
            dwg.text(10, 10, "", color=(250, 250, 250), size=50)
            dwg.text(10, 100, "Memorera sekvensen!", color=(250, 250, 250), size=30)

            nv = randint(0, len(self.game_state['leds']) - 1)
            if len(self.game_state['combination']) and nv == self.game_state['combination'][-1]:
                nv = randint(0, len(self.game_state['leds']) - 1)

            self.game_state['combination'].append(nv)
            logger.debug('Combination updated to: {}'.format(', '.join([str(v) for v in self.game_state['combination']])))

            # Flash all leds once to indicate start of sequence.
            sleep(1)
            self.game.turn_on_leds()
            sleep(0.1)
            self.game.turn_off_leds()

            
            for v in self.game_state['combination']:
                self.game.turn_off_leds()
                sleep(0.1)

                self.game_state['leds'][v].on()
                sleep(1)

                self.game.turn_off_leds()

        return RepeatCombinationState()


class RepeatCombinationState(State):
    def on_event(self, event):
        if event['name'] == 'init':
            dwg = self.drawing
            dwg.clear()
            dwg.text(10, 100, "Upprepa sekvensen", color=(250, 250, 250), size=30)

            self.game_state['position'] = 0


        if event['name'] == 'button_pressed':
            """ Check for correct button press. """
            self.game_state['leds'][event['num']].on()

            # Correct button?
            if event['num'] == self.game_state['combination'][self.game_state['position']]:
                self.game_state['position'] += 1

                if self.game_state['position'] >= len(self.game_state['combination']):
                    return ShowCombinationState()

            else:
                logger.info('Wrong button. Game over.')
                
                self.game.flash_leds()
                
                return GameOverState()                                
        
        if event['name'] == 'button_released':
            """ Flash once to confirm correct button press. """
            self.game_state['leds'][event['num']].off()
            sleep(0.1)
            self.game_state['leds'][event['num']].on()
            sleep(0.05)
            self.game_state['leds'][event['num']].off()
            sleep(0.05)

        return self


class GameOverState(State):
    def on_event(self, event):
        if event['name'] == 'init':
            dwg = self.drawing
            dwg.clear()
            dwg.text(10, 10, "GAME OVER!", color=(250, 250, 250), size=50)
        
        if event['name'] == 'button_pressed':
            return WaitState()
        
        return self
