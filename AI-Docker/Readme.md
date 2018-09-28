#Optoss Map AI

It performs full AI processing: 
- data whitening
- fitting
- predicting
- generating of CloudOptimizedGeo tiff file,
- uploading generated COG-tif to IBM _Cloud Storage_ and making uploaded file public-readable 

Docker image could be run either locally with local-volumes mounted for the best performance on big Data-sets 
or as a job in kubernetes IBM BlueMix cloud cluster

If the image is run locally, missed data-set files will be downloaded from IBM _Cloud Storage_ 
and cached locally

Cloud-based _Kepler-tiles viewer_ and _COG-tiles server_ could be used to visualize generated images.   
Docker files for these software images could be found in this repository in the `client` folder

Refer `s4_shell.sh` and `s4_run.sh` if running image locally

## Building image

```bash
 docker build -t c4c_s4  .
```

## Recipe file format (json)
```json
{
  "DATADIR": "/data/",
  "OUTDIR": "/out/",
  "COS": {
    "credentials": "../bluemix/cos_credentials",
    "endpoint": "https://s3.eu-de.objectstorage.softlayer.net",
    "bucket": "cog-1",
    "ResultKey":"cog-medium.tif"
  },
  "channels": {
    "sigma":     [      "Sigma0_IW2_VH_mst_06Aug2018"    ],
    "sigma_avg": [      "Sigma0_IW2_VH_mst_06Aug2018"    ],
    "sigmaVH":   [      "Sigma0_IW2_VH_mst_06Aug2018"    ],
    "sigmaVV":   [      "Sigma0_IW2_VV_mst_06Aug2018"    ],
    "coh":       [      "coh_IW2_VH_06Aug2018_18Aug2018_slv5_06Aug2018"    ],
    "coh_avg":   [      "coh_IW2_VH_06Aug2018_18Aug2018_slv5_06Aug2018"    ],
    "cohVH":     [      "coh_IW2_VH_06Aug2018_18Aug2018_slv5_06Aug2018"    ],
    "cohVV":     [      "coh_IW2_VV_06Aug2018_18Aug2018_slv6_06Aug2018"    ]
  },
  "zone": [    [      630,      580    ],
               [      4843,     3506   ]
          ],
  "products": {
    "sigma":     [      15,      2.0    ],
    "coh":       [      20,      4.0    ],
    "sigma_avg": [      15,      2.0    ]
  },
  "learn_channels": [    0,    1,    2  ],
  "learn_gauss": 3,
  "predict_gauss": 0
}
```
where 
- `DATADIR` for input *.img and *.hdr files
- `OUTDIR` for input *.img and *.hdr files
- `COS` Cloud Object Storage to be used 
#### COS object
- `credentials` file with content of IBM bluemix credentials JSON string, default to  `/root/.bluemix/cos_credentials`
- `endpoint` and `backet` IBM Object Storage URL and Bucket 
- `ResultKey` key to be used when result published to IBM Object Sotage
 
> use private COS endpoint if image runs inside IBM cloud

## Running

app uses 2 directories (mount-points) from recipe file:
- `DATADIR` for input *.img and *.hdr files
- `OUTDIR`  for saving intermediate results and produced images
> mount local volumes to mount-points from recipe file

#### Cloud Object Storage
- if file not exists in `{DATADIR}` app will download it form COS storage
- if downloading failed app will exit with error
 

## supported commands :
### full processing
performs full AI processing: data whitening, fitting, predicting, generation of CloudOptimizedGoe tiff file,
uploading it to IBM Cloud Storage and making uploaded file public-readable 
```bash
C4CAI$ docker run  c4c_s4  ./all.py --help
usage: all.py [-h] [--recipe RECIPE] [--upload-filename UPLOAD_FILENAME]

Generating COG image.

optional arguments:
  -h, --help            show this help message and exit
  --recipe RECIPE       JSON recipe file with path, default is ./recipe.json
  --upload-filename UPLOAD_FILENAME
                        Type of result
```

### step-by-step
##### assemble tensors

```bash
C4CAI$ docker run  c4c_s4  ./assemble.py --help
usage: assemble.py [-h] --recipe [RECIPE] --mode [type]

Generating COG image.

optional arguments:
  -h, --help         show this help message and exit
  --recipe [RECIPE]  JSON recipe file with path
  --mode [type]      zone|full|both
```

##### Learning processing

```bash
C4CAI$ docker run  c4c_s4  ./process.py --help
usage: process.py [-h] [--recipe RECIPE] {full,zone} {fit,fitpredict,predict}

Generating COG image.

positional arguments:
  {full,zone}           Type of result
  {fit,fitpredict,predict}
                        Learning type

optional arguments:
  -h, --help            show this help message and exit
  --recipe RECIPE       JSON recipe file with path, default is ./recipe.json
```

##### Visualizing
 
 ```bash
C4CAI$ docker run  c4c_s4  ./visualize.py --help
usage: visualize.py [-h] [--recipe RECIPE] {full,zone}

Generating COG image.

positional arguments:
  {full,zone}      zone|full

optional arguments:
  -h, --help       show this help message and exit
  --recipe RECIPE  JSON recipe file with path, default is ./recipe.json
 ```
 
 
##### COG image generation
 it takes `{OUTDIR}/pred8c.img` and produces `{OUTDIR}/out.tif` and COG `{OUTDIR}/cog-out.tif`
 ```bash
C4CAI$ docker run  c4c_s4  ./make_cog.py --help
usage: make_cog.py [-h] [--recipe RECIPE]

Generating COG image.

optional arguments:
  -h, --help       show this help message and exit
  --recipe RECIPE  JSON recipe file with path, default is ./recipe.json
 ```

##### Upload image to COS
```bash
C4CAI$ docker run  c4c_s4  ./publish.py  --help                                     
usage: publish.py [-h] [--recipe RECIPE] --upload-filename UPLOAD_FILENAME               
                                                                                         
Generating COG image.                                                                    
                                                                                         
optional arguments:                                                                      
  -h, --help            show this help message and exit                                  
  --recipe RECIPE       JSON recipe file with path, default is ./recipe.json             
                                                                                         
required arguments:                                                                      
  --upload-filename UPLOAD_FILENAME                                                      
``` 
 