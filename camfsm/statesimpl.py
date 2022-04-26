from state import State

class IdleState(State):

    def on_event(self, event):

        if event == 'dms1':
            return RecordingState()

        return self



class RecordingState(State):
    
    def on_event(self, event):
        if event == 'dms0':
            return IdleState()
        if event == 'dms1':
            print(self.count)
            self.count+=1

        return self
    


