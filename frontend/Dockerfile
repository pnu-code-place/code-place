ARG SERVER_NAME

# Build stage
FROM node:24.11.0 AS build-stage

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

ARG APP_VERSION
ARG SENTRY_ENVIRONMENT
ARG SENTRY_DSN
ARG USE_SENTRY
ENV VUE_APP_VERSION=$APP_VERSION
ENV SENTRY_ENVIRONMENT=$SENTRY_ENVIRONMENT
ENV SENTRY_DSN=$SENTRY_DSN
ENV USE_SENTRY=$USE_SENTRY

RUN npm run build:dll
RUN npm run build

# Production stage
FROM nginx:stable-alpine AS production-stage

ARG SERVER_NAME
ENV SERVER_NAME=$SERVER_NAME

WORKDIR /app
COPY ./ /app/
COPY --from=build-stage /app/dist /usr/share/nginx/html

RUN echo ${SERVER_NAME}
#COPY --from=build-stage /app/deploy/nginx /etc/nginx
#COPY --from=build-stage /app/deploy/entrypoint.sh /app/deploy/entrypoint.sh
RUN chmod -R u=rwX,go=rX ./
RUN chmod +x /app/deploy/entrypoint.sh
EXPOSE 80
EXPOSE 443
ENTRYPOINT ["/app/deploy/entrypoint.sh"]
