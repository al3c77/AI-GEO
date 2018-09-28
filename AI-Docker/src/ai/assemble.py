import logging
import sys

sys.path.insert(0, "./")
import os

import numpy as np
from medpy.filter.smoothing import anisotropic_diffusion
from scipy.ndimage.filters import gaussian_filter

from ai.lib.map_adfilter import fix_pixels

# todo pass recipe as JSON object
from ai.lib.Envi import Envi


class Assemble(object):
    # recipe = None  # type: Dict
    log = logging.getLogger('tensor-assembler')

    def __init__(self, mode, recipe, envi):
        """

        :type mode: str
        :type envi: Envi
        :type recipe: Recipe
        """
        self.envi = envi
        self.mode = mode
        self.recipe = recipe
        self.envi.DATADIR = self.recipe.get("DATADIR")
        self.WORKDIR = self.recipe.get("OUTDIR")

    def run(self):
        mode = self.mode
        if mode not in ('zone', 'both', 'full'):
            self.log.error("Unlnowm mode '%s' . Allowed: [zone|full|both]", mode)
            return -1
        recipe = self.recipe
        # self.log.debug(recipe)
        zone = np.array(recipe.get('zone'))
        products = recipe['products']

        if mode in ('zone', 'both') and zone is None:
            self.log.error('No zone info in recipe')
            return -1

        sigma_avg_names = recipe['channels'].get('sigma_avg', [])
        sigma_names = recipe['channels'].get('sigma', [])
        sigma_vv_names = recipe['channels'].get('sigmaVV', [])
        sigma_vh_names = recipe['channels'].get('sigmaVH', [])

        coh_avg_names = recipe['channels'].get('coh_avg', [])
        coh_names = recipe['channels'].get('coh', [])
        coh_vv_names = recipe['channels'].get('cohVV', [])
        coh_vh_names = recipe['channels'].get('cohVH', [])

        channel_names = sigma_names + sigma_avg_names + sigma_vv_names + sigma_vh_names + coh_names + coh_avg_names + coh_vv_names + coh_vh_names

        full_shape, _ = self.envi.read_header(channel_names[0])
        self.log.info({'full shape:': full_shape})

        # zone = [[0, 0], [full_shape[0], full_shape[1]]]

        if zone is not None:
            zone_shape = (zone[1][0] - zone[0][0], zone[1][1] - zone[0][1])
            self.log.info({'Zone': zone, 'Shape': full_shape})

        nproducts = ((len(sigma_names) if 'sigma' in products else 0) +
                     (1 if 'sigma_avg' in products else 0) +
                     (len(sigma_vv_names) if 'sigma_hypot' in products else 0) +
                     (len(sigma_vv_names) if 'sigma_pol' in products else 0) +
                     (len(coh_names) if 'coh' in products else 0) +
                     (1 if 'coh_avg' in products else 0) +
                     (len(coh_vv_names) if 'coh_hypot' in products else 0) +
                     (len(coh_vv_names) if 'coh_pol' in products else 0)
                     )

        if mode in ('zone', 'both'):
            tnsr_zone = np.empty((zone_shape[0], zone_shape[1], nproducts), dtype=np.float32)
            bd_zone = np.zeros((zone_shape[0], zone_shape[1]), dtype=np.bool)
        if mode in ('full', 'both'):
            tnsr_full = np.empty((full_shape[0], full_shape[1], nproducts), dtype=np.float32)
            bd_full = np.zeros((full_shape[0], full_shape[1]), dtype=np.bool)

        product_index = 0

        if ('sigma' in products):
            params = products['sigma']
            for sn in sigma_names:
                self.log.debug('sigma %s', sn)
                s = self.envi.load(sn)[0]

                if mode == 'zone':
                    s = s[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]

                bad_data = (s < 1e-6) | (s > 10) | (s < 1e-6) | (s > 10)
                s = np.clip(s, 1e-6, 10)
                s = np.log10(s)
                fix_pixels(s, bad_data)
                s = anisotropic_diffusion(s, params[0], params[1], 0.2, option=1)

                if mode == 'zone':
                    tnsr_zone[..., product_index] = s
                    product_index += 1
                    bd_zone |= bad_data
                elif mode == 'full':
                    tnsr_full[..., product_index] = s
                    product_index += 1
                    bd_full |= bad_data
                elif mode == 'both':
                    tnsr_full[..., product_index] = s
                    tnsr_zone[..., product_index] = s[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]
                    product_index += 1
                    bd_full |= bad_data
                    bd_zone |= bad_data[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]

        if ('sigma_avg' in products):
            params = products['sigma_avg']
            if mode in ('zone', 'both'):
                savg_zone = np.zeros(zone_shape, dtype=np.float32)
            if mode in ('full', 'both'):
                savg_full = np.zeros(full_shape, dtype=np.float32)

            for sn in sigma_avg_names:
                self.log.debug("sigma_avg %s", sn)
                s = self.envi.load(sn)[0]

                if mode == 'zone':
                    s = s[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]

                bad_data = (s < 1e-6) | (s > 10) | (s < 1e-6) | (s > 10)
                s = np.clip(s, 1e-6, 10)
                s = np.log10(s)
                fix_pixels(s, bad_data)

                if mode == 'zone':
                    savg_zone += s
                    bd_zone |= bad_data
                elif mode == 'full':
                    savg_full += s
                    bd_full |= bad_data
                elif mode == 'both':
                    savg_full += s
                    savg_zone += s[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]
                    bd_full |= bad_data
                    bd_zone |= bad_data[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]

            if mode in ('zone', 'both'):
                tnsr_zone[..., product_index] = anisotropic_diffusion(savg_zone / len(sigma_avg_names), params[0],
                                                                      params[1], 0.2, option=1)
            if mode in ('full', 'both'):
                tnsr_full[..., product_index] = anisotropic_diffusion(savg_full / len(sigma_avg_names), params[0],
                                                                      params[1], 0.2, option=1)
            product_index += 1

        if ('sigma_hypot' in products) or ('sigma_pol' in products):
            if 'sigma_hypot' in products:
                params = products['sigma_hypot']
            else:
                params = products['sigma_pol']

            for svvn, svhn in zip(sigma_vv_names, sigma_vh_names):
                self.log.debug({'svvn': svvn, 'svhn': svhn})
                svv = self.envi.load(svvn)[0]
                svh = self.envi.load(svhn)[0]

                if mode == 'zone':
                    svv = svv[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]
                    svh = svh[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]

                bad_data = (svv < 1e-6) | (svv > 10) | (svh < 1e-6) | (svh > 10)
                svh = np.clip(svh, 1e-6, 10)
                sv = np.clip(np.hypot(svv, svh), 1e-6, 10)

                svpol = None
                if 'sigma_pol' in products:
                    svpol = np.arcsin(svh / sv)
                    fix_pixels(svpol, bad_data)
                    svpol = gaussian_filter(svpol, params[2])
                    svpol = anisotropic_diffusion(svpol, params[3], params[4], 0.2, option=1)
                svv = None
                svh = None

                sv = np.log10(sv)
                fix_pixels(sv, bad_data)
                sv = anisotropic_diffusion(sv, params[0], params[1], 0.2, option=1)

                if mode == 'zone':
                    if 'sigma_hypot' in products:
                        tnsr_zone[..., product_index] = sv
                        product_index += 1
                    if 'sigma_pol' in products:
                        tnsr_zone[..., product_index] = svpol
                        product_index += 1
                    bd_zone |= bad_data
                elif mode == 'full':
                    if 'sigma_hypot' in products:
                        tnsr_full[..., product_index] = sv
                        product_index += 1
                    if 'sigma_pol' in products:
                        tnsr_full[..., product_index] = svpol
                        product_index += 1
                    bd_full |= bad_data
                elif mode == 'both':
                    if 'sigma_hypot' in products:
                        tnsr_full[..., product_index] = sv
                        tnsr_zone[..., product_index] = sv[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]
                        product_index += 1
                    if 'sigma_pol' in products:
                        tnsr_full[..., product_index] = svpol
                        tnsr_zone[..., product_index] = svpol[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]
                        product_index += 1
                    bd_full |= bad_data
                    bd_zone |= bad_data[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]

        if ('coh' in products):
            params = products['coh']
            for cn in coh_names:
                self.log.debug('coh %s', cn)
                c = self.envi.load(cn)[0]

                if mode == 'zone':
                    c = c[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]

                bad_data = (c < 0) | (c > 1) | (c < 0) | (c > 1)
                c = np.clip(c, 0, 1)

                fix_pixels(c, bad_data)
                c = anisotropic_diffusion(c, params[0], params[1], 0.2, option=1)

                if mode == 'zone':
                    tnsr_zone[..., product_index] = c
                    product_index += 1
                    bd_zone |= bad_data
                elif mode == 'full':
                    tnsr_full[..., product_index] = c
                    product_index += 1
                    bd_full |= bad_data
                elif mode == 'both':
                    tnsr_full[..., product_index] = c
                    tnsr_zone[..., product_index] = c[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]
                    product_index += 1
                    bd_full |= bad_data
                    bd_zone |= bad_data[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]

        if ('coh_avg' in products):
            if mode in ('zone', 'both'):
                cavg_zone = np.zeros(zone_shape, dtype=np.float32)
            if mode in ('full', 'both'):
                cavg_full = np.zeros(full_shape, dtype=np.float32)
            params = products['coh_avg']

            for cn in coh_avg_names:
                self.log.debug("coh_avg %s", cn)
                c = self.envi.load(cn)[0]

                if mode == 'zone':
                    c = c[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]

                bad_data = (c < 0) | (c > 1) | (c < 0) | (c > 1)
                c = np.clip(c, 0, 1)

                fix_pixels(c, bad_data)

                if mode == 'zone':
                    cavg_zone += c
                    bd_zone |= bad_data
                elif mode == 'full':
                    cavg_full += c
                    bd_full |= bad_data
                elif mode == 'both':
                    cavg_full += c
                    cavg_zone += c[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]
                    bd_full |= bad_data
                    bd_zone |= bad_data[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]

            if mode in ('zone', 'both'):
                tnsr_zone[..., product_index] = anisotropic_diffusion(cavg_zone / len(coh_avg_names), params[0],
                                                                      params[1], 0.2, option=1)
            if mode in ('full', 'both'):
                tnsr_full[..., product_index] = anisotropic_diffusion(cavg_full / len(coh_avg_names), params[0],
                                                                      params[1], 0.2, option=1)
            product_index += 1

        if ('coh_hypot' in products) or ('coh_pol' in products):
            if 'coh_hypot' in products:
                params = products['coh_hypot']
            else:
                params = products['coh_pol']

            for cvvn, cvhn in zip(coh_vv_names, coh_vh_names):
                self.log.debug({'cvvn': cvvn, 'cvhn': cvhn})
                cvv = self.envi.load(cvvn)[0]
                cvh = self.envi.load(cvhn)[0]

                if mode == 'zone':
                    cvv = cvv[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]
                    cvh = cvh[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]

                bad_data = (cvv < 0) | (cvv > 1) | (cvh < 0) | (cvh > 1)
                cvh = np.clip(cvh, 0, 1)
                cv = np.clip(np.hypot(cvv, cvh), 0, 2)

                cvpol = None
                if 'coh_pol' in products:
                    cvpol = np.arcsin(cvh / cv)
                    fix_pixels(cvpol, bad_data)
                    cvpol = gaussian_filter(cvpol, params[2])
                    cvpol = anisotropic_diffusion(cvpol, params[3], params[4], 0.2, option=1)
                cvv = None
                cvh = None

                fix_pixels(cv, bad_data)
                cv = anisotropic_diffusion(cv, params[0], params[1], 0.2, option=1)

                if mode == 'zone':
                    if 'coh_hypot' in products:
                        tnsr_zone[..., product_index] = cv
                        product_index += 1
                    if 'coh_pol' in products:
                        tnsr_zone[..., product_index] = cvpol
                        product_index += 1
                    bd_zone |= bad_data
                elif mode == 'full':
                    if 'coh_hypot' in products:
                        tnsr_full[..., product_index] = cv
                        product_index += 1
                    if 'coh_pol' in products:
                        tnsr_full[..., product_index] = cvpol
                        product_index += 1
                    bd_full |= bad_data
                elif mode == 'both':
                    if 'coh_hypot' in products:
                        tnsr_full[..., product_index] = cv
                        tnsr_zone[..., product_index] = cv[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]
                        product_index += 1
                    if 'coh_pol' in products:
                        tnsr_full[..., product_index] = cvpol
                        tnsr_zone[..., product_index] = cvpol[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]
                        product_index += 1
                    bd_full |= bad_data
                    bd_zone |= bad_data[zone[0][0]:zone[1][0], zone[0][1]:zone[1][1]]

        if not os.path.exists(self.WORKDIR):
            os.makedirs(self.WORKDIR)
        self.log.debug("Saving tnsr and bd into %s", self.WORKDIR)
        if mode in ('zone', 'both'):
            np.save(self.WORKDIR + 'tnsr_zone.npy', tnsr_zone)
            np.save(self.WORKDIR + 'bd_zone.npy', bd_zone)
        if mode in ('full', 'both'):
            np.save(self.WORKDIR + 'tnsr_full.npy', tnsr_full)
            np.save(self.WORKDIR + 'bd_full.npy', bd_full)
        self.log.info('tensors processed')
        # system("say 'assembling complete'")
        return 0
