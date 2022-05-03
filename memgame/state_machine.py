from . import logger


class Context():
    def __init__(self, state):
        self._state = state
        self._state._context = self
        self.data = {}


    def on_event(self, event):
        self._state = self._state.on_event(event)
        self._state._context = self


class State():
    def __init__(self):
        logger.debug(f'Processing current state: {str(self)}')
    
    
    @property
    def context(self):
        return self._context
        
    @context.setter
    def context(self, context):
        self._context = context
    
    
    def on_event(self, event):
        raise NotImplementedError()


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        return self.__class__.__name__
