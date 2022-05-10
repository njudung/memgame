from . import logger


class Context():
    def __init__(self, game, state):
        self._state = state
        self._state.context = self
        self.game = game


    def on_event(self, event):
        logger.debug('Event: {}'.format(event))
        self._state = self._state.on_event(event)
        self._state.context = self
        

class State():
    def __init__(self):
        logger.debug(f'Processing current state: {str(self)}')
        self.context = None

    
    def on_event(self, event):
        raise NotImplementedError()


    @property
    def game_state(self):
        raise Exception()

    @game_state.getter
    def game_state(self):
        return self.context.game.state


    @property
    def game(self):
        raise Exception()
    
    @game.getter
    def game(self):
        return self.context.game


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        return self.__class__.__name__
