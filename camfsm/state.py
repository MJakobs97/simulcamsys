class State(object):
    count = 0
    def __init__(self):
        print ('Switching to: ', str(self))
        self.count = 0

    def on_event(self, event):

        pass

    def __repr__(self):

        return self.__str__()

    def __str__(self):

        return self.__class__.__name__
    
