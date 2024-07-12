FROM alpine:latest
WORKDIR /app

FROM python:3.11-alpine

ENV OJ_ENV production
ARG TARGETARCH
ARG TARGETVARIANT

WORKDIR /app

# Chromedriver 설치
RUN apk update
RUN apk add chromium chromium-chromedriver
ENV CHROME_BIN=/usr/bin/chromedriver \
    CHROMEDRIVER_PATH=/usr/lib/chromium/

# Selenium 캐시 폴더 생성 및 권한 설정
RUN mkdir -p /root/.cache/selenium && chmod 777 /root/.cache/selenium

COPY ./deploy/requirements.txt /app/deploy/

# psycog2 의존 모듈 libpq-dev 설치
RUN apk add gcc libc-dev python3-dev libpq-dev

# Django 의존성 설치
RUN pip install -r /app/deploy/requirements.txt

COPY ./ /app/

RUN chmod +x /app/deploy/exec_gunicorn.sh

EXPOSE 8090
ENTRYPOINT ["/app/deploy/exec_gunicorn.sh"]