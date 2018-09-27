import logging
import warnings

import sys

warnings.simplefilter(action='ignore')
import coloredlogs as coloredlogs


FORMAT = '%(asctime)-15s  %(levelname)-5s %(name)-10s %(relativeCreated)-10d : %(message)s| %(filename)s:%(lineno)d'
coloredlogs.install(fmt=FORMAT, level='DEBUG')
# warnings.simplefilter(action='ignore', category=FutureWarning)
# logging.basicConfig(format=FORMAT)
logging.getLogger('ibm_s3transfer').setLevel(logging.INFO)
logging.getLogger('ibm_botocore').setLevel(logging.INFO)
# logging.getLogger('ibm_s3transfer.utils').setLevel(logging.INFO)
# logging.getLogger('ibm_s3transfer.tasks').setLevel(logging.INFO)
# logging.getLogger('ibm_s3transfer.futures').setLevel(logging.INFO)
#
logger = logging
