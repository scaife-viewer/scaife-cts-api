FROM gcr.io/scaife-viewer/nautilus-cnd:v1.2.0

RUN mkdir -p /usr/src/scaife-cts-api
WORKDIR /usr/src/scaife-cts-api
COPY requirements.txt /usr/src/scaife-cts-api
RUN set -ex \
        && pip install --no-cache-dir -r requirements.txt
COPY . /usr/src/scaife-cts-api
RUN set -ex \
        && apk add --no-cache --virtual .fetch-deps \
            curl \
            tar \
        && mkdir -p /var/lib/nautilus/data \
        && pip install -e . \
        && scaife-cts-api loadcorpus \
        && apk del .fetch-deps
