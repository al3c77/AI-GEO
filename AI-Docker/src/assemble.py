#!/usr/bin/env python3.7
import logger
from ai.COS import COS
from ai.assemble import Assemble
from ai.lib.Envi import Envi
from ai.recipe import Recipe
from command_line import cmd_options, check_recipe_exists

logger.init()

cmd_options.add_argument('mode',
                         choices=('full', 'zone', 'both'),
                         help='Type of result')
args = cmd_options.parse_args()

check_recipe_exists(args.recipe)

recipe = Recipe(args.recipe)
cos = COS(recipe)
envi = Envi(recipe, cos)

Assemble(args.mode, recipe, envi).run()
