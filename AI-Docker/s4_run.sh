#!/usr/bin/env bash
 docker run --rm --name c4c_s4 -it \
     -v  c:/VLZ/Playground/C4CAI/src:/usr/src/app \
   -v  c:/VLZ/Playground/C4CAI/data:/data \
   -v  c:/VLZ/Playground/C4CAI/out:/out \
   -v  c:/VLZ/Playground/C4CAI/bluemix/cos_credentials:/root/.bluemix/cos_credentials:ro \
    registry.eu-de.bluemix.net/c4c-tiles/c4c_s4:1.0 $@