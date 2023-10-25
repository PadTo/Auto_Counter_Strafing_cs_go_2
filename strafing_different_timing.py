from pynput.keyboard import Key, Controller as KeyboardController, Listener as KeyboardListener
from pynput.mouse import Button, Controller as MouseController, Listener as MouseListener
import os
import threading
import time

# Initializing keyboard and mouse controllers
keyboard_controller = KeyboardController()
mouse_controller = MouseController()

# A dictionary for opposite in-game movement
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

# Global variables needed for the algorithm

simulated_press = False         # Is the press made by a human or the program?
active_keys = set()             # Tracking currently pressed keys

# This is to track the time between subsequent scrolls (I jump with scroll wheel), it deactivates the opposite movement while mid-air
mouse_scroll_times = 0
enabled = True                  # A condition for activation an de-activation of the code
# This is the condition of when you are jumping, if you are, then it is set to True
activated = False

# Press function


def on_press_button(key):
    global simulated_press
    global pressed_time
    global enabled
    try:

        # When q is pressed, quit the entire program
        if key.char == 'q':
            os._exit(0)
        # When t is pressed, pause the program
        if key.char == 't':
            enabled = not enabled
            return
        if not enabled:
            return

        if simulated_press:
            simulated_press = False
            return

        # Tracking currently pressed key and time of the press
        if key.char in counter_movement:
            pressed_time = time.time()
            active_keys.add(key.char)
            # print(active_keys)

    except AttributeError:
        pass

# A function where the opposite press time of a key is correlated with the players momentum (These values came purely from testing in-game)


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

# Release function


def on_release_button(key):
    global simulated_press, active_keys, pressed_time
    global activated
    global released_time

    try:
        if key.char in active_keys:

            # Tracking the release time and removing the button from active keys
            released_time = time.time()
            active_keys.remove(key.char)
            counter_key = counter_movement.get(key.char)
            time_between_press_and_release = released_time - pressed_time

            # print(time_between_press_and_release)

            # This condition takes into account if you are in mid-air and if the keys your holding is equal to 1.
            # It is important to note that the "len(active_keys) >= 1" condition is implemented due to whacky movement while moving forward continuously
            # while moving forward continuously and then trying to move left or right
            if counter_key and not activated and not len(active_keys) >= 1:

                simulated_press = True
                keyboard_controller.press(counter_key)
                sleep_duration = get_sleep_duration(
                    time_between_press_and_release)
                time.sleep(sleep_duration)
                keyboard_controller.release(counter_key)

    except AttributeError:
        pass

# While air-born function


def active_for_one_second(dy):
    global activated
    global mouse_scroll_times
    scroll_threshold = 0.05  # This is simply the the threshold time between scrolls

    current_time = time.time()
    duration_since_last_scroll = current_time - mouse_scroll_times
    mouse_scroll_times = current_time

    # If jumped then activate the jumping condition "activated"
    if dy > 0 and duration_since_last_scroll > scroll_threshold:
        activated = True
        time.sleep(1.2)
        activated = False

# Scrolling function


def on_scroll(x, y, dx, dy):
    threading.Thread(target=active_for_one_second, args=(dy,)).start()


Keyboard_Listener = KeyboardListener(
    on_press=on_press_button, on_release=on_release_button)
mouse_listener = MouseListener(on_scroll=on_scroll)

Keyboard_Listener.start()
mouse_listener.start()

Keyboard_Listener.join()
mouse_listener.join()
