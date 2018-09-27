#!/usr/bin/env python3.7
import json

from ai.COS import COS
from command_line import cmd_options, check_recipe_exists
from logger import logger

required = cmd_options.add_argument_group('required arguments')
required.add_argument('--upload-filename',
                      required=True,
                      help='Type of result')
args = cmd_options.parse_args()
print(args)
check_recipe_exists(args.recipe)
log = logger.getLogger('main')
recipe = json.load(open(args.recipe, 'r'))
WORKDIR = recipe['OUTDIR']
cog_file = WORKDIR + 'cog-out.tif'

cos = COS('/root/.bluemix/cos_credentials', args.recipe, logger)
cos.publish(cog_file, args.upload_filename)
