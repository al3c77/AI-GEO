#!/usr/bin/env python3.7
import logging
import os
import time
from glob import glob

import numpy as np
# from botocore.exceptions import CredentialRetrievalError
from cachetools.func import ttl_cache
from ibm_botocore.exceptions import ClientError, CredentialRetrievalError

from ai.COS import COS
from ai.recipe import Recipe

datatypeDict = {1: np.uint8, 2: np.int16, 3: np.int32, 4: np.float32, 5: np.float64, 6: np.complex64, 9: np.complex128,
                12: np.uint16, 13: np.uint32, 14: np.int64, 15: np.uint64}
datatypeDictInv = {np.dtype(v).name: k for k, v in datatypeDict.items()}


class Envi(object):
    """AI file operations (downloads missed files from  COS)"""
    log = logging.getLogger('Envi-COS')

    def __init__(self, recipe: Recipe, cos: COS):
        self.cos = cos
        self.recipe = recipe
        self.DATADIR = self.recipe.get("DATADIR")

    @ttl_cache(maxsize=128, ttl=600, timer=time.time, typed=False)
    def object_etag(self, file):
        if self.cos.resource is None:
            self.log.warning("COS is not valid")
            return None
        object_summary = self.cos.resource.ObjectSummary(self.cos.bucket, file)
        try:
            # fetch data
            return object_summary.e_tag
        except (ClientError, CredentialRetrievalError) as e:
            self.log.critical(e)
            return None

    def cache_cos(self, file:str, dir:str):
        full_name = dir + file

        if os.path.isfile(full_name):
            self.log.info("File %s found in %s", file, dir)
            return full_name
        # todo - cache etags, download if needed
        if not self.cos:
            self.log.error("File does not exists : %s", full_name)
            return False
        if self.object_etag(file) is None:
            self.log.error("File does not exists in COS %s", file)
            return False
        try:
            start_time = time.time()
            self.log.info('Starting download %s into %s', file, full_name)
            self.cos.resource.Bucket(self.cos.bucket).download_file(file, full_name)
            self.log.info('Done download %s in %s seconds', file, time.time() - start_time)
        except (ClientError, CredentialRetrievalError) as e:
            self.log.critical(e)
            return False
        return dir + file

    def load(self, l_path:str):
        file_hdr = self.cache_cos(l_path + '.hdr', self.DATADIR)

        if not file_hdr:
            self.log.error('Could not load %s', file_hdr)
            exit(-1)
        header = open(file_hdr, 'r')
        hdict = dict([tuple(val[:-1].split(' = ')) for val in header.readlines()[1:] if len(val) > 1])

        if int(hdict['bands']) == 1:
            imshape = (int(hdict['lines']), int(hdict['samples']))
        else:
            print('Multibands not implemented')
            exit(-1)

        datatype = datatypeDict[int(hdict['data type'])]
        load_datatype = datatype
        if int(hdict['byte order']):
            load_datatype = np.dtype(datatype).newbyteorder('>')
        file_img = self.cache_cos(l_path + '.img', self.DATADIR)
        if not file_img:
            self.log.error('Could not load %s', file_img)
            exit(-1)
        arr = np.fromfile(file_img, load_datatype).astype(datatype)
        arr = arr.reshape(imshape)
        np.nan_to_num(arr, copy=False)
        return arr, hdict

    def read_header(self, l_path):
        file_hdr = self.cache_cos(l_path + '.hdr', self.DATADIR)

        if not file_hdr:
            self.log.error('Could not load %s', l_path)
            raise SystemExit(1)
        header = open(file_hdr, 'r')
        hdict = dict([tuple(val[:-1].split(' = ')) for val in header.readlines()[1:] if len(val) > 1])

        if int(hdict['bands']) == 1:
            imshape = (int(hdict['lines']), int(hdict['samples']))
        else:
            print('Multibands not implemented')
            exit(-1)

        return imshape, hdict

    def save(self, l_path, arr, map_info, coord_string, chnames='my_ch_name', desc='my description', interleave='bip'):
        path = l_path
        nbands = 0
        if len(arr.shape) == 2:
            nbands = 1
            ch_shape = arr.shape
        elif len(arr.shape) == 3:
            if interleave == 'bip':
                nbands = arr.shape[2]
                ch_shape = arr.shape[:2]
            elif interleave == 'bsq':
                nbands = arr.shape[0]
                ch_shape = arr.shape[1:]
            else:
                print('Not Implemented')
                exit(-1)
        else:
            print('Wrong arr shape')
            exit(-1)

        hdr = open(path + '.hdr', 'w')
        hdr.write('ENVI\n')
        hdr.write('description = ' + desc + '\n')
        hdr.write('samples = ' + str(ch_shape[1]) + '\n')
        hdr.write('lines = ' + str(ch_shape[0]) + '\n')
        hdr.write('bands = ' + str(nbands) + '\n')
        hdr.write('header offset = 0\n')
        hdr.write('file type = ENVI Standard\n')
        hdr.write('data type = ' + str(datatypeDictInv[arr.dtype.name]) + '\n')
        hdr.write('interleave = ' + interleave + '\n')
        hdr.write('byte order = 0\n')

        if isinstance(chnames, str):
            hdr.write('band names = { ' + chnames + ' }\n')
        elif isinstance(chnames, list):
            hdr.write('band names = { ' + ', '.join(chnames) + ' }\n')
        else:
            print('Wrong chnames format')
            exit(-1)

        hdr.write('map info = ' + map_info + '\n')
        hdr.write('coordinate system string = ' + coord_string + '\n')
        hdr.close()

        arr.tofile(path + '.img')

    def locate(self, l_path='./'):
        return [os.path.split(os.path.splitext(el)[0])[1] for el in glob(l_path + '*.hdr')]
