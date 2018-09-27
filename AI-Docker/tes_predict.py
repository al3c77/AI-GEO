import numpy as np
import matplotlib.pyplot as plt
tnsr = np.load('./out/bd_full.npy')
# tnsr = np.load('./out/prob_pred_zone.npy')
# tnsr = np.load('./out/prob_pred_full.npy')
# tnsr = np.load('./out/tnsr_full.npy')
plt.imshow(tnsr[...,3])
plt.show()