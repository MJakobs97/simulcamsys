from statemachine import StateMachine
import keyboard
import time
from pynput import keyboard

sm = StateMachine()

def on_press(key):
        try:
            ##print('Alphanumeric key pressed: {0} '.format(key.char))
            ##print('Key that is currently being held down: {0}'.format(key.char))
            if format(key.char) == 'r':
                sm.on_event('dms1')
                
        except AttributeError:
            print('')

def on_release(key):
        try:
            if format(key.char) == 'r':
                sm.on_event('dms0')
                
            if key == keyboard.Key.esc:
                # Stop listener
                return False
        except AttributeError:
            print('')

# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
