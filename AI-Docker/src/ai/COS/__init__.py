import logging
import time

import ibm_boto3
from ibm_botocore.config import Config
from ibm_botocore.exceptions import ClientError


class COS(object):
    """Interface to BlueMix Object Storage
    gets params from Recipe:
      {
        "COS": {
            "credentials": "../bluemix/cos_credentials",
            "endpoint": "https://s3.eu-de.objectstorage.softlayer.net",
            "bucket": "cog-1"
        }
      }
    """
    log = logging.getLogger('COS')

    # log = None  # type: Logger

    def __init__(self, recipe):
        """

        :type recipe: Recipe
        """

        # self.log.setLevel(DEBUG)
        self.log.info("Connection to COS")
        cos_creds = recipe.cos_creds_content()
        api_key = cos_creds['apikey']
        auth_endpoint = 'https://iam.bluemix.net/oidc/token'
        service_instance_id = cos_creds['resource_instance_id']
        service_endpoint = recipe["COS"]["endpoint"]
        # service_endpoint = "s3.eu-de.objectstorage.service.networklayer.com"
        self.bucket = recipe["COS"]["bucket"]
        self.log.info("service endpoint '%s'", service_endpoint)
        self.log.info("service bucket '%s'", self.bucket)
        try:
            self.resource = ibm_boto3.resource(
                's3',
                ibm_api_key_id=api_key,
                ibm_service_instance_id=service_instance_id,
                ibm_auth_endpoint=auth_endpoint,
                config=Config(signature_version='oauth'),
                endpoint_url=service_endpoint
            )
        except ClientError as e:
            self.log.fatal('Exception: %s', e)
            raise SystemExit(-1)

    def publish(self, file, item_name):
        """        upload <file> to COS into bucket from Recipe
         as <item_name>(key) and make it public-read

        :param file: str
        :param item_name: str
        :return: None
        """
        # self.resource.Bucket(self.bucket).put_object(Key="sss.txt",Body=b'sss')
        # self.log.info('sss')
        start = time.time()
        res = self.resource.Bucket(self.bucket).upload_file(file, item_name, ExtraArgs={'ACL': 'public-read'})
        self.log.info("file '%s uploaded to COS as %s in %s sec", file, item_name, time.time() - start)
