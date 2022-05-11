from . import logger


class Context():
    def __init__(self, game, state):
        self._state = state
        self._state.context = self
        self.game = game
        self._state.on_event({'name': 'init'})


    def on_event(self, event):
        logger.debug('Event: {}'.format(event))
        new_state = self._state.on_event(event)
        
        if not self._state is new_state:
            self._state = new_state
            self._state.context = self
            self._state.on_event({'name': 'init'})


class State():
    def __init__(self):
        logger.debug(f'Processing current state: {str(self)}')
        self.context = None


    def on_event(self, event):
        raise NotImplementedError()


    @property
    def drawing(self):
        raise Exception()


    @drawing.getter
    def drawing(self):
        return self.context.game.drawing


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
