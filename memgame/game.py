from gpiozero import Button, LED
from signal import pause
from . import logger
from .state_machine import Context, State


class Game():
    def __init__(self):
        self.buttons = [Button(10), Button(9), Button(11)]
        self.leds = [LED(17), LED(27), LED(22)]

        self.ctx = Context(WaitState())


    def run(self):
        for i, button in enumerate(self.buttons):
            button.when_pressed = lambda btn=button: self.ctx.on_event({'name': 'button_pressed', 'button': btn, 'num': i})
            button.when_released = lambda btn=button: self.ctx.on_event({'name': 'button_released', 'button': btn, 'num': i})

        pause()
       

class WaitState(State):
    def on_event(self, event):
        if event['name'] == 'button_pressed':
            logger.info('Starting game.')
            self._context.data['combination'] = []
            return ShowCombinationState()

        return self


class ShowCombinationState(State):
    def on_event(self, event):
        if event['name'] == 'button_pressed':
            return GameOverState()
        
        return self


class RepeatCombinationState(State):
    def on_event(self, event):
        if event['name'] == 'button_pressed':
            pass

        return self


class GameOverState(State):
    def on_event(self, event):
        if event['name'] == 'button_pressed':
            return WaitState()
        
        return self
