#!/usr/bin/env python3.7
import json
from logging import DEBUG

from ai.COS import COS
from ai.lib.map_envi_cos.Envi import Envi
from logger import logger
import ibm_boto3
from ibm_botocore.client import Config

log = logger.getLogger('test')
log.setLevel(DEBUG)


cos = COS('./cos_credentials','./recipe-test.json',logger)



envi = Envi('./recipe-test.json', cos.resource, logger)

log.info("cache_cos satrt ")

file = 'Sigma0_IW2_VH_mst_06Aug2018'
summary = envi.object_etag(file + '.hdr')
log.info("cache_cos satrt %s", summary)
envi.read_header(file)
envi.load(file)
