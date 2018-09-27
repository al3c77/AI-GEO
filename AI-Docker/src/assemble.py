#!/usr/bin/env python3.7
from ai.COS import COS
from ai.lib.map_envi_cos.Envi import Envi
from command_line import cmd_options, check_recipe_exists
from logger import logger
from ai.tensor import Assemble

cmd_options.add_argument('mode',
                         choices=('full', 'zone', 'both'),
                         help='Type of result')
args = cmd_options.parse_args()

check_recipe_exists(args.recipe)

cos = COS('/root/.bluemix/cos_credentials', args.recipe, logger)

envi = Envi(args.recipe, cos.resource, logger)
tensor = Assemble(args.mode, args.recipe, envi, logger)

tensor.run()
