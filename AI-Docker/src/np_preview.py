import matplotlib.pyplot as plt
import numpy as np

tnsr = np.load("../test-data/medium/out/prob_pred_full.npy")
plt.imshow(tnsr[..., 0])
plt.show()
