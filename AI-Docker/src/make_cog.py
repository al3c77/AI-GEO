#!/usr/bin/env python3.7
"""
Make COG tif file from Visualize output image
"""
import logging
import os

from ai.gdal_wrap import GDALWrap
from ai.recipe import Recipe
from command_line import cmd_options, check_recipe_exists
from logger import init as initlog  ## put it first to suppress warnings

initlog('INFO')
args = cmd_options.parse_args()
check_recipe_exists(args.recipe)
log = logging.getLogger('GDAL')
log.info('GDAL operations....')
recipe = Recipe(args.recipe)
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
