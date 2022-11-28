import cv2
import numpy as np
import math

INPUT_PATH = 'demo.mp4'
MAX_FRAMES = 50

video = cv2.VideoCapture(INPUT_PATH)
if video.isOpened() == False : 
    print("Error")

frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

if frame_count > MAX_FRAMES:
    step = math.ceil(frame_count / MAX_FRAMES)
else:
    step = 1

count = 0
written_no = 0
while video.isOpened():
    ret, frame = video.read()
    if ret == True:
        if count % step == 0:
            if written_no < 10:
                cv2.imwrite(f'./images/00{written_no}.png', frame)
            else:
                cv2.imwrite(f'./images/0{written_no}.png', frame)
            written_no += 1
        count += 1
    else:
        break