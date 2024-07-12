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
