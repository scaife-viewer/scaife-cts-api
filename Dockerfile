FROM gcr.io/scaife-viewer/nautilus-cnd:v1.2.0

COPY loaddata.py corpus.json /usr/local/share/nautilus/
RUN set -ex \
        && apk add --no-cache --virtual .fetch-deps \
            curl \
            tar \
        && mkdir -p /var/lib/nautilus/data \
        && /usr/local/share/nautilus/loaddata.py \
        && apk del .fetch-deps
