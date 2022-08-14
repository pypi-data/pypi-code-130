import keyboard


def key(pressed: str):
    if keyboard.is_pressed(pressed):
        return True
