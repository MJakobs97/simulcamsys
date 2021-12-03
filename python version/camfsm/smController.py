from statemachine import StateMachine
import time
from gpiozero import Button
from signal import pause

def BT_connect_handler():
	print('button pressed')
	sm.on_event('dms2')

def BT_rec_stop():
	print('trigger released')
	sm.on_event('dms0')

def BT_rec_start():
	print('trigger pressed')
	sm.on_event('dms1')	

trigger = Button(3, hold_time=0.5)

sm = StateMachine()


try: 
	trigger.when_held = BT_rec_start
	trigger.when_released = BT_rec_stop
	pause()

finally: 
	pass