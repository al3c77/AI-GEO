#!/usr/bin/env python3.7
from logging import DEBUG

from ai.lib.map_envi_cos.Envi import Envi

from ai.COS import COS
from logger import logger

log = logger.getLogger('test')
log.setLevel(DEBUG)

cos = COS('./cos_credentials', './recipe-test.json', logger)

envi = Envi('./recipe-test.json', cos.resource, logger)

log.info("cache_cos satrt ")

file = 'Sigma0_IW2_VH_mst_06Aug2018'
summary = envi.object_etag(file + '.hdr')
log.info("cache_cos satrt %s", summary)
envi.read_header(file)
envi.load(file)
