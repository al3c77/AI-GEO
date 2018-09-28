#!/usr/bin/env bash
 docker run --rm --name c4c_s4 -it \
    -v  c:/VLZ/Playground/C4CAI/src:/usr/src/app \
    -v  c:/VLZ/Playground/C4CAI/bluemix:/usr/src/bluemix \
    -v  c:/VLZ/Playground/C4CAI/test-data:/usr/src/test-data \
    c4c_s4 bash
