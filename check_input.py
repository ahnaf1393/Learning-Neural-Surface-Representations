import os
import cv2
import glob
import numpy as np
import math

from argparse import ArgumentParser
import shutil
 
parser = ArgumentParser()
parser.add_argument('--loc', help='Folder containing the input')
parser.add_argument('--number_frames', default=70, type=int, help='If the input is a video, set how many frames should be extracted from it')
args = parser.parse_args()

if os.path.isdir(f'{args.loc}/image'):
    imgs = []
    for ext in ['*.png', '*.jpg', '*.JPEG', '*.JPG']:
        imgs.extend(glob.glob(os.path.join(f'{args.loc}/image/', ext)))
    print(len(imgs))
    if len(imgs) < 1:
        print("There are no images!")
    else:
        print("Images detected")
else:
    video_path = glob.glob(os.path.join(f'{args.loc}/*.mp4'))
    if len(video_path) == 1:
        print("Video detected")
        MAX_FRAMES = args.number_frames

        video = cv2.VideoCapture(video_path[0])
        if video.isOpened() == False : 
            print("Error")

        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f'Total frames: {frame_count}')

        if frame_count > MAX_FRAMES:
            step = math.ceil(frame_count / MAX_FRAMES)
        else:
            step = 1

        step = 1

        print(f'Step: {step}')

        os.makedirs(f'{args.loc}/image')

        count = 0
        written_no = 0
        while video.isOpened():
            ret, frame = video.read()
            if ret == True:
                if count % step == 0:
                    if written_no < 10:
                        cv2.imwrite(f'{args.loc}/image/00{written_no}.png', frame)
                    else:
                        cv2.imwrite(f'{args.loc}/image/0{written_no}.png', frame)
                    written_no += 1
                count += 1
            else:
                break
    else:
        print("No image or video found")