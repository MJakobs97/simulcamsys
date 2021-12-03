from statesimpl import IdleState

class StateMachine(object):

    def __init__(self):
        self.state = IdleState()

    def on_event(self, event):
        self.state = self.state.on_event(event)
