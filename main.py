import datetime
import sys
from PySide2.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton,QVBoxLayout, QDialog, QLabel, QSlider, QLCDNumber, QMessageBox, QSystemTrayIcon, QToolButton, QMenu  
from PySide2.QtCore import *
from PySide2.QtGui import QIcon, QFont

class Form(QDialog):

    def __init__(self, parent=None):
        self.lcd = QLCDNumber(5)
        self.lcd2 = QLCDNumber(5)
        self.clock = QLCDNumber(5)
        super(Form, self).__init__(parent)
        self.setWindowTitle("Pomodoro")
        # Create widgets
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 99)
        self.slider.setValue(25)
        self.slider2 = QSlider(Qt.Horizontal)
        self.slider2.setRange(1, 99)
        self.slider2.setValue(5)
        self.count = self.slider.value() * 60
        self.rest = self.slider2.value() * 60 
        self.taskbar_count = 0
        self.taskbar2_count = 0
        self.text = QLabel("How long should the work period be?")
        self.text2 = QLabel("How long should the rest period be?")
        self.work = QLabel("WORK")
        self.pause = QLabel("REST")
        self.work.setAlignment(Qt.AlignHCenter)
        self.work.setFont(QFont("Times", 18, QFont.Bold))
        self.pause.setAlignment(Qt.AlignHCenter)
        self.pause.setFont(QFont("Times", 18, QFont.Bold))
        self.button = QPushButton("Start timer")
        self.button2 = QPushButton("Stop timer")
        self.lcd.display("25:00")
        self.lcd2.display("05:00")
        mins = 25
        secs = "00"
        self.clock.display(f"{mins}:{secs}")
        self.slider.valueChanged.connect(self.first_display)
        self.slider2.valueChanged.connect(self.second_display)
        self.slider.valueChanged.connect(self.clock_display)
        self.button2.hide()
        self.work.hide()
        self.pause.hide()
        self.clock.hide()
        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.lcd)
        layout.addWidget(self.slider)
        layout.addWidget(self.text2)
        layout.addWidget(self.lcd2)
        layout.addWidget(self.slider2)
        layout.addWidget(self.button)
        layout.addWidget(self.button2)
        layout.addWidget(self.work)
        layout.addWidget(self.pause)
        layout.addWidget(self.clock)
        # Set dialog layout
        self.setLayout(layout)
        self.systemtray_icon = QSystemTrayIcon(QIcon("snake.png"))
        self.systemtray_icon.show()
        self.systemtray_icon.activated.connect(self.icon_activated)
        self.menu = QMenu(parent)
        self.exit_action = self.menu.addAction("Exit")
        self.systemtray_icon.setContextMenu(self.menu)
        self.exit_action.triggered.connect(self.slot_exit)
        # Add signals
        self.slider.valueChanged.connect(self.count_func)
        self.slider2.valueChanged.connect(self.count_func)
        self.button.clicked.connect(self.button_update)
        self.button.clicked.connect(self.timer_func)
        self.button2.clicked.connect(self.stop)
    
    def icon_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show()

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def slot_exit(self):
        QApplication.exit(0)

    def first_display(self):
        minute = str(self.slider.sliderPosition())
        second = ":00"
        leading_zero = "0"
        if self.slider.sliderPosition() >= 10:
            self.lcd.display(minute+second)
        else:
            self.lcd.display(leading_zero + minute + second)

    def second_display(self):
        minute = str(self.slider2.sliderPosition())
        second = ":00"
        leading_zero = "0"
        if self.slider2.sliderPosition() >= 10:
            self.lcd2.display(minute+second)
        else:
            self.lcd2.display(leading_zero + minute + second)

    def clock_display(self):
        minute = str(self.slider.sliderPosition())
        second = ":00"
        leading_zero = "0"
        if self.slider.sliderPosition() >= 10:
            self.clock.display(minute+second)
        else:
            self.clock.display(leading_zero + minute + second)

    def count_func(self):
        self.count = self.slider.sliderPosition() * 60
        self.rest = self.slider2.sliderPosition() * 60

    def countdown(self):
        minute, second = divmod(self.count, 60)
        zero = "0"
        show =  self.work.show()
        if second < 10 and minute < 10:
            self.clock.display(zero + str(minute) + ":" + zero + str(second))
        elif second < 10:
            self.clock.display(str(minute) + ":" + zero + str(second))
        elif minute < 10:
            self.clock.display(zero + str(minute) + ":" + str(second))
        else:
            self.clock.display(str(minute) + ":" + str(second))
        self.count -= 1
        if self.count < -1:
            self.work.hide()
            self.taskbar_rest()
            show =  self.pause.show()
            minute, second = divmod(self.rest, 60)
            zero = "0"
            if self.rest == self.slider2.value() * 60:
                self.show()
            if second < 10 and minute < 10:
                self.clock.display(zero + str(minute) + ":" + zero + str(second))
            elif second < 10:
                self.clock.display(str(minute) + ":" + zero + str(second))
            elif minute < 10:
                self.clock.display(zero + str(minute) + ":" + str(second))
            else:
                self.clock.display(str(minute) + ":" + str(second))
            self.rest -= 1
            if self.rest < -1:
                self.clock.display("00:00")
                self.taskbar_work()
                self.timer.stop()
                self.stop()
        show

    def timer_func(self):
        timer = QTimer()
        self.timer = timer
        self.timer.timeout.connect(self.countdown)
        self.timer.start(1000)

    def button_update(self):
        self.button.hide()
        self.text.hide()
        self.lcd.hide()
        self.slider.hide()
        self.text2.hide()
        self.lcd2.hide()
        self.slider2.hide()
        self.clock.show()
        self.button2.show()
        self.work.show()

    def taskbar_rest(self):
        if self.taskbar_count == 0:
            self.systemtray_icon.showMessage("PAUSE", "Time to rest!", QSystemTrayIcon.Information, 500000)
            self.taskbar_count = 1

    def taskbar_work(self):
        if self.taskbar2_count == 0:
            self.systemtray_icon.showMessage("WORK", "Break over!", QSystemTrayIcon.Information, 500000)
            self.taskbar2_count = 1

    def stop(self):
        self.timer.stop()
        self.button2.hide()
        self.work.hide()
        self.pause.hide()
        self.clock.hide()
        self.count = self.slider.value() * 60
        self.rest = self.slider2.value() * 60
        self.clock.display(str(self.slider.value()) + ":00")                 
        self.button.show()
        self.text.show()
        self.lcd.show()
        self.slider.show()
        self.text2.show()
        self.lcd2.show()
        self.slider2.show()
        self.show()
        self.taskbar_count = 0
        self.taskbar2_count = 0


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    app.setQuitOnLastWindowClosed(False)
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())