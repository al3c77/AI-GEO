import subprocess

import time


#TODO better error handling via raise, no Sysexit
class GDALWrap(object):
    def __init__(self,input_file,out_file,cog_file,logger):
        self.cog_file = cog_file
        self.out_file = out_file
        self.log=logger.getLogger('GADLwrap')
        self.file = input_file
    def    gdaltranslate(self):
        self.log.info('gdaltranslate...')
        start  =time.time()
        # gdal_translate /data/out/pred8c.img /data/out/out.tif -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW
        result = subprocess.run(['/usr/bin/gdal_translate',
                                 self.file,
                                 self.out_file,
                                 '-co', 'TILED=YES',
                                 '-co', 'COPY_SRC_OVERVIEWS=YES',
                                 '-co', 'COMPRESS=LZW'
                                 ],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                                )
        if result.returncode:
            self.log.error(result.stderr.decode('utf-8'))
            self.log.error("gdal_translate exited with code %s", result.returncode)
            raise RuntimeError("gdalwarp")
        self.log.debug(result.stdout.decode('utf-8'))
        self.log.info('gdaltranslate done in %s',time.time()-start)
    def gdalwarp(self):
        self.log.info('gdalwarp...')
        start  =time.time()
        # gdalwarp /data/out/out.tif /cog-out.tif -t_srs EPSG:3857
        result = subprocess.run(['/usr/bin/gdalwarp',
                                 self.out_file,
                                 self.cog_file,
                                 '-t_srs', 'EPSG:3857'
                                 ],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                                )
        if result.returncode:
            self.log.error(result.stderr.decode('utf-8'))
            self.log.error("gdalwarp exited with code %s", result.returncode)
            raise RuntimeError("gdalwarp")
        self.log.debug(result.stdout.decode('utf-8'))
        self.log.info('gdalwarp done in %s',time.time()-start)
    def gdaladdo(self):
        self.log.info('gdaladdo')
        start  =time.time()
        # gdaladdo -r average ~/cog-out.tif 2 4 8 16 32
        result = subprocess.run(['/usr/bin/gdaladdo',
                                 '-r','average',
                                 self.cog_file,
                                 '2', '4', '8', '16', '32'
                                 ],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                                )
        if result.returncode:
            self.log.error(result.stderr.decode('utf-8'))
            self.log.error("gdaladdo exited with code %s", result.returncode)
            raise RuntimeError("gdalwarp")
        self.log.debug(result.stdout.decode('utf-8'))
        self.log.info('gdaladdo done in %s',time.time()-start)