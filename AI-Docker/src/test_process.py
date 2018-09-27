from ai.process import Process
from logger import logger  ## put it first to suppress warnings
processor = Process('full', 'predict', './recipe-local.json', logger)

processor.run()
