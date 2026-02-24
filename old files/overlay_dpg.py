import dearpygui.dearpygui as dpg
import threading

class OverlayWindow:
    def __init__(self, text_data, geometry):
        self.text_data = text_data
        self.geometry = geometry
        self.running = True

        self.overlay_thread = threading.Thread(target=self.run_overlay, daemon=True)
        self.overlay_thread.start()

    def run_overlay(self):
        dpg.create_context()

        dpg.create_viewport(title="Translation Overlay",
                            width=self.geometry["width"],
                            height=self.geometry["height"],
                            x_pos=self.geometry["left"],
                            y_pos=self.geometry["top"],
                            decorated=False,
                            clear_color=(0, 0, 0, 0))  # Fully transparent

        dpg.setup_dearpygui()
        dpg.set_viewport_always_top(True)
        dpg.show_viewport()

        # === Drawing layer ===
        with dpg.window(label="Overlay", tag="OverlayWindow",
                        no_background=True, no_title_bar=True,
                        no_resize=True, no_move=True, no_collapse=True):
            dpg.add_drawlist(width=self.geometry["width"], height=self.geometry["height"], tag="OverlayDraw")

        self.redraw()

        # === Tooltip window for translation ===
        with dpg.window(tag="OverlayHoverTip",
                        no_title_bar=True,
                        no_move=True,
                        no_resize=True,
                        no_close=True,
                        no_collapse=True,
                        no_scrollbar=True,
                        show=False):
            dpg.add_text("", tag="HoverText")

        # === Input handlers ===
        with dpg.handler_registry():
            dpg.add_key_release_handler(callback=self.handle_key)
            dpg.add_mouse_move_handler(callback=self.update_hover)

        dpg.start_dearpygui()
        dpg.destroy_context()

    def redraw(self):
        dpg.delete_item("OverlayDraw", children_only=True)
        for item in self.text_data:
            x, y, w, h = self.bbox_to_rect(item['bbox'])
            dpg.draw_rectangle((x, y), (x + w, y + h),
                            color=(255, 0, 0, 255),
                            fill=(0, 0, 0, 120),
                            thickness=2,
                            parent="OverlayDraw")


    def update_hover(self, sender, app_data):
        mouse_x, mouse_y = dpg.get_mouse_pos()
        for item in self.text_data:
            x, y, w, h = self.bbox_to_rect(item['bbox'])
            if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                en = item.get("translation", "[no translation]")
                dpg.set_value("HoverText", en)
                dpg.configure_item("OverlayHoverTip", show=True)
                dpg.set_item_pos("OverlayHoverTip", [mouse_x + 10, mouse_y + 10])
                return
        dpg.configure_item("OverlayHoverTip", show=False)

    def handle_key(self, sender, app_data):
        if app_data in (256, 298):  # Escape or F9
            print("[Overlay] Hiding on key")
            self.hide()

    def bbox_to_rect(self, bbox):
        xs = [pt[0] for pt in bbox]
        ys = [pt[1] for pt in bbox]
        x, y = min(xs), min(ys)
        w, h = max(xs) - x, max(ys) - y
        return int(x), int(y), int(w), int(h)

    # === New Methods for Smart Refresh ===
    def update_data(self, new_text_data):
        self.text_data = new_text_data
        self.redraw()

    def show(self):
        dpg.configure_viewport(item="__main_viewport", show=True)

    def hide(self):
        dpg.configure_viewport(item="__main_viewport", show=True)
