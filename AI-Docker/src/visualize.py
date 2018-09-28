#!/usr/bin/env python3.7
from ai.COS import COS
from ai.lib.Envi import Envi
from ai.recipe import Recipe
from ai.visualize import Visualize
from command_line import cmd_options, check_recipe_exists
from logger import init as initlog

initlog('DEBUG')

cmd_options.add_argument('mode',
                         choices=('full', 'zone'),
                         help='zone|full')

args = cmd_options.parse_args()
check_recipe_exists(args.recipe)
recipe = Recipe(args.recipe)

cos = COS(recipe)
envi = Envi(recipe, cos)
viz = Visualize(args.mode, recipe, envi)
viz.run()
