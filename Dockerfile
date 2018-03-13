FROM gcr.io/scaife-viewer/nautilus-cnd:v1.2.0

WORKDIR /opt/scaife-cts-api/src/
RUN pip --no-cache-dir --disable-pip-version-check install pipenv
ENV PATH="/opt/scaife-cts-api/bin:${PATH}" VIRTUAL_ENV="/opt/scaife-cts-api"
COPY Pipfile Pipfile.lock ./
RUN set -ex \
    && apk --no-cache add --virtual .build-deps \
      build-base \
      libxml2-dev libxslt-dev \
    && virtualenv /opt/scaife-cts-api \
    && pipenv install --deploy \
    && apk del .build-deps
COPY . ./
RUN set -ex \
    && runDeps="$( \
      scanelf --needed --nobanner --format '%n#p' --recursive $(pipenv --venv) \
        | tr ',' '\n' \
        | sort -u \
        | awk 'system("[ -e /usr/local/lib/" $1 " ]") == 0 { next } { print "so:" $1 }' \
    )" \
    && apk --no-cache add $runDeps \
    && apk --no-cache add --virtual .fetch-deps \
      curl tar \
    && mkdir -p /var/lib/nautilus/data \
    && pipenv run pip --no-cache-dir --disable-pip-version-check install -e . \
    && scaife-cts-api loadcorpus \
    && apk del .fetch-deps
