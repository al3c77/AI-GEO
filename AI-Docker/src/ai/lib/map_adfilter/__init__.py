import numpy as np


def fix_pixels(image, bad_pixels):
    bad_indices = np.nonzero(bad_pixels)
    mean = np.zeros(bad_indices[0].size, dtype=np.float32)
    mean_good = np.zeros(bad_indices[0].size, dtype=np.float32)
    norm = np.zeros(bad_indices[0].size, dtype=np.int32)
    shifts = ((-1, -1),
              (-1, 0),
              (-1, 1),
              (0, 1),
              (1, 1),
              (1, 0),
              (1, -1),
              (0, -1))

    for di, dj in shifts:
        I = np.clip(bad_indices[0] + di, 0, image.shape[0] - 1)
        J = np.clip(bad_indices[1] + dj, 0, image.shape[1] - 1)
        px = image[I, J]
        bmask = bad_pixels[I, J]
        mean += px
        mean_good += np.where(bmask, 0, px)
        norm += (~bmask).astype(np.int32)
    mean /= len(shifts)
    mean_good /= np.maximum(1, norm)
    image[bad_indices[0], bad_indices[1]] = np.where(norm <= len(shifts) / 2, mean, mean_good)
