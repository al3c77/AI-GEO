#!/usr/bin/env python3.7
import json
import os

from ai.COS import COS
from ai.gdal_wrap import GDALWrap
from ai.lib.map_envi_cos.Envi import Envi
from ai.process import Process
from ai.visualize import Visualize
from logger import logger
from ai.tensor import Assemble
from command_line import cmd_options, check_recipe_exists

log = logger.getLogger('main')

cmd_options.add_argument('mode',
                         choices=('full', 'zone'),
                         help='Type of result')
cmd_options.add_argument('type',
                         choices=('fit', 'fitpredict', 'predict'),
                         help='Learning type')

required = cmd_options.add_argument_group('required arguments')
required.add_argument('--upload-filename',
                      required=True,
                      help='Type of result')

args = cmd_options.parse_args()
check_recipe_exists(args.recipe)

cos = COS('/root/.bluemix/cos_credentials', args.recipe, logger)
envi = Envi('./recipe-test.json', cos, logger)

tensor = Assemble(args.mode, args.recipe, envi, logger)
if tensor.run() != 0:
    log.error('Tensor assemble failed')
    exit(-1)


log.info("Learning...")
processor = Process('zone', 'fit', args.recipe, logger)
if processor.run() != 0:
    log.error('Processing failed')
    exit(-1)

log.info("Prediction...")
processor = Process('full', 'predict', args.recipe, logger)
if processor.run() != 0:
    log.error('Processing failed')
    exit(-1)

viz = Visualize(args.mode, args.recipe, envi, logger)
if viz.run() != 0:
    log.error('visualization failed')
    exit(-1)

recipe = json.load(open(args.recipe, 'r'))
WORKDIR = recipe['OUTDIR']
file = WORKDIR + 'pred8c.img'
out_file = WORKDIR + 'out.tif'
cog_file = WORKDIR + 'cog-out.tif'
if not os.path.isfile(file):
    log.critical("File doen not exists! %s", file)
    raise SystemExit(1)

w = GDALWrap(file, out_file, cog_file,logger)
try:
    w.gdaltranslate()
    w.gdalwarp()
    w.gdaladdo()
except RuntimeError as e:
    log.critical("COG-tiff generation failed %s",e)

###publish
cos.publish(cog_file, args.upload_filename)
