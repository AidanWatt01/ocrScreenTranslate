import keyboard
from overlay_pygame import OverlayWindow
from capture import capture_active_monitor
from ocr import extract_japanese_text
from translator import translate_batch

class Controller:
    def __init__(self):
        self.overlay = None
        keyboard.add_hotkey("F8", self.launch_or_refresh_overlay)
        keyboard.add_hotkey("F9", self.hide_overlay)
        print("F8 = Show/Refresh overlay | F9 = Hide overlay | Ctrl+C = Quit")

    def launch_or_refresh_overlay(self):
        print("[Overlay] Launch requested...")

        try:
            # Step 1: Capture screen
            image_np, geometry = capture_active_monitor()

            # Step 2: OCR
            data = extract_japanese_text(image_np)

            if not data:
                print("[Overlay] No Japanese text found.")
                return

            # Step 3: Translate
            translations = translate_batch([d['text'] for d in data])
            for i, item in enumerate(data):
                item['translation'] = translations[i]

            # Step 4: Create or update overlay
            if self.overlay is None:
                self.overlay = OverlayWindow(data, geometry)
                self.overlay.show()
            else:
                self.overlay.update_data(data)
                self.overlay.show()

        except Exception as e:
            print(f"[ERROR] Failed to launch/refresh overlay: {e}")

    def hide_overlay(self):
        if self.overlay:
            print("[Overlay] Hiding overlay")
            self.overlay.hide()
