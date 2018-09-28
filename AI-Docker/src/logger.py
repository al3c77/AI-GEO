import logging
import warnings

warnings.simplefilter(action='ignore')
import coloredlogs as coloredlogs


def init(level='DEBUG'):
    coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 'green'}, 'hostname': {'color': 'magenta'},
                                        'levelname': {'color': 'white', 'bold': True}, 'name': {'color': 'blue'},
                                        'programname': {'color': 'cyan'}}
    FORMAT = '%(asctime)s.%(msecs)03d  %(levelname)-5s %(name)-10s %(relativeCreated)-10d : %(message)s| %(filename)s:%(lineno)d'
    # logging.basicConfig(format=FORMAT,level=logging.getLevelName(level))
    coloredlogs.install(fmt=FORMAT, level=level)
    # warnings.simplefilter(action='ignore', category=FutureWarning)
    logging.getLogger('matplotlib').setLevel(logging.INFO)
    logging.getLogger('ibm_s3transfer').setLevel(logging.INFO)
    logging.getLogger('ibm_botocore').setLevel(logging.INFO)
    # logging.getLogger('ibm_s3transfer.utils').setLevel(logging.INFO)
    # logging.getLogger('ibm_s3transfer.tasks').setLevel(logging.INFO)
    # logging.getLogger('ibm_s3transfer.futures').setLevel(logging.INFO)


def getLogger(category):
    return logging.getLogger(category)
