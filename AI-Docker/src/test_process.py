import json

from ai.lib.map_envi_cos.Envi import Envi

from ai.COS import COS
from ai.process import Process
from logger import logger  ## put it first to suppress warnings

log = logger.getLogger()

recipe_file = './recipe-local.json'
recipe = json.load(open(recipe_file, 'r'))
WORKDIR = recipe.get("OUTDIR")

cos = COS('../bluemix/cos_credentials', recipe_file, logger)
envi = Envi('./recipe-test.json', cos, logger)

# # Assemble('full', recipe_file, envi, logger).run()
# # Assemble('zone', recipe_file, envi, logger).run()
# Assemble('both', recipe_file, envi, logger).run()
#
# tnsr_f = np.load(WORKDIR + 'tnsr_full.npy')
# tnsr_z = np.load(WORKDIR + 'tnsr_zone.npy')
# bad_data_f = np.load(WORKDIR + 'bd_full.npy')
# bad_data_z = np.load(WORKDIR + 'bd_zone.npy')

Process('full', 'fit', recipe_file, logger).run()
proc = Process('full', 'predict', recipe_file, logger).run()

log.info('done')
