import json
import os
from logging import DEBUG, INFO, ERROR

import ibm_boto3
import time
from ibm_botocore.config import Config
from ibm_botocore.exceptions import ClientError


class COS(object):
    def __init__(self, creds, recipe, logger):
        self.log = logger.getLogger('COS')
        self.log.setLevel(DEBUG)
        if not os.path.isfile(creds):
            self.log.critical("Invalid COS credits file")
            raise SystemExit(-1)
        self.log.info("Connection to COS")
        cos_creds = json.load(open(creds, 'r'))
        recipe = json.load(open(recipe, 'r'))
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
            self.cos_cli = ibm_boto3.client("s3",
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
        # self.resource.Bucket(self.bucket).put_object(Key="sss.txt",Body=b'sss')
        # self.log.info('sss')
        start = time.time()
        res = self.resource.Bucket(self.bucket).upload_file(file,item_name,ExtraArgs={'ACL':'public-read'})
        self.log.info("file '%s uploaded to COS as %s in %s sec",file,item_name,time.time()-start)


