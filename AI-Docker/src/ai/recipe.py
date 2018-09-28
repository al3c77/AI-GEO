import json
import logging
import os


# TODO add JSON schema validation
class Recipe(dict):
    """Wrapper(Inherits from) around Dict object filled from recipe file
    """
    log = logging.getLogger("Recipe")

    def __init__(self, file):
        self.recipe_file = file
        self.recipe = json.load(open(file, 'r'))
        super(Recipe, self).__init__(self.recipe)  # make Dict from self
        self.log.info("Getting recipe from {}".format(self.recipe_file))

    def cos_creds_content(self):
        if not os.path.isfile(self._cos_creds_file()):
            self.log.critical("Invalid COS credits file")
            raise SystemExit(-1)
        return json.load(open(self._cos_creds_file(), 'r'))

    def _cos_creds_file(self):
        return self.recipe['COS'].get('credentials', '/root/.bluemix/cos_credentials')
