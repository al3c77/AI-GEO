import argparse
import os
from argparse import ArgumentParser

cmd_options: ArgumentParser = argparse.ArgumentParser(description='Generating COG image.')

cmd_options.add_argument('--recipe',
                         type=str,
                         default=('./recipe.json'),
                         help='JSON recipe file with path, default is ./recipe.json')
def check_recipe_exists(fname):
    if not os.path.isfile(fname):
        print ("Error: Recipe file not found {} \n\n".format(fname))
        cmd_options.print_help()
        exit(-1)
