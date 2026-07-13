"use strict"

function isSentryEnabled(nodeEnv = process.env.NODE_ENV) {
  const enabled = (process.env.USE_SENTRY || (nodeEnv === "production" ? "1" : "0")) === "1"
  return enabled && Boolean(getSentryDsn())
}

function getSentryDsn() {
  return process.env.SENTRY_DSN_FRONTEND || ""
}

function getSentryEnvironment(nodeEnv = process.env.NODE_ENV) {
  return process.env.SENTRY_ENVIRONMENT || nodeEnv || "development"
}

function isSentryUploadEnabled(nodeEnv = process.env.NODE_ENV) {
  return (
    isSentryEnabled(nodeEnv) &&
    Boolean(process.env.SENTRY_AUTH_TOKEN) &&
    Boolean(process.env.APP_VERSION || process.env.VUE_APP_VERSION)
  )
}

module.exports = {
  getSentryEnvironment,
  getSentryDsn,
  isSentryEnabled,
  isSentryUploadEnabled,
}
