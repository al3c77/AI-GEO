FROM python:3.7.0-stretch

WORKDIR /usr/src/app

COPY src/requirements.txt /usr/src/app/requirements.txt

RUN cd /usr/src/app && pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get  install -y  gdal-bin  &&  apt-get clean &&\
     rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* &&\
    rm -rf /usr/share/doc/ && rm -rf /usr/share/man/ && rm -rf /usr/share/locale/

COPY src /usr/src/app

RUN mkdir -p /data && mkdir -p /out && cd /usr/src/app && chmod +x *.py

CMD [ "bash"]
