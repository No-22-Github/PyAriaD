import sys
from PyQt6.QtWidgets import QApplication, QWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle("PyAriaD")
        self.resize(900, 450)
        self.center()
        self.show()

    def center(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = self.frameGeometry()

        center_point = screen_geometry.center()

        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
