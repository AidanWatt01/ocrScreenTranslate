from PyQt5 import QtCore, QtGui, QtWidgets

class OverlayWindow(QtWidgets.QWidget):
    def __init__(self, text_data, geometry):
        super().__init__()
        self.text_data = text_data
        self.hovered_item = None

        self.setGeometry(
            geometry['left'],
            geometry['top'],
            geometry['width'],
            geometry['height']
        )

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        QtWidgets.QShortcut(QtGui.QKeySequence("Escape"), self).activated.connect(self.close)
        print(f"[Overlay] Initialized — size {geometry['width']}x{geometry['height']} with {len(text_data)} boxes.")

    def paintEvent(self, event):
        try:
            print("[Overlay] paintEvent triggered.")
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2))

            for item in self.text_data:
                rect = self.bbox_to_rect(item['bbox'])
                painter.fillRect(rect, QtGui.QColor(0, 0, 0, 80))
                painter.drawRect(rect)
            print("[Overlay] paintEvent complete.")
        except Exception as e:
            print(f"[Overlay] paintEvent ERROR: {e}")

    def mouseMoveEvent(self, event):
        try:
            print(f"[Overlay] mouseMove at {event.pos()}")
            for item in self.text_data:
                rect = self.bbox_to_rect(item['bbox'])
                if rect.contains(event.pos()):
                    print(f"[Overlay] Hovered on: {item.get('text', '[unknown]')}")
                    # Temporarily disable tooltip to isolate crash
                    # tip = item.get("translation") or "[no translation]"
                    # QtWidgets.QToolTip.showText(event.globalPos(), tip)
                    return
            # QtWidgets.QToolTip.hideText()
        except Exception as e:
            print(f"[Overlay] mouseMoveEvent ERROR: {e}")

    def mousePressEvent(self, event):
        try:
            print(f"[Overlay] mousePress at {event.pos()}")
            for item in self.text_data:
                rect = self.bbox_to_rect(item['bbox'])
                if rect.contains(event.pos()):
                    print(f"[Overlay] Clicked: {item.get('text')}")
                    self.show_translation_popup(item)
                    return
        except Exception as e:
            print(f"[Overlay] mousePressEvent ERROR: {e}")

    def show_translation_popup(self, item):
        try:
            print(f"[Popup] Opening for: {item.get('text')}")
            jp_text = item.get("text", "") or "[no text]"
            en_text = item.get("translation", "") or "[no translation]"

            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Translation")
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(QtWidgets.QLabel(f"<b>Japanese:</b> {jp_text}"))
            layout.addWidget(QtWidgets.QLabel(f"<b>English:</b> {en_text}"))
            dialog.setLayout(layout)
            dialog.setFixedSize(400, 150)
            dialog.move(QtGui.QCursor.pos())
            dialog.exec_()
        except Exception as e:
            print(f"[Popup] ERROR: {e}")

    def keyPressEvent(self, event):
        print(f"[Overlay] keyPress: {event.key()}")
        if event.key() == QtCore.Qt.Key_Escape:
            print("[Overlay] Closing on ESC")
            self.close()

    def bbox_to_rect(self, bbox):
        try:
            xs = [pt[0] for pt in bbox]
            ys = [pt[1] for pt in bbox]
            x, y = min(xs), min(ys)
            w, h = max(xs) - x, max(ys) - y
            return QtCore.QRect(int(x), int(y), int(w), int(h))
        except Exception as e:
            print(f"[Overlay] bbox_to_rect ERROR: {e}")
            return QtCore.QRect(0, 0, 0, 0)
