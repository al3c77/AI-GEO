#!/usr/bin/env python3.7
from ai.COS import COS
from ai.lib.map_envi_cos.Envi import Envi
from ai.visualize import Visualize
from command_line import cmd_options, check_recipe_exists
from logger import logger

cmd_options.add_argument('mode',
                         choices=('full', 'zone'),
                         help='zone|full')

args = cmd_options.parse_args()
check_recipe_exists(args.recipe)

cos = COS('/root/.bluemix/cos_credentials', args.recipe, logger)
envi = Envi('./recipe-test.json', cos.resource, logger)
viz = Visualize(args.mode, args.recipe, envi, logger)
viz.run()
