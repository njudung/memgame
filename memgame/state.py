from . import logger


class State:
    def __init__(self, game):
        logger.debug(f"Changing to state: {str(self)}")
        self.game = game

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__
        
    def tick(self):
        pass

    def draw(self):
        raise NotImplementedError

    def on_event(self, event):
        raise NotImplementedError
