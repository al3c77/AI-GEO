#!/usr/bin/env python3.7
import json
import logging
import os

from ai.lib.Envi import Envi
from ai.assemble import Assemble

from ai.COS import COS
from ai.gdal_wrap import GDALWrap
from ai.process import Process
from ai.recipe import Recipe
from ai.visualize import Visualize
from command_line import cmd_options, check_recipe_exists
from logger import init as initlog
initlog('DEBUG')

log = logging.getLogger('main')

# cmd_options.add_argument('mode',
#                          choices=('full', 'zone'),
#                          help='Type of result')
# cmd_options.add_argument('type',
#                          choices=('fit', 'fitpredict', 'predict'),
#                          help='Learning type')

cmd_options.add_argument('--upload-filename',
                      help='Type of result')

args = cmd_options.parse_args()
check_recipe_exists(args.recipe)
recipe = Recipe(args.recipe)

cos = COS(recipe)
envi = Envi(recipe, cos)


if Assemble('both', recipe, envi).run() != 0:
    log.error('Tensor assemble failed')
    exit(-1)

log.info("Learning...")
processor = Process('zone', 'fit', recipe)
if processor.run() != 0:
    log.error('Processing failed')
    exit(-1)

log.info("Prediction...")
processor = Process('full', 'predict',  recipe)
if processor.run() != 0:
    log.error('Processing failed')
    exit(-1)

viz = Visualize('full', recipe, envi)
if viz.run() != 0:
    log.error('visualization failed')
    exit(-1)


WORKDIR = recipe['OUTDIR']
file = WORKDIR + 'pred8c.img'
out_file = WORKDIR + 'out.tif'
cog_file = WORKDIR + 'cog-out.tif'
if not os.path.isfile(file):
    log.critical("File doen not exists! %s", file)
    raise SystemExit(1)

w = GDALWrap(recipe,file, out_file, cog_file)
try:
    w.make_gep_json()
    w.gdaltranslate()
    w.gdalwarp()
    w.gdaladdo()

except RuntimeError as e:
    log.critical("COG-tiff generation failed %s", e)

###publish
cos_key = args.upload_filename
if not cos_key and "COS" in recipe:
    cos_key = recipe['COS'].get('ResultKey')

if not cos_key:
    log.critical("No COS key (upload file name)")
    exit(-1)

log.info("uploading %s as %s", cog_file, cos_key)
cos.publish(cog_file, cos_key)
if os.path.isfile(cog_file + '.geojson'):
    cos.publish(cog_file + '.geojson', cos_key + '.geojson')
