import sys
import time
import numpy as np
from collections import deque

# Dependencies: PyQt5, pyqtgraph, keyboard
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import keyboard  # pip install keyboard

class SOCDDetectorZX:
    def __init__(self, conflict_threshold=0.3, window_size=200):
        # conflict_threshold: proportion of recent frames with simultaneous presses to trigger ban
        self.conflict_threshold = conflict_threshold
        self.conf_window = deque(maxlen=window_size)
        self.direction = 0  # -1 for Z, +1 for X, 0 neutral

    def update(self):
        now = time.time()
        z = keyboard.is_pressed('z')
        x = keyboard.is_pressed('x')

        # Determine immediate direction
        if z and not x:
            self.direction = -1
        elif x and not z:
            self.direction = 1
        else:
            self.direction = 0

        # Record conflict state and compute rate
        conflict = z and x
        self.conf_window.append(1 if conflict else 0)
        rate = sum(self.conf_window) / len(self.conf_window)

        # Trigger SOCd ban only if conflict is sustained beyond threshold
        if rate > self.conflict_threshold:
            return True
        return False

class BanWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, flags=QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet('background-color: red;')
        self.setWindowTitle("SOCD BAN")
        self.init_ui()
        self.grabKeyboard()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel('SOCD VIOLATION - BANNED')
        label.setFont(QtGui.QFont('Arial', 48))
        label.setStyleSheet('color: white;')
        label.setAlignment(QtCore.Qt.AlignCenter)
        info = QtWidgets.QLabel('Press ESC to exit.')
        info.setFont(QtGui.QFont('Arial', 24))
        info.setStyleSheet('color: white;')
        info.setAlignment(QtCore.Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(label)
        layout.addWidget(info)
        layout.addStretch()
        self.setLayout(layout)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            QtWidgets.qApp.quit()

class SOCDApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SOCD Detector (Z/X)')
        self.resize(800, 600)

        # Initialize detector and state
        self.detector = SOCDDetectorZX()
        self.ban_shown = False

        # UI setup
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # Direction label
        self.dir_label = QtWidgets.QLabel('Neutral')
        self.dir_label.setFont(QtGui.QFont('Consolas', 24))
        self.dir_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.dir_label)

        # Graphs
        self.plot_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.plot_widget, stretch=1)
        self.conf_plot = self.plot_widget.addPlot(title='Conflict Rate')
        self.conf_curve = self.conf_plot.plot(pen=pg.mkPen('r', width=2))
        self.conf_history = deque([0]*200, maxlen=200)

        # Timer for updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._on_update)
        self.timer.start(50)

    def _on_update(self):
        if self.ban_shown:
            return

        socd = self.detector.update()
        if socd:
            self._show_ban()
            return

        # Update direction label
        dir_map = {-1: 'Z', 0: 'Neutral', 1: 'X'}
        self.dir_label.setText(dir_map[self.detector.direction])

        # Update conflict plot
        rate = sum(self.detector.conf_window) / len(self.detector.conf_window)
        self.conf_history.append(rate)
        self.conf_curve.setData(list(self.conf_history))

    def _show_ban(self):
        self.ban_shown = True
        self.timer.stop()
        self.ban_window = BanWindow(self)
        self.ban_window.showFullScreen()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SOCDApp()
    window.show()
    sys.exit(app.exec_())