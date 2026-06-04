FROM python:3.11-alpine
ARG TARGETARCH
ARG TARGETVARIANT

ENV OJ_ENV production
WORKDIR /app

COPY ./deploy/requirements.txt /app/deploy/
# psycopg2: libpg-dev
# pillow: libjpeg-turbo-dev zlib-dev freetype-dev
RUN --mount=type=cache,target=/etc/apk/cache,id=apk-cahce-$TARGETARCH$TARGETVARIANT-final \
    --mount=type=cache,target=/root/.cache/pip,id=pip-cahce-$TARGETARCH$TARGETVARIANT-final \
    <<EOS
set -ex
apk add gcc libc-dev python3-dev libpq libpq-dev libjpeg-turbo libjpeg-turbo-dev zlib zlib-dev freetype freetype-dev curl unzip
pip install -r /app/deploy/requirements.txt
apk del gcc libc-dev python3-dev libpq-dev libjpeg-turbo-dev zlib-dev freetype-dev
EOS

COPY ./ /app/
RUN chmod -R u=rwX,go=rX ./ && chmod +x ./deploy/entrypoint.sh ./deploy/entrypoint_beat.sh ./deploy/entrypoint_worker.sh

HEALTHCHECK --interval=5s CMD [ "curl", "-fsS", "http://localhost:8080/api/health" ]
EXPOSE 8080
