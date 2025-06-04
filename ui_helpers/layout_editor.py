import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QVBoxLayout, QWidget, QPushButton,
    QHBoxLayout, QGraphicsTextItem, QGraphicsProxyWidget
)
from PySide6.QtGui import QBrush, QColor, QPainter, QCursor
from PySide6.QtCore import QRectF, Qt, QPointF, Signal

ESCALA = 0.2
HANDLE_SIZE = 10


class WindowBlock(QGraphicsRectItem):
    def __init__(self, x, y, w, h, label, block_type, screen_geometries):
        super().__init__(x * ESCALA, y * ESCALA, w * ESCALA, h * ESCALA)
        self.name = label
        self.block_type = block_type
        self.screen_geometries = screen_geometries

        self.setBrush(QBrush(QColor(100, 200, 250)))
        self.setFlags(
            QGraphicsRectItem.ItemIsMovable |
            QGraphicsRectItem.ItemIsSelectable |
            QGraphicsRectItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.resizing = False

        self.text = QGraphicsTextItem(label, self)
        self.text.setDefaultTextColor(QColor(0, 0, 0))
        self.update_text_position()

        if self.block_type == "backglass":
            self.add_fullscreen_button()

    def update_text_position(self):
        text_rect = self.text.boundingRect()
        rect = self.rect()
        x = rect.width() / 2 - text_rect.width() / 2
        y = rect.height() / 2 - text_rect.height() / 2
        self.text.setPos(rect.x() + x, rect.y() + y)

    def add_fullscreen_button(self):
        self.button = QPushButton("⛶")
        self.button.setFixedSize(20, 20)
        self.button.setStyleSheet("background-color: white;")
        self.button.clicked.connect(self.make_fullscreen)

        self.button_proxy = QGraphicsProxyWidget(self)
        self.button_proxy.setWidget(self.button)
        self.update_button_position()

    def update_button_position(self):
        rect = self.rect()
        self.button_proxy.setPos(rect.right() - 22, rect.top() + 2)

    def make_fullscreen(self):
        x = self.scenePos().x() / ESCALA
        y = self.scenePos().y() / ESCALA
        w = self.rect().width() / ESCALA
        h = self.rect().height() / ESCALA
        center = QPointF(x + w / 2, y + h / 2)

        for geo in self.screen_geometries:
            if geo.contains(center.toPoint()):
                self.setRect(0, 0, geo.width() * ESCALA, geo.height() * ESCALA)
                self.setPos(geo.x() * ESCALA, geo.y() * ESCALA)
                self.update_text_position()
                self.update_button_position()
                break

    def hoverMoveEvent(self, event):
        if self.block_type == "backglass" and self.button_proxy:
            self.update_button_position()

        pos = event.pos()
        rect = self.rect()
        if self.is_in_resize_area(pos, rect):
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
        super().hoverMoveEvent(event)

    def is_in_resize_area(self, pos, rect):
        return (rect.right() - HANDLE_SIZE <= pos.x() <= rect.right() and
                rect.bottom() - HANDLE_SIZE <= pos.y() <= rect.bottom())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_in_resize_area(event.pos(), self.rect()):
            self.resizing = True
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            new_pos = event.pos()
            new_rect = QRectF(self.rect().topLeft(), new_pos)
            if new_rect.width() > HANDLE_SIZE and new_rect.height() > HANDLE_SIZE:
                self.setRect(new_rect)
                self.update_text_position()
                if self.block_type == "backglass":
                    self.update_button_position()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        super().mouseReleaseEvent(event)


class MonitorCanvas(QGraphicsScene):
    def __init__(self, screens, mode):
        super().__init__()
        self.setBackgroundBrush(QBrush(Qt.lightGray))
        self.blocks = []
        self.screens = screens
        self.screen_geometries = [s.geometry() for s in screens]
        self.mode = mode
        self.counts = {}

        if mode == "screens":
            self.available_blocks = ["pinmame", "backglass", "b2sdmd"]
        elif mode == "pup":
            self.available_blocks = ["PUPFullDMD", "PUPPlayfield", "PUPDMD", "PUPBackglass", "PUPTopper"]

        for block_type in self.available_blocks:
            self.counts[block_type] = 1

        for screen in screens:
            geo = screen.geometry()
            rect = QRectF(geo.x() * ESCALA, geo.y() * ESCALA,
                          geo.width() * ESCALA, geo.height() * ESCALA)
            self.addRect(rect).setBrush(QBrush(QColor(200, 200, 200)))

    def add_window_block(self, block_type):
        name = f"{block_type} {self.counts[block_type]}"
        self.counts[block_type] += 1
        x = 100 + self.counts[block_type]*20
        y = 100 + self.counts[block_type]*20
        block = WindowBlock(x, y, 340, 250, name, block_type, self.screen_geometries)
        self.addItem(block)
        self.blocks.append(block)

    def get_positions_dict(self):
        result = {}

        for block in self.blocks:
            x = int(block.scenePos().x() / ESCALA)
            y = int(block.scenePos().y() / ESCALA)
            w = int(block.rect().width() / ESCALA)
            h = int(block.rect().height() / ESCALA)

            if self.mode == "screens":
                if block.block_type == "pinmame":
                    result["PinMAMEWindow"] = "1"
                    result["PinMAMEWindowX"] = str(x)
                    result["PinMAMEWindowY"] = str(y)
                    result["PinMAMEWindowWidth"] = str(w)
                    result["PinMAMEWindowHeight"] = str(h)
                elif block.block_type == "backglass":
                    result["B2SWindows"] = "1"
                    result["B2SBackglassX"] = str(x)
                    result["B2SBackglassY"] = str(y)
                    result["B2SBackglassWidth"] = str(w)
                    result["B2SBackglassHeight"] = str(h)
                elif block.block_type == "b2sdmd":
                    result["B2SDMDX"] = str(x)
                    result["B2SDMDY"] = str(y)
                    result["B2SDMDWidth"] = str(w)
                    result["B2SDMDHeight"] = str(h)

            elif self.mode == "pup":
                prefix = block.block_type
                result[f"{prefix}Screen"] = "1"
                result[f"{prefix}Window"] = "1"
                result[f"{prefix}WindowX"] = str(x)
                result[f"{prefix}WindowY"] = str(y)
                result[f"{prefix}WindowWidth"] = str(w)
                result[f"{prefix}WindowHeight"] = str(h)
                result[f"{prefix}WindowRotation"] = "0"

        return result


class LayoutEditorWindow(QMainWindow):
    positionsSaved = Signal(dict)

    def __init__(self, screens, mode="screens", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"VPX Layout Setup - {mode.capitalize()}")
        self.setMinimumSize(1000, 700)
        self.mode = mode

        self.canvas = MonitorCanvas(screens, mode)
        self.view = QGraphicsView(self.canvas)
        self.view.setRenderHints(QPainter.Antialiasing)

        # Buttons
        self.btn_save = QPushButton("Save Positions")
        self.btn_save.clicked.connect(self.on_save_clicked)

        h_layout = QHBoxLayout()

        for block in self.canvas.available_blocks:
            btn = QPushButton(f"Add {block}")
            btn.clicked.connect(lambda _, b=block: self.canvas.add_window_block(b))
            h_layout.addWidget(btn)

        h_layout.addStretch()
        h_layout.addWidget(self.btn_save)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addLayout(h_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_save_clicked(self):
        data = self.canvas.get_positions_dict()
        print("Positions saved:", data)
        self.positionsSaved.emit(data)
        self.close()


def main():
    app = QApplication(sys.argv)
    screens = app.screens()
    window = LayoutEditorWindow(screens, mode="pup")  # or "screens"
    window.positionsSaved.connect(lambda data: print("Received positions:", data))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
