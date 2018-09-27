#!/usr/bin/env bash
 docker run --rm --name c4c_s4 -it \
    -v  c:/VLZ/Playground/C4CAI/src:/usr/src/app \
    -v  c:/VLZ/Playground/C4CAI/data:/data \
    -v  c:/VLZ/Playground/C4CAI/bluemix/cos_credentials:/root/.bluemix/cos_credentials:rw \
    c4c_s4 bash
