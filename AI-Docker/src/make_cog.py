#!/usr/bin/env python3.7
import json
import os

from ai.gdal_wrap import GDALWrap
from command_line import cmd_options, check_recipe_exists
from logger import logger  ## put it first to suppress warnings

args = cmd_options.parse_args()
check_recipe_exists(args.recipe)
log = logger.getLogger('GDAL')
log.info('GDAL operations....')
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
