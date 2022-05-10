from guizero import App
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
            'position': 0
            }

        self.ctx = Context(self, WaitState())


    def run(self):
        for i, button in enumerate(self.state['buttons']):
            button.when_pressed = lambda btn=button, num=i: self.ctx.on_event({'name': 'button_pressed', 'button': btn, 'num': num})
            button.when_released = lambda btn=button, num=i: self.ctx.on_event({'name': 'button_released', 'button': btn, 'num': num})

        pause()
    

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
       

class WaitState(State):
    def on_event(self, event):
        if event['name'] == 'button_pressed':
            logger.info('Starting game.')
            self.game_state['combination'] = []  # Reset combination
            return ShowCombinationState()

        return self


class ShowCombinationState(State):
    def on_event(self, event):
        self.game_state['combination'].append(randint(0, len(self.game_state['leds']) - 1))
        self.game_state['position'] = 0

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
        if event['name'] == 'button_pressed':
            """ Check for correct button press. """
            self.game_state['leds'][event['num']].on()

            # Correct button?
            if event['num'] == self.game_state['combination'][self.game_state['position']]:
                self.game_state['position'] += 1
            else:
                logger.info('Wrong button. Game over.')
                
                self.game.flash_leds()
                
                return GameOverState()                
                
            if self.game_state['position'] >= len(self.game_state['combination']):
                return ShowCombinationState()
        
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
        if event['name'] == 'button_pressed':
            return WaitState()
        
        return self
