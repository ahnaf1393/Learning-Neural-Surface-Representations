import os
import cv2
import glob
import numpy as np
from skimage.measure import label
from argparse import ArgumentParser
import shutil
 
parser = ArgumentParser()
parser.add_argument('--loc', help='Folder containing the input')
args = parser.parse_args()

INPUT = args.loc +  '/mask/*.png'
OUTPUT = args.loc +  '/mask_new'

height, width, _ = cv2.imread(glob.glob(args.loc +  '/image/*.png')[0]).shape

os.makedirs(OUTPUT)
paths = glob.glob(INPUT)

def getLargestCC(segmentation):
    labels = label(segmentation)
    unique, counts = np.unique(labels, return_counts=True)
    list_seg=list(zip(unique, counts))[1:] # the 0 label is by default background so take the rest
    largest=max(list_seg, key=lambda x:x[1])[0]
    labels_max=(labels == largest).astype(int)
    return labels_max

for path in paths:
    originalImage = cv2.imread(path)
    originalImage = cv2.resize(originalImage, dsize=(width, height), interpolation=cv2.INTER_CUBIC)
    grayImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)
    (thresh, img_bw ) = cv2.threshold(grayImage, 10, 255, cv2.THRESH_BINARY)

    labels = getLargestCC(img_bw)
    labels = np.where(labels == 1, 255, 0)

    img2 = np.zeros( ( labels.shape[0], labels.shape[1], 3 ) )
    img2[:,:,0] = labels 
    img2[:,:,1] = labels
    img2[:,:,2] = labels

    file_name = os.path.basename(path)
    p_1 = int(os.path.splitext(file_name)[0])
    p_2 = os.path.splitext(file_name)[1]
    if p_1 < 10:
        file_name = f'00{p_1}' + p_2
    else:
        file_name = f'0{p_1}' + p_2
    cv2.imwrite(OUTPUT + '/' + file_name, img2)

shutil.rmtree (args.loc +  '/mask')
os.rename(args.loc +  '/mask_new', args.loc +  '/mask')