from statemachine import StateMachine
import time
import asyncio
from gpiozero import Button
from signal import pause

def BT_connect_handler():
 print('discovery button pressed!')
 sm.on_event('dms2')

def BT_rec_stop():
 print('recording trigger released!')
 sm.on_event('dms0')

def BT_rec_start():
 print('recording trigger pressed!')
 sm.on_event('dms1')

trigger = Button(3, hold_time=0.25)
button_conn = Button(4, hold_time=1)

sm = StateMachine()


try: 
	trigger.when_held = BT_rec_start
	trigger.when_released = BT_rec_stop
	button_conn.when_held = BT_connect_handler
	pause()

finally: 
	pass
