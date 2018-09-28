#!/usr/bin/env python3.7
import logging
import os
from pickle import dump, load

import numpy as np
from scipy.ndimage.filters import gaussian_filter
from sklearn.cluster import MiniBatchKMeans
from sklearn.mixture import GaussianMixture as GM
from sklearn.utils import shuffle

# todo Assemble has zone|full|both while this filr only zone|full
from ai.recipe import Recipe


class Process(object):
    log = logging.getLogger('Process')

    def __init__(self, mode, prediction_type, recipe: Recipe):
        """

        :type prediction_type: str
        :type mode: str
        """
        self.mode = mode
        self.type = prediction_type
        self.recipe = recipe
        self.WORKDIR = self.recipe.get("OUTDIR")

    def run(self):
        if self.type not in ('fit', 'predict', 'fitpredict'):
            self.log.error("Bad mode '%s'. Allowed  [fit|predict|fitpredict]", self.mode)
            return -1

        if self.mode not in ('zone', 'full'):
            self.log.error("Bad mode '%s'. Allowed  [zone|full]", self.mode)
            return -1

        if self.mode == 'zone':
            tnsr = np.load(self.WORKDIR + 'tnsr_zone.npy')
            bad_data = np.load(self.WORKDIR + 'bd_zone.npy')
        else:
            tnsr = np.load(self.WORKDIR + 'tnsr_full.npy')
            bad_data = np.load(self.WORKDIR + 'bd_full.npy')

        cselect = tuple(self.recipe['learn_channels'])

        tnsr = tnsr[..., cselect]
        self.log.debug({'tnsr.shape': tnsr.shape})
        ts = tnsr.shape

        if self.type == 'fitpredict' or self.type == 'fit':
            gauss_sz = self.recipe['learn_gauss']
            if self.type == 'fitpredict':
                tnsr_or = tnsr.copy()
            tnorm = np.empty((tnsr.shape[-1], 2))
            for n in range(tnsr.shape[-1]):
                tnorm[n, 0] = tnsr[..., n].mean()
                tnsr[..., n] -= tnorm[n, 0]
                tnorm[n, 1] = tnsr[..., n].std()
                tnsr[..., n] /= tnorm[n, 1]
                # tnsr[bad_data,n] = tnorm[n,0]
                if gauss_sz:
                    tnsr[..., n] = gaussian_filter(tnsr[..., n], gauss_sz)

            tnsr_learn = tnsr[~bad_data, :].reshape((-1, tnsr.shape[-1]))
            # tnsr_learn = tnsr.reshape((-1, tnsr.shape[-1]))
            self.log.debug({'tnsr_learn.shape': tnsr_learn.shape})
            tnsr_learn = shuffle(tnsr_learn)

            predictor = MiniBatchKMeans(n_clusters=7, batch_size=1000000, compute_labels=False).fit(tnsr_learn)

            dump(predictor, open(self.WORKDIR + 'predictor.pkl', 'wb'))
            np.save(self.WORKDIR + 'tnorm.npy', tnorm)

            cc = np.array(predictor.cluster_centers_)
            self.log.debug(cc)
            gm = GM(cc.shape[0], max_iter=10, means_init=cc, tol=0.01)
            gm.fit(shuffle(tnsr_learn)[:(4000000 if self.mode == 'full' else 2000000)])
            self.log.debug('gm')
            dump(gm, open(self.WORKDIR + 'gm.pkl', 'wb'))
            # system("say 'learning done'")
            if self.type == 'fitpredict':
                tnsr = tnsr_or
            else:
                return 0

        tnorm = np.load(self.WORKDIR + 'tnorm.npy')
        # predictor = load(open(DATADIR+'predictor.pkl','rb'))
        gm = load(open(self.WORKDIR + 'gm.pkl', 'rb'))
        Ncc = len(gm.weights_)
        prob_pred = np.empty(tnsr.shape[:-1] + (Ncc,), dtype=np.float32)

        gauss_sz = self.recipe['predict_gauss']
        ns = 100
        d = 6
        for i in range(0, tnsr.shape[0], ns):
            self.log.debug('iteration[%d]', i)
            d1 = min(d, i)
            d2 = max(0, min(tnsr.shape[0] - i - ns, d))
            tstr = tnsr[i - d1:i + ns + d2, :, :].copy()
            bdstr = bad_data[i - d1:i + ns + d2, :]

            strshape = tstr.shape
            tstr -= tnorm[np.newaxis, np.newaxis, :, 0]
            tstr /= tnorm[np.newaxis, np.newaxis, :, 1]
            # tstr[bdstr, :] = tnorm[:,0]
            if gauss_sz:
                for n in range(tstr.shape[-1]):
                    tstr[..., n] = gaussian_filter(tstr[..., n], gauss_sz)

            ppstr = gm.predict_proba(tstr.reshape((-1, strshape[-1])))
            ppstr = ppstr.astype(np.float32).reshape(strshape[:-1] + (Ncc,))
            # prob_pred[i:i+ns,...] = ppstr
            ppstr = np.where(bdstr[..., np.newaxis], 0, ppstr)
            if d2 == 0:
                prob_pred[i:i + ns, ...] = ppstr[d1:, ...]
            else:
                prob_pred[i:i + ns, ...] = ppstr[d1:-d2, ...]
        if not os.path.exists(self.WORKDIR):
            os.makedirs(self.WORKDIR)

        if self.mode == 'zone':
            fname = self.WORKDIR + 'prob_pred_zone.npy'
        else:
            fname = self.WORKDIR + 'prob_pred_full.npy'
        np.save(fname, prob_pred)
        self.log.info("Process results saved as '%s'", fname)

        return 0  # all good
