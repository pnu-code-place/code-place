ARG SERVER_NAME

# Build stage
FROM node:24.11.0 AS build-stage

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

ARG APP_VERSION
ARG SENTRY_ENVIRONMENT
ARG SENTRY_DSN_FRONTEND
ARG USE_SENTRY
ARG SENTRY_ORG=onlinejudge
ARG SENTRY_PROJECT=onlinejudgefe
ENV APP_VERSION=$APP_VERSION
ENV VUE_APP_VERSION=$APP_VERSION
ENV SENTRY_ENVIRONMENT=$SENTRY_ENVIRONMENT
ENV SENTRY_DSN_FRONTEND=$SENTRY_DSN_FRONTEND
ENV USE_SENTRY=$USE_SENTRY
ENV SENTRY_ORG=$SENTRY_ORG
ENV SENTRY_PROJECT=$SENTRY_PROJECT

RUN npm run build:dll
RUN --mount=type=secret,id=sentry_auth_token,required=false <<'EOF'
set -eu
SENTRY_AUTH_TOKEN="$(cat /run/secrets/sentry_auth_token 2>/dev/null || true)"
if [ "${USE_SENTRY:-0}" = "1" ] && [ -z "$SENTRY_AUTH_TOKEN" ]; then
  echo "SENTRY_AUTH_TOKEN is required when USE_SENTRY=1" >&2
  exit 1
fi
export SENTRY_AUTH_TOKEN
npm run build
EOF

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
