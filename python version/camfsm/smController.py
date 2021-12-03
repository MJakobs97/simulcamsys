from statemachine import StateMachine
#import keyboard
import time
#from pynput import keyboard
from gpiozero import Button
from signal import pause

def BT_connect_handler():
	print('button pressed')
	sm.on_event('dms1')

def BT_connect_release():
	print('button released')
	sm.on_event('dms0')
	

button = Button(3, hold_time=0.5)

sm = StateMachine()


try: 
	button.when_held = BT_connect_handler
	button.when_released = BT_connect_release
	pause()

finally: 
	pass