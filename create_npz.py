import numpy as np
import os
import colmap_read_model as read_model
from argparse import ArgumentParser
import glob
import cv2

parser = ArgumentParser()
parser.add_argument('--loc', help='Folder containing the input')
parser.add_argument('--scale', default=5, type=int, help='Multiplication factor of the scale matrix')
args = parser.parse_args()


DIR = args.loc
DST_1 = os.path.join(DIR, "cameras.npz")
DST_2 = os.path.join(DIR, "cameras_linear_init.npz")
SCALE = args.scale

IMAGE_ROOT = os.path.join(DIR, 'image')
MASK_ROOT = os.path.join(DIR, 'mask')
mask_paths = glob.glob(os.path.join(MASK_ROOT, '*.png'))
mask_paths.sort()

def intersect(P0, P1):
    n = (P1 - P0) / np.linalg.norm(P1 - P0, axis=1)[:, np.newaxis]
    projs = np.eye(n.shape[1]) - n[:, :, np.newaxis] * n[:, np.newaxis]
    R = projs.sum(axis=0)
    q = (projs @ P0[:, :, np.newaxis]).sum(axis=0)
    p = np.linalg.lstsq(R, q, rcond=None)[0]
    return p


camerasfile = os.path.join(DIR, 'sparse/0/cameras.bin')
camdata = read_model.read_cameras_binary(camerasfile)
list_of_keys = list(camdata.keys())
cam = camdata[list_of_keys[0]]

h, w, f, cx, cy = cam.height, cam.width, cam.params[0], cam.params[1], cam.params[2]
k = np.array([[f, 0, cx],
              [0, f, cy],
              [0, 0, 1]])

imagesfile = os.path.join(DIR, 'sparse/0/images.bin')
imdata = read_model.read_images_binary(imagesfile)
bottom = np.array([0, 0, 0, 1.]).reshape([1, 4])
names = [imdata[k].name for k in imdata]
perm = np.argsort(names)
cameras = {}
cameras_linear_init = {}
for i in perm:
    im = imdata[i+1]
    r = im.qvec2rotmat()
    t = im.tvec.reshape([3, 1])

    dummy = np.eye(4)
    dummy[:3,:3] = k @ r
    dummy[:3,3] = k @ t.reshape([3])

    w2c = np.concatenate([np.concatenate([r, t], 1), bottom], 0)
    c2w = np.linalg.inv(w2c)

    r = c2w[:3, :3]
    r = r.T  
    t = c2w[:3, 3]
    t = -t 

    wm = np.eye(4)
    wm[:3,:3] = k @ r
    wm[:3,3] = k @ r @ t

    cameras[f'world_mat_{i}'] = wm
    cameras_linear_init[f'world_mat_{i}'] = wm

P0 = []
P1 = []
for path in mask_paths:
    file_name = os.path.basename(path)
    img_no = int(os.path.splitext(file_name)[0])
    
    WM4x4 = cameras[f'world_mat_{img_no}']
    WM4x4inv = np.linalg.inv(WM4x4)
    cam_pos = np.matmul(WM4x4inv, np.asarray([0,0,0,1]))
    
    mask = cv2.imread(path)
    mask_points = np.where(mask.max(axis=2) > 0.5)
    xs = mask_points[1]
    ys = mask_points[0]
    x = int(xs.mean())
    y = int(ys.mean())
    ss_pos = np.array([x, y, 1, 1])
    
    pixel_pos = np.matmul(WM4x4inv, ss_pos)

    P0.append(cam_pos[:-1])
    P1.append(pixel_pos[:-1])

P0 = np.asarray(P0)
P1 = np.asarray(P1)

p = intersect(P0, P1)

SM = np.eye(4)
SM[:3] *= SCALE
SM[:3, 3] = p.T[0]

print(SM)


for i in perm:
    cameras[f'scale_mat_{i}'] = SM
    cameras_linear_init[f'scale_mat_{i}'] = SM

np.savez(DST_1, **cameras)
np.savez(DST_2, **cameras_linear_init)