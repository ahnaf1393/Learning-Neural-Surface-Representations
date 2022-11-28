from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog
import sys
import subprocess

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(500, 500, 400, 300)
        self.setWindowTitle("Prototype")
        self.initUI()

    def initUI(self):
        self.label = QLabel(self)
        self.label.setText("Press Start")
        self.label.move(175, 100)

        self.b1 = QPushButton(self)
        self.b1.setText("Start")
        self.b1.move(160, 50)
        self.b1.clicked.connect(self.clicked)

    def clicked(self):
        self.label.setText("Computing..")
        folder_path = str(QFileDialog.getExistingDirectory(self, "Select Input Directory"))
        process = subprocess.Popen(['./run.sh', folder_path])
        process.wait()
        self.label.setText("Done!")
        

def window():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

window()