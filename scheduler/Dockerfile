FROM alpine:latest
WORKDIR /app

FROM python:3.11-alpine

ENV OJ_ENV production
ARG TARGETARCH
ARG TARGETVARIANT

WORKDIR /app

COPY ./deploy/requirements.txt /app/deploy/

# psycog2 의존 모듈 libpq-dev 설치
RUN apk add gcc libc-dev python3-dev libpq-dev

# Django 의존성 설치
RUN pip install -r /app/deploy/requirements.txt

COPY ./ /app/

RUN chmod +x /app/deploy/exec_gunicorn.sh

EXPOSE 8090
ENTRYPOINT ["/app/deploy/exec_gunicorn.sh"]