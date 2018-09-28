import json
import logging
import os
import subprocess

import time

geojson_tempalte = json.loads(  # language=JSON
    """
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "COGURL": "http://159.122.178.150:30458/tiles/{z}/{x}/{y}@2x?url=https://s3.eu-de.objectstorage.softlayer.net/cog-1/cog-33-out.tif"
      },
      "geometry": {      }
    }
  ]
  }
""")


# TODO better error handling via raise, no Sysexit
class GDALWrap(object):
    """         GDAL transformation for visulize output file
    """
    log = logging.getLogger('GADLwrap')

    def __init__(self, recipe, input_file, out_file, cog_file):
        """         GDAL transformation for visulize output file

        :type recipe: Recipe
        :type cog_file: str
        :type input_file: str
        :type out_file: str
        """
        self.cog_file = cog_file
        self.out_file = out_file
        self.input_file = input_file
        self.recipe = recipe

    def make_gep_json(self):
        try:
            if "COS" not in self.recipe or "GEOJSON" not in self.recipe or "ResultKey" not in self.recipe["COS"]:
                self.log.warning("recipe not configured for Geo-json generation")
                return
            str = json.loads(self._get_gdalinfo())
            """ wgs84Extent has wrong coordinates order (Batterfly like but we wants square )
            so use cornerCoordinates og GDALinfo
            """
            coords = str["cornerCoordinates"]
            geojson = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "COGURL": (self.recipe["GEOJSON"]["COGURL"])
                        },
                        "geometry": {
                            "type": "Polygon",
                            'coordinates': [
                                [
                                    coords["upperLeft"], coords["upperRight"], coords["lowerRight"],
                                    coords["lowerLeft"],
                                    coords["upperLeft"]
                                ]
                            ]
                        }
                    }
                ]
            }
            json.dump(geojson, open(self.cog_file + '.geojson', 'w'))
            self.log.info("generated file info %s", self.cog_file + '.geojson')
        except BaseException as e:
            self.log.warning("cold not save geojson")
            self.log.exception("cold not save geojson")

    def _get_gdalinfo(self):
        """
            gdalinfo -json
            :rtype: str
        """
        self.log.info('getting info...')
        start = time.time()
        result = subprocess.run(['/usr/bin/gdalinfo',
                                 '-json',
                                 self.input_file,
                                 ],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                                )
        if result.returncode:
            self.log.error(result.stderr.decode('utf-8'))
            self.log.error("gdal_translate exited with code %s", result.returncode)
            raise RuntimeError("gdalwarp")
        self.log.info('gdalinfo done in %s', time.time() - start)
        return result.stdout.decode('utf-8')

    def gdaltranslate(self) -> None:
        """ gdal_translate  wrapper        """
        self.log.info('gdaltranslate...')
        start = time.time()
        """
        gdal_translate /data/out/pred8c.img /data/out/out.tif -co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW
        """
        result = subprocess.run(['/usr/bin/gdal_translate',
                                 self.input_file,
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
        self.log.info('gdaltranslate done in %s', time.time() - start)

    def gdalwarp(self) -> None:
        """        gdalwarp  wrapper       """

        self.log.info('gdalwarp...')
        start = time.time()
        """
         gdalwarp /data/out/out.tif /cog-out.tif -t_srs EPSG:3857
        """
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
        self.log.info('gdalwarp done in %s', time.time() - start)

    def gdaladdo(self) -> None:
        """ gdaladdo  wrapper """
        self.log.info('gdaladdo')
        start = time.time()
        """
        gdaladdo -r average ~/cog-out.tif 2 4 8 16 32
        """
        result = subprocess.run(['/usr/bin/gdaladdo',
                                 '-r', 'average',
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
        self.log.info('gdaladdo done in %s', time.time() - start)
