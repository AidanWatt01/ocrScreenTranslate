import win32api
from screeninfo import get_monitors

def get_monitor_from_mouse():
    x, y = win32api.GetCursorPos()
    for m in get_monitors():
        if m.x <= x <= m.x + m.width and m.y <= y <= m.y + m.height:
            return {'left': m.x, 'top': m.y, 'width': m.width, 'height': m.height}
    return {'left': 0, 'top': 0, 'width': 1920, 'height': 1080}
