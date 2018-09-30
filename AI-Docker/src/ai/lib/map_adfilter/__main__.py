import numpy as np

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from medpy.filter.smoothing import anisotropic_diffusion
    from scipy.ndimage.filters import gaussian_filter
    from ai.lib.map_envi import load

    # imt = np.load('tnsr.npy')[3000:4000,4000:5000,0]
    # bdt = np.load('bad_data.npy')[3000:4000,4000:5000]
    # print(imt.min(), imt.max(), imt.mean(), imt.std())

    # im = np.zeros((1000, 1000), dtype=np.float32)
    # bd = np.zeros((1000, 1000), dtype=np.bool)
    # for fn in ('Sigma0_IW1_VH_mst_22Jun2018',
    #            'Sigma0_IW1_VH_slv1_04Jul2018',
    #            'Sigma0_IW1_VV_mst_22Jun2018',
    #            'Sigma0_IW1_VV_slv2_04Jul2018'):
    #     patch, _ = load(fn)
    #     patch = patch[10000:11000,11000:12000].astype(np.float32)
    #     bd |= (patch <= 1e-6) | (patch > 10)
    #     im += patch

    # im *= 0.25
    # im = np.where(bd, 0, np.log10(np.maximum(1e-6, im)) )

    im1 = load('Sigma0_IW1_VV_mst_22Jun2018')[0][7000:13000, 7000:13000].astype(np.float32)
    im2 = load('Sigma0_IW1_VH_mst_22Jun2018')[0][7000:13000, 7000:13000].astype(np.float32)

    im = np.hypot(im1, im2)
    bd = (im <= 1e-6) | (im > 10)

    im = np.arcsin(im2 / im)

    im = np.maximum(1e-6, im)
    imor = im.copy()

    fix_pixels(im, bd)

    u = gaussian_filter(im, 4)
    u = anisotropic_diffusion(im, 50, 20, 0.25, option=1)
    # u = im
    G1 = np.hypot(*np.gradient(im))
    G2 = np.hypot(*np.gradient(u))

    plt.subplot(2, 2, 1), plt.imshow(imor, cmap='gray')
    plt.xticks([]), plt.yticks([])

    plt.subplot(2, 2, 2), plt.imshow(u, cmap='gray')
    plt.xticks([]), plt.yticks([])

    plt.subplot(2, 2, 3), plt.imshow(G1, cmap='gray')
    plt.xticks([]), plt.yticks([])

    plt.subplot(2, 2, 4), plt.imshow(G2, cmap='gray')
    plt.xticks([]), plt.yticks([])

    plt.subplots_adjust(bottom=0., right=1, top=1)

    plt.show()
