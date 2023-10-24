from pynput.keyboard import Key, Controller as KeyboardController, Listener as KeyboardListener
from pynput.mouse import Button, Controller as MouseController, Listener as MouseListener
import os
import threading
import time


keyboard_controller = KeyboardController()
mouse_controller = MouseController()
counter_movement = {
    'a': 'd',
    'd': 'a',
    's': 'w',
    'w': 's',
    'as': 'dw',
    'sa': 'wd',
    'ds': 'aw',
    'sd': 'wa',
    'wd': 'sa',
    'dw': 'as',
    'wa': 'sd',
    'aw': 'ds'
}
simulated_press = False
active_keys = set()
key_press_times = 0
long_press_duration = 0.05
short_press_duration = 0.07
mouse_scroll_times = 0

activated = False


# def on_press_mouse(self, x, y, button, pressed):
#       if button == Button.left and pressed:


def on_press_button(key):
    global simulated_press
    global key_press_times
    global is_long_press
    global is_short_press

    try:
        if key.char == 'q':
            os._exit(0)
        if simulated_press:
            simulated_press = False
            return
        if key.char in counter_movement:
            current_time = time.time()
            last_press_time = key_press_times
            active_keys.add(key.char)
            duration_since_last_press = current_time - last_press_time
            key_press_times = current_time
            is_long_press = duration_since_last_press < long_press_duration
            is_short_press = duration_since_last_press > short_press_duration
    except AttributeError:
        pass


def on_release_button(key):
    global simulated_press, active_keys, is_long_press, is_short_press
    global activated
    try:
        if key.char in active_keys:
            active_keys.remove(key.char)
            counter_key = counter_movement.get(key.char)

            if counter_key and not activated and not len(active_keys) >= 1:

                simulated_press = True
                keyboard_controller.press(counter_key)
                if is_long_press:
                    time.sleep(0.12)
                if is_short_press:
                    time.sleep(0.04)
                keyboard_controller.release(counter_key)

    except AttributeError:
        pass


def active_for_one_second(dy):
    global activated
    global mouse_scroll_times
    scroll_threshold = 0.05

    current_time = time.time()
    duration_since_last_scroll = current_time - mouse_scroll_times
    mouse_scroll_times = current_time

    if dy > 0 and duration_since_last_scroll > scroll_threshold:
        activated = True
        time.sleep(1.2)
        activated = False


def on_scroll(x, y, dx, dy):
    threading.Thread(target=active_for_one_second, args=(dy,)).start()


Keyboard_Listener = KeyboardListener(
    on_press=on_press_button, on_release=on_release_button)
mouse_listener = MouseListener(on_scroll=on_scroll)

Keyboard_Listener.start()
mouse_listener.start()

Keyboard_Listener.join()
mouse_listener.join()
