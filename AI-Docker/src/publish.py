#!/usr/bin/env python3.7
"""Upload COG tiff to COS by Recipe
if --upload-filename options is missed, will try to get filename from Recipe[ COS.ResultKey ] field

"""
import logging

from ai.COS import COS
from ai.recipe import Recipe
from command_line import cmd_options, check_recipe_exists
from logger import init as initlog

initlog('DEBUG')
log = logging.getLogger("Publish")
required = cmd_options.add_argument_group('required arguments')
required.add_argument('--upload-filename',
                      help='Cloud Object Sorage object Key(filename) ')
args = cmd_options.parse_args()
check_recipe_exists(args.recipe)

recipe = Recipe(args.recipe)
cog_file = recipe['OUTDIR'] + 'cog-out.tif'

cos_key = args.upload_filename
if not cos_key and "COS" in recipe:
    cos_key = recipe['COS'].get('ResultKey')

if not cos_key:
    log.critical("No COS key (upload file name)")
    exit(-1)

log.debug(recipe.get("ssss"))
log.info("uploading %s as %s", cog_file, cos_key)

cos = COS(recipe).publish(cog_file, args.upload_filename)
