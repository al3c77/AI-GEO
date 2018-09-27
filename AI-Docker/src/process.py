#!/usr/bin/env python3.7
from ai.process import Process
from command_line import cmd_options, check_recipe_exists
from logger import logger  ## put it first to suppress warnings

cmd_options.add_argument('mode',
                         choices=('full', 'zone'),
                         help='Type of result')
cmd_options.add_argument('type',
                         choices=('fit', 'fitpredict', 'predict'),
                         help='Learning type')

args = cmd_options.parse_args()
check_recipe_exists(args.recipe)

processor = Process(args.mode, args.type, args.recipe, logger)

processor.run()
