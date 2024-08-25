# Build stage
FROM node:16 as build-stage

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

ENV NODE_ENV development
RUN npm run build:dll

ARG APP_VERSION
ENV VUE_APP_VERSION=$APP_VERSION

RUN npm run build

# Production stage
FROM nginx:stable-alpine as production-stage
WORKDIR /app
COPY ./ /app/
COPY --from=build-stage /app/dist /usr/share/nginx/html
#COPY --from=build-stage /app/deploy/nginx /etc/nginx
#COPY --from=build-stage /app/deploy/entrypoint.sh /app/deploy/entrypoint.sh
RUN chmod -R u=rwX,go=rX ./
RUN chmod +x /app/deploy/entrypoint.sh
EXPOSE 80
EXPOSE 443
ENTRYPOINT ["/app/deploy/entrypoint.sh"]
