import sys
import glob
import os
import numpy as np
from argparse import ArgumentParser
from PIL import Image

from PyQt5.QtWidgets import (QWidget, QApplication, QHBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit, QMessageBox, QVBoxLayout, QSizePolicy, QSlider)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer

def reorder_images(path):
    fnames = sorted(glob.glob(os.path.join(path, '*.jpg')))
    if len(fnames) == 0:
        fnames = sorted(glob.glob(os.path.join(path, '*.png')))

    for i, old_name in enumerate(fnames):
        if i < 10:
            new_name = os.path.dirname(old_name) + '/00' + str(i) + os.path.splitext(old_name)[1]
        elif i > 9:
            new_name = os.path.dirname(old_name) + '/0' + str(i) + os.path.splitext(old_name)[1]

        os.rename(old_name, new_name)
    

def load_images(path):
    fnames = sorted(glob.glob(os.path.join(path, '*.jpg')))
    if len(fnames) == 0:
        fnames = sorted(glob.glob(os.path.join(path, '*.png')))
    frame_list = []
    for i, fname in enumerate(fnames):
        frame_list.append(np.array(Image.open(fname).convert('RGB'), dtype=np.uint8))
    frames = np.stack(frame_list, axis=0)
    return frames

class App(QWidget):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.images = load_images(f'{self.path}/image')
        self.num_frames, self.height, self.width = self.images.shape[:3]

        self.setWindowTitle('Select Images')
        self.setGeometry(100, 100, self.width, self.height+100)

        # some buttons
        self.play_button = QPushButton('Play')
        self.play_button.clicked.connect(self.on_play)
        self.play_button.setMaximumSize(100,100)
        self.exit_button = QPushButton('Exit')
        self.exit_button.clicked.connect(self.exit)
        self.exit_button.setMaximumSize(100,100)

        # LCD
        self.lcd = QTextEdit()
        self.lcd.setReadOnly(True)
        self.lcd.setMaximumHeight(28)
        self.lcd.setMaximumWidth(120)
        self.lcd.setText('{: 4d} / {: 4d}'.format(0, self.num_frames-1))

        # timeline slider
        self.tl_slider = QSlider(Qt.Horizontal)
        self.tl_slider.valueChanged.connect(self.tl_slide)
        self.tl_slider.setMinimum(0)
        self.tl_slider.setMaximum(self.num_frames-1)
        self.tl_slider.setValue(0)
        self.tl_slider.setTickPosition(QSlider.TicksBelow)
        self.tl_slider.setTickInterval(1)

         # Main canvas -> QLabel
        self.main_canvas = QLabel()
        self.main_canvas.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.main_canvas.setAlignment(Qt.AlignCenter)
        self.main_canvas.setMinimumSize(100, 100)

        mini_label = QLabel('Enter the indices of the images to remove')
        self.textbox = QLineEdit(self)
        self.remove_button = QPushButton('Remove')
        self.remove_button.clicked.connect(self.on_remove)
        self.remove_button.setMaximumSize(100,100)

        # navigator
        navi = QHBoxLayout()
        navi.addWidget(self.lcd)
        navi.addWidget(self.play_button)
        navi.addWidget(mini_label)
        navi.addWidget(self.textbox)
        navi.addWidget(self.remove_button)
        navi.addWidget(self.exit_button)

        draw_area = QHBoxLayout()
        draw_area.addWidget(self.main_canvas)

        '''
        # Minimap area
        minimap_area = QVBoxLayout()
        minimap_area.setAlignment(Qt.AlignCenter)
        mini_label = QLabel('Enter the indices of the images to remove')
        minimap_area.addWidget(mini_label)

        self.textbox = QLineEdit(self)
        minimap_area.addWidget(self.textbox)

        self.remove_button = QPushButton('Remove')
        self.remove_button.clicked.connect(self.on_remove)
        self.remove_button.setMaximumSize(100,100)
        minimap_area.addWidget(self.remove_button)   

        draw_area.addLayout(minimap_area, 1)
        '''

        layout = QVBoxLayout()
        layout.addLayout(draw_area)
        layout.addWidget(self.tl_slider)
        layout.addLayout(navi)
        self.setLayout(layout)

        # timer
        self.timer = QTimer()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.on_time)

        self.cursur = 0
        self.show()

        self.show_current_frame()


    def show_current_frame(self):
        self.update_interact_vis()
        self.lcd.setText('{: 3d} / {: 3d}'.format(self.cursur, self.num_frames-1))
        self.tl_slider.setValue(self.cursur)

    def update_interact_vis(self):
        # Update the interactions without re-computing the overlay
        image = self.images[self.cursur].copy()
        height, width, channel = image.shape
        bytesPerLine = 3 * width

        image = image.astype(np.uint8)

        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.main_canvas.setPixmap(QPixmap(qImg.scaled(self.main_canvas.size(), Qt.KeepAspectRatio, Qt.FastTransformation)))

        self.main_canvas_size = self.main_canvas.size()
        self.image_size = qImg.size()

    def tl_slide(self):
        self.cursur = self.tl_slider.value()
        self.show_current_frame()

    def on_time(self):
        self.cursur += 1
        if self.cursur > self.num_frames-1:
            self.cursur = 0
        self.tl_slider.setValue(self.cursur)

    def on_play(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(1000 / 25)

    def exit(self):
        self.close()

    def on_remove(self):
        remove_list = []
        text = self.textbox.text()

        if text:
            comma_separated = text.split(",")

            for i in comma_separated:
                i = i.replace(" ", "")
                dash_separated = i.split("-")
                if len(dash_separated) == 1:
                    remove_list.append(int(dash_separated[0]))
                else:
                    for j in range(int(dash_separated[0]), int(dash_separated[1])+1):
                        remove_list.append(j)

            remove_list = list(set(remove_list))
            remove_list.sort()

        if len(remove_list) > 0:
            buttonReply = QMessageBox.question(self, 'Confirmation', "The follwing frames will be removed: " + str(remove_list) + ". Confirm?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                for idx in remove_list:
                    if idx < 10:    
                        file_path = f'{self.path}/image/00{idx}.png'
                    else:
                        file_path = f'{self.path}/image/0{idx}.png'
                    if os.path.exists(file_path):
                        os.remove(file_path)

                    if idx < 10:    
                        file_path = f'{self.path}/image/00{idx}.jpg'
                    else:
                        file_path = f'{self.path}/image/0{idx}.jpg'
                    if os.path.exists(file_path):
                        os.remove(file_path)

                reorder_images(f'{self.path}/image')
                self.images = load_images(f'{self.path}/image')
                self.num_frames, self.height, self.width = self.images.shape[:3]
                self.tl_slider.setMinimum(0)
                self.tl_slider.setMaximum(self.num_frames-1)
                self.tl_slider.setValue(0)
                self.cursur = 0
                self.show_current_frame()
                self.textbox.setText("")
                

    def on_undo(self):
        print("Undo")


parser = ArgumentParser()
parser.add_argument('--path')
args = parser.parse_args()

app = QApplication(sys.argv)
ex = App(args.path)
sys.exit(app.exec_())