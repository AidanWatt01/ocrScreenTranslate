import dxcam
import numpy as np
import win32api
from screeninfo import get_monitors

camera = dxcam.create(output_idx=0)

def get_monitor_geometry_from_mouse():
    x, y = win32api.GetCursorPos()
    for m in get_monitors():
        if m.x <= x <= m.x + m.width and m.y <= y <= m.y + m.height:
            return {'left': m.x, 'top': m.y, 'width': m.width, 'height': m.height}
    # fallback
    return {'left': 0, 'top': 0, 'width': 1920, 'height': 1080}

def capture_active_monitor():
    geometry = get_monitor_geometry_from_mouse()
    region = (geometry['left'], geometry['top'],
              geometry['left'] + geometry['width'],
              geometry['top'] + geometry['height'])

    frame = camera.grab(region=region)
    if frame is None:
        raise RuntimeError("Screen capture failed")
    image_np = np.array(frame)
    return image_np, geometry
