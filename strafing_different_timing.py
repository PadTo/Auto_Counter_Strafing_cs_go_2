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
enabled = True

activated = False


def on_press_button(key):
    global simulated_press
    global key_press_times
    global pressed_time
    global enabled
    try:

        if key.char == 'q':
            os._exit(0)
        if key.char == 't':
            enabled = not enabled
            return
        if not enabled:
            return

        if simulated_press:
            simulated_press = False
            return
        if key.char in counter_movement:
            pressed_time = time.time()
            active_keys.add(key.char)
            # print(active_keys)

    except AttributeError:
        pass


def get_sleep_duration(time_between_press_and_release):
    if time_between_press_and_release < 0.005:
        return 0.01
    elif 0.005 <= time_between_press_and_release < 0.04:
        return 0.11
    elif 0.04 <= time_between_press_and_release < 0.06:
        return 0.01
    elif 0.06 <= time_between_press_and_release < 0.12:
        return 0.02
    elif 0.12 <= time_between_press_and_release < 0.2:
        return 0.055
    elif 0.2 <= time_between_press_and_release < 0.25:
        return 0.07
    elif 0.25 <= time_between_press_and_release < 0.28:
        return 0.08
    elif 0.28 <= time_between_press_and_release < 0.35:
        return 0.09
    elif 0.35 <= time_between_press_and_release < 0.44:
        return 0.1
    elif 0.44 <= time_between_press_and_release < 0.5:
        return 0.11
    elif time_between_press_and_release >= 0.5:
        return 0.11
    else:
        return 0  # Default case


def on_release_button(key):
    global simulated_press, active_keys, pressed_time
    global activated
    global released_time

    try:
        if key.char in active_keys:
            released_time = time.time()
            active_keys.remove(key.char)
            counter_key = counter_movement.get(key.char)

            time_between_press_and_release = released_time - pressed_time
            print(time_between_press_and_release)

            if counter_key and not activated and not len(active_keys) >= 1:

                simulated_press = True
                keyboard_controller.press(counter_key)
                sleep_duration = get_sleep_duration(
                    time_between_press_and_release)
                time.sleep(sleep_duration)
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
