FROM node:16-alpine

RUN apk add --no-cache nginx git python3 build-base

VOLUME [ "/CSEP_FE", "/var/log/nginx/", "/data/avatar"]
EXPOSE 80

CMD ["/bin/sh", "/CSEP_FE/deploy/run.sh"]
