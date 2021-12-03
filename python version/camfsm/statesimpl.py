from state import State
import subprocess

class IdleState(State):

    def on_event(self, event):

       if event == 'dms1':
	#this has to be exchanged with main.py -- [addresses] start call
           subprocess.run("./ble_find_and_connect.sh")
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
    


