import numpy as np
from scipy.spatial.transform import Rotation as R

gt = np.load('./cameras.npz')
noisy = np.load('./cameras_linear_init.npz')
colmap = np.load('./colmap.npz')

# Set intrinsics
K = np.eye(3)
K[0, 0] = 2892.843725329502400
K[1, 1] = 2882.249450476587300
K[0, 2] = 824.425157504919530
K[1, 2] = 605.187152104484080
K_inv = np.linalg.inv(K)

all_qs = []
all_ts = []

bottom = np.array([0, 0, 0, 1.]).reshape([1, 4])
for i in range(49):
    wm = colmap[f'world_mat_{i}'][:3, :]
    w2c = K_inv @ wm
    w2c = np.concatenate([w2c, bottom], 0)
    c2w = np.linalg.inv(w2c)

    all_qs.append(R.as_quat(R.from_matrix(c2w[:3, :3])))
    all_ts.append(c2w[:3, 3])

times = np.arange(49).reshape((49,1))
all_qs = np.asarray(all_qs)
all_ts = np.asarray(all_ts)

print(times.shape)
print(all_qs.shape)
print(all_ts.shape)

csv = np.concatenate((times, all_ts, all_qs), axis=1)

np.savetxt("colmap.csv", csv, delimiter=",")