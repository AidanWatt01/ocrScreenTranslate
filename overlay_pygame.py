import pygame
import win32gui
import win32con
import win32api
import threading
import time
import os

class OverlayWindow:
    def __init__(self, text_data, geometry):
        self.text_data = text_data
        self.geometry = geometry
        self.running = False
        self.thread = None
        self.hwnd = None
        self.hovered_item = None
        self.clicked_item = None
        self.tooltip_parts = None
        self.box_parts = None
        self.tooltip_alpha = 0
        self.tooltip_target_alpha = 255
        self.tooltip_pos = (0, 0)
        self.tooltip_text = ""


    def show(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_overlay, daemon=True)
            self.thread.start()
        else:
            self.update_data(self.text_data)

    def hide(self):
        self.running = False
        time.sleep(0.1)

    def update_data(self, new_text_data):
        self.text_data = new_text_data
        self.hovered_item = None
        self.clicked_item = None

    def _run_overlay(self):
        pygame.init()
        width, height = self.geometry["width"], self.geometry["height"]
        screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
        hwnd = pygame.display.get_wm_info()["window"]
        self.hwnd = hwnd

        self._make_window_transparent(hwnd)
        self._set_clickable(True)

        font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 18)
        big_font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 24)
        clock = pygame.time.Clock()

        self._load_tooltip_parts()
        self._load_box_parts()

        while self.running:
            screen.fill((255, 0, 255))  # Transparency key
            mouse_pos = pygame.mouse.get_pos()
            self.hovered_item = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for item in self.text_data:
                        x, y, w, h = self._bbox_to_rect(item["bbox"])
                        if pygame.Rect(x, y, w, h).collidepoint(mouse_pos):
                            self.clicked_item = item
                            break

            for item in self.text_data:
                x, y, w, h = self._bbox_to_rect(item["bbox"])
                rect = pygame.Rect(x, y, w, h)
                self._draw_box_with_border(screen, rect, self.box_parts)

                if rect.collidepoint(mouse_pos):
                    self.hovered_item = item

            if self.hovered_item:
                tx = self.hovered_item.get("translation", "")
                if tx:
                    self.tooltip_text = tx
                    self.tooltip_target_alpha = 255
                    self.tooltip_pos = self._get_smart_tooltip_position(mouse_pos, tx, font)
                    self.tooltip_alpha = min(self.tooltip_alpha + 15, 255)
                    self._draw_tooltip_with_border(screen, font, self.tooltip_pos, tx, self.tooltip_alpha)
            else:
                self.tooltip_alpha = max(self.tooltip_alpha - 20, 0)
                if self.tooltip_alpha > 0 and self.tooltip_text:
                    self._draw_tooltip_with_border(screen, font, self.tooltip_pos, self.tooltip_text, self.tooltip_alpha)


            if self.clicked_item:
                tx = self.clicked_item.get("translation", "")
                if tx:
                    self._draw_expanded_box(screen, big_font, tx)

            pygame.display.update()
            clock.tick(30)

        pygame.display.quit()
        pygame.quit()

    def _set_clickable(self, enable=True):
        style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        if enable:
            style &= ~win32con.WS_EX_TRANSPARENT
        else:
            style |= win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, style)

    def _make_window_transparent(self, hwnd):
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

        win32gui.SetLayeredWindowAttributes(
            hwnd,
            win32api.RGB(255, 0, 255),  # Magenta = transparency key
            0,
            win32con.LWA_COLORKEY
        )

        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            self.geometry["left"],
            self.geometry["top"],
            self.geometry["width"],
            self.geometry["height"],
            win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW | win32con.SWP_NOSENDCHANGING | win32con.SWP_NOOWNERZORDER
        )


    def _draw_box_with_border(self, surface, rect, parts):
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        tile_w, tile_h = parts["c"].get_size()

        # Corners
        surface.blit(parts["tl"], (x, y))
        surface.blit(parts["tr"], (x + w - tile_w, y))
        surface.blit(parts["bl"], (x, y + h - tile_h))
        surface.blit(parts["br"], (x + w - tile_w, y + h - tile_h))

        # Top / Bottom edges
        for i in range(x + tile_w, x + w - tile_w, tile_w):
            surface.blit(parts["t"], (i, y))
            surface.blit(parts["b"], (i, y + h - tile_h))

        # Left / Right edges
        for j in range(y + tile_h, y + h - tile_h, tile_h):
            surface.blit(parts["l"], (x, j))
            surface.blit(parts["r"], (x + w - tile_w, j))


    def _draw_tooltip_with_border(self, surface, font, pos, text, alpha=255):
        parts = self.tooltip_parts
        padding = 6

        def render_text_with_outline(text, font, color, outline_color):
            base = font.render(text, True, color)
            outline = pygame.Surface((base.get_width() + 2, base.get_height() + 2), pygame.SRCALPHA)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx != 0 or dy != 0:
                        outline.blit(font.render(text, True, outline_color), (1 + dx, 1 + dy))
            outline.blit(base, (1, 1))
            return outline

        text_surf = render_text_with_outline(text, font, (255, 255, 255), (150, 100, 200))
        text_rect = text_surf.get_rect()
        content_w = text_rect.width + padding * 2
        content_h = text_rect.height + padding * 2
        tile_w, tile_h = parts["c"].get_size()
        total_w = content_w + tile_w * 2
        total_h = content_h + tile_h * 2
        x, y = pos

        tooltip_surf = pygame.Surface((total_w, total_h), pygame.SRCALPHA)

        # Fill
        for i in range(tile_w, total_w - tile_w, tile_w):
            for j in range(tile_h, total_h - tile_h, tile_h):
                tooltip_surf.blit(parts["c"], (i, j))

        # Edges
        for i in range(tile_w, total_w - tile_w, tile_w):
            tooltip_surf.blit(parts["t"], (i, 0))
            tooltip_surf.blit(parts["b"], (i, total_h - tile_h))
        for j in range(tile_h, total_h - tile_h, tile_h):
            tooltip_surf.blit(parts["l"], (0, j))
            tooltip_surf.blit(parts["r"], (total_w - tile_w, j))

        # Corners
        tooltip_surf.blit(parts["tl"], (0, 0))
        tooltip_surf.blit(parts["tr"], (total_w - tile_w, 0))
        tooltip_surf.blit(parts["bl"], (0, total_h - tile_h))
        tooltip_surf.blit(parts["br"], (total_w - tile_w, total_h - tile_h))

        # Text
        tooltip_surf.blit(text_surf, (tile_w + padding, tile_h + padding))

        # Apply fade
        tooltip_surf.set_alpha(alpha)
        surface.blit(tooltip_surf, (x, y))

    def _draw_expanded_box(self, surface, font, text):
        padding = 10
        width = 400
        lines = self._wrap_text(font, text, width - padding * 2)
        height = padding * 2 + len(lines) * font.get_height()
        x = (self.geometry["width"] - width) // 2
        y = self.geometry["height"] - height - 40

        box_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (0, 0, 0), box_rect)
        pygame.draw.rect(surface, (255, 255, 255), box_rect, 2)

        for i, line in enumerate(lines):
            text_surf = font.render(line, True, (255, 255, 255))
            surface.blit(text_surf, (x + padding, y + padding + i * font.get_height()))

    def _wrap_text(self, font, text, max_width):
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = current + (" " if current else "") + word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def _load_tooltip_parts(self):
        load = lambda name: pygame.image.load(os.path.join("assets", "tooltip_small", name)).convert_alpha()
        self.tooltip_parts = {
            "tl": load("top_left.png"),
            "t":  load("top.png"),
            "tr": load("top_right.png"),
            "l":  load("left.png"),
            "c":  load("center.png"),
            "r":  load("right.png"),
            "bl": load("bottom_left.png"),
            "b":  load("bottom.png"),
            "br": load("bottom_right.png"),
        }

    def _load_box_parts(self):
        load = lambda name: pygame.image.load(os.path.join("assets", "box_border_small", name)).convert_alpha()
        self.box_parts = {
            "tl": load("top_left.png"),
            "t":  load("top.png"),
            "tr": load("top_right.png"),
            "l":  load("left.png"),
            "c":  load("center.png"),
            "r":  load("right.png"),
            "bl": load("bottom_left.png"),
            "b":  load("bottom.png"),
            "br": load("bottom_right.png"),
        }

    def _get_smart_tooltip_position(self, mouse_pos, text, font):
        padding = 12
        text_surf = font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect()
        content_w = text_rect.width + padding * 2
        content_h = text_rect.height + padding * 2

        tile_w, tile_h = self.tooltip_parts["c"].get_size()
        total_w = content_w + tile_w * 2
        total_h = content_h + tile_h * 2

        screen_w = self.geometry["width"]
        screen_h = self.geometry["height"]

        x = mouse_pos[0]
        y = mouse_pos[1] - total_h  # default: above mouse

        if x + total_w > screen_w:
            x = screen_w - total_w - 5
        if x < 0:
            x = 5
        if y < 0:
            y = mouse_pos[1] + 20  # flip below mouse if above is off screen
        return x, y

    def _bbox_to_rect(self, bbox):
        xs = [pt[0] for pt in bbox]
        ys = [pt[1] for pt in bbox]
        x, y = min(xs), min(ys)
        w, h = max(xs) - x, max(ys) - y
        return int(x), int(y), int(w), int(h)
