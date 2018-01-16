FROM gcr.io/scaife-viewer/nautilus-cnd:v1.1.1

COPY loaddata.py /usr/local/share/nautilus/
RUN set -ex \
        && apk add --no-cache --virtual .fetch-deps \
            curl \
            tar \
        && mkdir -p /var/lib/nautilus/data \
        && /usr/local/share/nautilus/loaddata.py \
        && apk del .fetch-deps
